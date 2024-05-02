import sys
import os
import logging
import time

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")

utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/payment'))
sys.path.insert(0, utils_path)
import payment_pb2 as payment
import payment_pb2_grpc as payment_grpc

import grpc
from concurrent import futures

logging.getLogger().setLevel(logging.DEBUG)  # set logging level so stuff shows up


class PaymentService(payment_grpc.PaymentServiceServicer):

    def __init__(self):
        self.pending_payments = dict()

    def DoPayment(self, request, context):
        logging.log(logging.DEBUG, f"Received Payment request orderId: {request.orderId}")
        self.pending_payments[request.orderId] = (request.targetBankAccount, request.amount)
        response = payment.PaymentResponse()
        response.ok = True
        return response

    def ConfirmPayment(self, request, context):
        logging.log(logging.DEBUG, f"Received ConfirmPayment request orderId: {request.orderId}")
        if request.orderId not in self.pending_payments:
            logging.log(logging.ERROR, f"ERROR, there is no pending payment with orderid {request.orderId}")
            response = payment.PaymentResponse()
            response.ok = False
            return response

        targetBankAccount, amount = self.pending_payments[request.orderId]
        del self.pending_payments[request.orderId]
        logging.log(logging.INFO, f"Paid {round(amount, 2)} to {targetBankAccount}, for orderId {request.orderId}")
        response = payment.PaymentResponse()
        response.ok = True
        return response


def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add HelloService
    payment_grpc.add_PaymentServiceServicer_to_server(PaymentService(), server)
    # Listen on port 50063
    port = "50063"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    print("Server started. Listening on port 50063.")
    # Keep thread alive
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
