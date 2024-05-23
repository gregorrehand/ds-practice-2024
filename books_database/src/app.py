import sys
import os
import logging
import redis
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

# Service name is required for most backends
resource = Resource(attributes={
    SERVICE_NAME: "Books database"
})

traceProvider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(
    OTLPSpanExporter(endpoint="http://observability:4318/v1/traces")
)
traceProvider.add_span_processor(processor)
trace.set_tracer_provider(traceProvider)
tracer = trace.get_tracer("orchestrator")

reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint="http://observability:4318/v1/metrics"),
    export_interval_millis=10000,
)
meterProvider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(meterProvider)

# Creates a meter from the global meter provider
meter = metrics.get_meter("database_metrics")
book_counter = meter.create_gauge("book.counter", unit="1")
book_counter.set(0)

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")

utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/books_database'))
sys.path.insert(0, utils_path)
import books_database_pb2 as books_database
import books_database_pb2_grpc as books_database_grpc

import grpc
from concurrent import futures

logging.getLogger().setLevel(logging.DEBUG)  # set logging level so stuff shows up


class BooksDatabaseService():
    def __init__(self):
        self.books = {"JavaScript - The Good Parts": 50, "Learning Python": 4}
        book_counter.set(sum(self.books.values()))
        self.redisClient = redis.Redis(host='redis', port=6379, db=0)
        self.service_address = f"{os.getenv('SERVICE_ID')}:{os.getenv('PORT')}"
        self.list_of_replicas = os.getenv('LIST_OF_REPLICAS').split(',')

    def GetStock(self, request, context):
        logging.log(logging.DEBUG, f"Received GetStock request title: {request.title}")
        response = books_database.StockResponse()
        response.title = request.title
        response.quantity = self.books[request.title] if request.title in self.books else 0
        return response

    def SetStock(self, request, context):
        current_leader = self.redisClient.get('books-database-election')
        if not current_leader:
            logging.log(logging.DEBUG, f"No current leader, becoming leader with address: {self.service_address}")
            self.redisClient.set('books-database-election', self.service_address, ex=20, nx=True)
            current_leader = self.service_address
        else:
            current_leader = current_leader.decode("utf-8")  # redis returns a binary string

        if current_leader != self.service_address:
            logging.log(logging.DEBUG, f"I am not the leader, sending write request to : {current_leader}")
            with grpc.insecure_channel(current_leader) as channel:
                stub = books_database_grpc.BooksDatabaseServiceStub(channel)
                response = stub.SetStock(request)
                return response
        else:
            logging.log(logging.DEBUG, f"Received SetStock request title: {request.title}")
            self.books[request.title] = request.quantity
            book_counter.set(sum(self.books.values()))
            response = books_database.StockResponse()
            response.title = request.title
            response.quantity = request.quantity
            for replica in self.list_of_replicas:
                logging.log(logging.DEBUG, f"Replicating changes to: {replica}")
                with grpc.insecure_channel(replica) as channel:
                    stub = books_database_grpc.BooksDatabaseServiceStub(channel)
                    response = stub.ReplicateChanges(request)
            return response

    def ReplicateChanges(self, request, context):
        logging.log(logging.DEBUG, f"Received ReplicateChanges request title: {request.title}")
        self.books[request.title] = request.quantity
        book_counter.set(sum(self.books.values()))
        response = books_database.StockResponse()
        response.title = request.title
        response.quantity = request.quantity
        return response


def serve():
    server = grpc.server(futures.ThreadPoolExecutor())
    books_database_grpc.add_BooksDatabaseServiceServicer_to_server(BooksDatabaseService(), server)
    port = os.getenv('PORT', '50060')
    server.add_insecure_port("[::]:" + port)
    server.start()
    print(f"Server started. Listening on port {port}.")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
