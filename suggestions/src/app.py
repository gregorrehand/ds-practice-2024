import sys
import os
import logging
import time

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

import grpc
from concurrent import futures

logging.getLogger().setLevel(logging.DEBUG)  # set logging level so stuff shows up


class SuggestionsService(suggestions_grpc.SuggestionsServiceServicer):

    def __init__(self, **args):
        super().__init__(**args)
        self.states = dict()

    def GetSuggestions(self, request, context):
        logging.log(logging.INFO, f"Received GetSuggestions request orderId: {request.orderId}")
        self.states[request.orderId] = {"should_cancel": False, "vector_clock": [0, 0, 0]}

        while True:
            if self.states[request.orderId]["should_cancel"]:
                del self.states[request.orderId]
                return suggestions.SuggestionsResponse()

            if (not self.states[request.orderId]["should_cancel"] and
                    self.states[request.orderId]["vector_clock"][0] >= 2 and  # transaction verification is done
                    self.states[request.orderId]["vector_clock"][1] >= 1):  # fraud detection is done
                response = suggestions.SuggestionsResponse()
                response.suggestions.extend([
                    suggestions.Suggestion(bookId=1, title="Book 1", author="Author 1"),
                    suggestions.Suggestion(bookId=2, title="Book 2", author="Author 2"),
                    suggestions.Suggestion(bookId=3, title="Book 3", author="Author 3"),
                ])

                self.states[request.orderId]["vector_clock"][2] += 1

                if self.states[request.orderId]["should_cancel"]:
                    # send should_cancel=True to all other services
                    self.send_vector_clock_update("transaction_verification", request.orderId)
                    self.send_vector_clock_update("fraud_detection", request.orderId)
                else:
                    # send vector clock updates to dependant services
                    pass

                del self.states[request.orderId]
                return response

            time.sleep(0.01)

    def send_vector_clock_update(self, service_name, order_id):
        """
        Send vector clock update to dependant services
        """
        if service_name == "fraud_detection":
            with grpc.insecure_channel('fraud_detection:50051') as channel:
                stub = fraud_detection_grpc.FraudDetectionServiceStub(channel)
                stub.UpdateVectorClock(fraud_detection.VectorClockRequest(
                    orderId=order_id,
                    vectorClock=self.states[order_id]["vector_clock"],
                    shouldCancel=self.states[order_id]["should_cancel"],
                ))
        if service_name == "transaction_verification":
            with grpc.insecure_channel('transaction_verification:50052') as channel:
                stub = transaction_verification_grpc.VerificationServiceStub(channel)
                stub.UpdateVectorClock(transaction_verification.VectorClockRequest(
                    orderId=order_id,
                    vectorClock=self.states[order_id]["vector_clock"],
                    shouldCancel=self.states[order_id]["should_cancel"],
                ))
        if service_name == "suggestions":
            with grpc.insecure_channel('suggestions:50053') as channel:
                stub = suggestions_grpc.SuggestionsServiceStub(channel)
                stub.UpdateVectorClock(suggestions.VectorClockRequest(
                    orderId=order_id,
                    vectorClock=self.states[order_id]["vector_clock"],
                    shouldCancel=self.states[order_id]["should_cancel"],
                ))

    def UpdateVectorClock(self, request, context):
        """
        Recieve a vector clock update
        """
        logging.log(logging.INFO, f"Received UpdateVectorClock {request.orderId} {request.shouldCancel} {request.vectorClock}")
        if request.orderId in self.states:
            self.states[request.orderId]["should_cancel"] = request.shouldCancel

            # update vector clock
            self.states[request.orderId]["vector_clock"] = [
                max(request.vectorClock[i], self.states[request.orderId]["vector_clock"][i])
                for i in range(len(request.vectorClock))
            ]
        return fraud_detection.Empty()


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
