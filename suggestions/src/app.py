import sys
import os
import logging

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/suggestions'))
sys.path.insert(0, utils_path)
import suggestions_pb2 as suggestions
import suggestions_pb2_grpc as suggestions_grpc

import grpc
from concurrent import futures

logging.getLogger().setLevel(logging.DEBUG)  # set logging level so stuff shows up

# Create a class to define the server functions, derived from
# suggestions_pb2_grpc.HelloServiceServicer
class SuggestionsService(suggestions_grpc.SuggestionsServiceServicer):
    # Create an RPC function to say hello
    def GetSuggestions(self, request, context):

        logging.log(logging.INFO, "Received GetSuggestions request")

        # Create a SuggestionsResponse object
        response = suggestions.SuggestionsResponse()
        response.suggestions.extend([
            suggestions.Suggestion(bookId=1, title="Book 1", author="Author 1"),
            suggestions.Suggestion(bookId=2, title="Book 2", author="Author 2"),
            suggestions.Suggestion(bookId=3, title="Book 3", author="Author 3"),
        ])
        # Return the response object
        return response

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add HelloService
    suggestions_grpc.add_SuggestionsServiceServicer_to_server(SuggestionsService(), server)
    # Listen on port 50051
    port = "50053"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    print("Server started. Listening on port 50053.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()