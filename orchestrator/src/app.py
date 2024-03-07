import sys
import os
import threading
import logging

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

# show all logs
logging.getLogger().setLevel(logging.DEBUG)

import grpc

def greet(name='you'):
    return "hello"

def get_suggestions(request):
    with grpc.insecure_channel('suggestions:50053') as channel:
        # Create a stub object.
        stub = suggestions_grpc.SuggestionsServiceStub(channel)
        # Call the service through the stub object.
        response = stub.GetSuggestions(suggestions.SuggestionsRequest(name="eee"))
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
                                                           quantities=[x["quantity"] for x in request["items"]])

        # Call the service through the stub object.
        response = stub.TransactionVerification(req)
    return response.isOk


def validate_order(request):
    with grpc.insecure_channel('fraud_detection:50051') as channel:
        # Create a stub object.
        stub = fraud_detection_grpc.FraudDetectionServiceStub(channel)
        req = fraud_detection.FraudDetectionRequest(expirationDate=request["creditCard"]["expirationDate"])

        # Call the service through the stub object.
        response = stub.ValidateOrder(req)
    logging.log(logging.INFO, f"Fraud detection response: {response.isOk}")
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
    logging.log(logging.INFO, f"Received checkout request: {request.json}")
    out_dict = dict()  # save the results of all threads here

    threads = [
        threading.Thread(target=lambda request, out_dict: out_dict.__setitem__("verification", get_verification(request)), args=(request.json, out_dict),
                         name="transaction_verification"),
        threading.Thread(target=lambda request, out_dict: out_dict.__setitem__("fraud_detection", validate_order(request)), args=(request.json, out_dict),
                         name="fraud_detection"),
        threading.Thread(target=lambda request, out_dict: out_dict.__setitem__("suggested_books", get_suggestions(request)),args=(request.json, out_dict),
                         name="suggested_books"),
    ]

    for thread in threads:
        logging.log(logging.INFO, f"Starting thread {thread.name}")
        thread.start()

    for thread in threads:
        thread.join()
        logging.log(logging.INFO, f"Thread {thread.name} done")


    order_status_response = {
        'orderId': '12345',
        'status': 'Order Accepted',
        'suggestedBooks': out_dict["suggested_books"]
    }
    transaction_approved = out_dict["verification"]
    order_approved = out_dict["fraud_detection"]
    if not transaction_approved:
        order_status_response = {
            'status': 'Transaction Rejected',
        }
    if not order_approved:
        order_status_response = {
            'status': 'Order Rejected',
        }

    logging.log(logging.INFO, "Sending order status response")

    return order_status_response


if __name__ == '__main__':
    # Run the app in debug mode to enable hot reloading.
    # This is useful for development.
    # The default port is 5000.
    logging.log(logging.INFO, "Starting orchestrator")
    app.run(host='0.0.0.0')
