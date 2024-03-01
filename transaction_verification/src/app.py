import sys
import os
import logging

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/transaction_verification'))
sys.path.insert(0, utils_path)
import transaction_verification_pb2 as transaction_verification
import transaction_verification_pb2_grpc as transaction_verification_grpc

import grpc
from concurrent import futures

logging.getLogger().setLevel(logging.DEBUG)  # set logging level so stuff shows up

# Create a class to define the server functions, derived from
# transaction_verification_pb2_grpc.HelloServiceServicer
class HelloService(transaction_verification_grpc.VerificationServiceServicer):
    # Create an RPC function to say hello
    def TransactionVerification(self, request, context):

        logging.log(logging.INFO, "Received TransactionVerification request")

        response = transaction_verification.VerificationResponse()

        response.isOk = (request.user_name != "" and
                         request.user_contact != "" and
                         request.creditcard_nr != "" and
                         request.items != [] and
                         request.quantities != [] and
                         sum(request.quantities) > 0
                         )

        #print(request.user_name, request.user_contact, request.creditcard_nr, request.items, request.quantities)

        # Return the response object
        return response

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add HelloService
    transaction_verification_grpc.add_VerificationServiceServicer_to_server(HelloService(), server)
    # Listen on port 50052
    port = "50052"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    print("Server started. Listening on port 50052.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()