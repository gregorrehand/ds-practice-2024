import random
import sys
import os
import threading
import logging
import time

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
    SERVICE_NAME: "Orchestrator"
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
order_counter = meter.create_counter("order.counter", unit="1")
order_counter.add(0)
hist = meter.create_histogram("aaa", unit="1")
accepted_order_counter = meter.create_counter("accepted.order.counter", unit="1")
accepted_order_counter.add(0)
rejected_order_counter = meter.create_counter("rejected.order.counter", unit="1")
rejected_order_counter.add(0)
order_latency = meter.create_gauge("avg.order.time", unit="1")
order_latency.set(0)
running_avg_order_latency = 0

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/fraud_detection'))
sys.path.insert(0, utils_path)
import fraud_detection_pb2 as fraud_detection
import fraud_detection_pb2_grpc as fraud_detection_grpc

utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/suggestions'))
sys.path.insert(0, utils_path)
import suggestions_pb2 as suggestions
import suggestions_pb2_grpc as suggestions_grpc

utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/transaction_verification'))
sys.path.insert(0, utils_path)
import transaction_verification_pb2 as transaction_verification
import transaction_verification_pb2_grpc as transaction_verification_grpc

utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/order_queue'))
sys.path.insert(0, utils_path)
import order_queue_pb2 as order_queue
import order_queue_pb2_grpc as order_queue_grpc

# show all logs
logging.getLogger().setLevel(logging.DEBUG)

import grpc

order_id_counter = 0


@tracer.start_as_current_span("Get new orderId")
def get_order_id():
    global order_id_counter
    order_id_counter += 1
    return order_id_counter - 1


def greet(name='you'):
    return "hello"


def get_suggestions(request):
    with grpc.insecure_channel('suggestions:50053') as channel:
        stub = suggestions_grpc.SuggestionsServiceStub(channel)
        response = stub.GetSuggestions(suggestions.SuggestionsRequest(
            orderId=request["order_id"],
        ))
    return [suggestion_to_dict(suggestion) for suggestion in response.suggestions]


def suggestion_to_dict(suggestion):
    return {
        "bookId": suggestion.bookId,
        "title": suggestion.title,
        "author": suggestion.author,
    }


def get_verification(request):
    with grpc.insecure_channel('transaction_verification:50052') as channel:
        # Create a stub object.
        stub = transaction_verification_grpc.VerificationServiceStub(channel)
        req = transaction_verification.VerificationRequest(user_name=request["user"]["name"],
                                                           user_contact=request["user"]["contact"],
                                                           creditcard_nr=request["creditCard"]["number"],
                                                           items=[x["name"] for x in request["items"]],
                                                           quantities=[x["quantity"] for x in request["items"]],
                                                           orderId=request["order_id"],
                                                           )

        # Call the service through the stub object.
        response = stub.TransactionVerification(req)
    return response.isOk


def validate_order(request):
    with grpc.insecure_channel('fraud_detection:50051') as channel:
        # Create a stub object.
        stub = fraud_detection_grpc.FraudDetectionServiceStub(channel)
        req = fraud_detection.FraudDetectionRequest(
            expirationDate=request["creditCard"]["expirationDate"],
            userName=request["user"]["name"],
            orderId=request["order_id"],
        )

        # Call the service through the stub object.
        response = stub.ValidateOrder(req)
    return response.isOk


@tracer.start_as_current_span("Enqueue order")
def enqueue_order(request):
    with grpc.insecure_channel('order_queue:50054') as channel:
        stub = order_queue_grpc.OrderQueueServiceStub(channel)
        response = stub.Enqueue(order_queue.EnqueueRequest(
            orderId=request["order_id"],
            items=request["items"]
        ))
    return response.success


# Import Flask.
# Flask is a web framework for Python.
# It allows you to build a web application quickly.
# For more information, see https://flask.palletsprojects.com/en/latest/
from flask import Flask, request
from flask_cors import CORS, cross_origin

# Create a simple Flask app.
app = Flask(__name__)


# Enable CORS for the app.
CORS(app)

# Define a GET endpoint.
@app.route('/', methods=['GET'])
def index():
    """
    Responds with 'Hello, [name]' when a GET request is made to '/' endpoint.
    """
    # Test the fraud-detection gRPC service.
    response = greet(name='orchestrator')
    # Return the response.
    return response


@app.route('/checkout', methods=['POST'])
@tracer.start_as_current_span("Checkout")
def checkout():
    """
    Responds with a JSON object containing the order ID, status, and suggested books.
    """
    global running_avg_order_latency, order_id_counter
    start_time = time.time()
    # Print request object data
    request.json["order_id"] = str(get_order_id())
    logging.log(logging.INFO, f"Received checkout request: {request.json}")
    order_counter.add(1)

    out_dict = dict()  # save the results of all threads here
    threads = [
        threading.Thread(
            target=lambda request, out_dict: out_dict.__setitem__("verification", get_verification(request)),
            args=(request.json, out_dict),
            name="transaction_verification"),
        threading.Thread(
            target=lambda request, out_dict: out_dict.__setitem__("fraud_detection", validate_order(request)),
            args=(request.json, out_dict),
            name="fraud_detection"),
        threading.Thread(
            target=lambda request, out_dict: out_dict.__setitem__("suggested_books", get_suggestions(request)),
            args=(request.json, out_dict),
            name="suggested_books"),
    ]
    with tracer.start_as_current_span("Order confirmation") as span:
        for thread in threads:
            logging.log(logging.INFO, f"Starting thread {thread.name}")
            thread.start()

        for thread in threads:
            thread.join()
            logging.log(logging.INFO, f"Thread {thread.name} done")

    order_status_response = {
        'orderId': request.json["order_id"],
        'status': 'Order Accepted',
        'suggestedBooks': out_dict["suggested_books"]
    }
    transaction_approved = out_dict["verification"]
    order_approved = out_dict["fraud_detection"]
    if not transaction_approved:
        running_avg_order_latency += time.time() - start_time
        hist.record((time.time() - start_time) * 100000)
        order_latency.set(running_avg_order_latency / order_id_counter)
        rejected_order_counter.add(1)
        return {
            'status': 'Transaction Rejected',
        }
    if not order_approved:
        running_avg_order_latency += time.time() - start_time
        hist.record((time.time() - start_time) * 100000)
        order_latency.set(running_avg_order_latency / order_id_counter)
        rejected_order_counter.add(1)
        return {
            'status': 'Order Rejected',
        }

    logging.log(logging.INFO, "Sending order status response")
    queue_success = enqueue_order(request.json)
    if not queue_success:
        running_avg_order_latency += time.time() - start_time
        hist.record((time.time() - start_time) * 100000)
        order_latency.set(running_avg_order_latency / order_id_counter)
        rejected_order_counter.add(1)
        return {
            'status': 'Order rejected due to technical problems',
        }
    running_avg_order_latency += time.time() - start_time
    hist.record((time.time() - start_time) * 100000)
    order_latency.set(running_avg_order_latency / order_id_counter)
    accepted_order_counter.add(1)
    return order_status_response


if __name__ == '__main__':
    # Run the app in debug mode to enable hot reloading.
    # This is useful for development.
    # The default port is 5000.
    logging.log(logging.INFO, "Starting orchestrator")
    app.run(host='0.0.0.0')
