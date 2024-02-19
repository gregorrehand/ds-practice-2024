import sys
import os
import threading

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/fraud_detection'))
sys.path.insert(0, utils_path)
import fraud_detection_pb2 as fraud_detection
import fraud_detection_pb2_grpc as fraud_detection_grpc

utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/transaction_verification'))
sys.path.insert(0, utils_path)
import transaction_verification_pb2 as transaction_verification
import transaction_verification_pb2_grpc as transaction_verification_grpc

import grpc

def greet(name='you'):
    # Establish a connection with the fraud-detection gRPC service.
    with grpc.insecure_channel('fraud_detection:50051') as channel:
        # Create a stub object.
        stub = fraud_detection_grpc.HelloServiceStub(channel)
        # Call the service through the stub object.

        response = stub.SayHello(fraud_detection.HelloRequest(name=name))
    return response.greeting


def get_verification(request):
    with grpc.insecure_channel('transaction_verification:50052') as channel:
        # Create a stub object.
        stub = transaction_verification_grpc.VerificationServiceStub(channel)
        req = transaction_verification.VerificationRequest(user_name=request["user"]["name"],
                                                           user_contact=request["user"]["contact"],
                                                           creditcard_nr=request["creditCard"]["number"],
                                                           items=[x["name"] for x in request["items"]],
                                                           quantities=[x["quantity"] for x in request["items"]])

        # Call the service through the stub object.
        response = stub.TransactionVerification(req)
    return response.isOk


# Import Flask.
# Flask is a web framework for Python.
# It allows you to build a web application quickly.
# For more information, see https://flask.palletsprojects.com/en/latest/
from flask import Flask, request
from flask_cors import CORS

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
def checkout():
    """
    Responds with a JSON object containing the order ID, status, and suggested books.
    """
    # Print request object data
    print("Request Data:", request.json)
    out_dict = dict()  # save the results of all threads here

    threads = [
        threading.Thread(target=lambda request, out_dict: out_dict.__setitem__("verification", get_verification(request)), args=(request.json, out_dict)),
        # todo make similar threads for fraud detection and suggestion service
        # threading.Thread(target=lambda request, out_dict: out_dict.__setitem__("fraud_detection", is_fraud(request)), args=(request.json, out_dict)),
        # threading.Thread(target=lambda request, out_dict: out_dict.__setitem__("suggested_books", get_recommendations(request)),args=(request.json, out_dict)),
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    print("thread outputs:", out_dict)

    is_approved = out_dict["verification"] #and out_dict["fraud_detection"]

    # Dummy response following the provided YAML specification for the bookstore
    order_status_response = {
        'orderId': '12345',
        'status': 'Order Approved' if is_approved else "Order Rejected",
        'suggestedBooks': None  # out_dict["suggested_books"]
    }

    return order_status_response


if __name__ == '__main__':
    # Run the app in debug mode to enable hot reloading.
    # This is useful for development.
    # The default port is 5000.
    app.run(host='0.0.0.0')
