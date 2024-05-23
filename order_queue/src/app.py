import sys
import os
import logging
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
    SERVICE_NAME: "Order queue"
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
meter = metrics.get_meter("orchestrator_metrics")
order_queue_counter = meter.create_up_down_counter("queue.size", unit="1")
order_queue_counter.add(0)

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")

utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/order_queue'))
sys.path.insert(0, utils_path)
import order_queue_pb2 as order_queue
import order_queue_pb2_grpc as order_queue_grpc


import grpc
from concurrent import futures

logging.getLogger().setLevel(logging.DEBUG)  # set logging level so stuff shows up


class OrderQueueService(order_queue_grpc.OrderQueueService):
    def __init__(self):
        self.queue = []

    def Enqueue(self, request, context):
        logging.log(logging.DEBUG, f'Order added to the queue: {request.orderId}')
        self.queue.append((request.orderId, request.items))
        order_queue_counter.add(1)
        return order_queue.EnqueueResponse(success=True)

    def Dequeue(self, request, context):
        if self.queue:
            orderId, items = self.queue.pop(0)
            order_queue_counter.add(-1)
            logging.log(logging.DEBUG, f'Order popped from the queue: {orderId}')
            return order_queue.DequeueResponse(orderId=orderId, items=items, success=True)
        else:
            return order_queue.DequeueResponse(success=False)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor())
    order_queue_grpc.add_OrderQueueServiceServicer_to_server(OrderQueueService(), server)
    port = "50054"
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started. Listening on port 50054.")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
