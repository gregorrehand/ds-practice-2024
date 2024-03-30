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


# Create a class to define the server functions, derived from
# transaction_verification_pb2_grpc.HelloServiceServicer
class HelloService(transaction_verification_grpc.VerificationServiceServicer):
    def __init__(self, **args):
        super().__init__(**args)
        self.states = dict()

    def TransactionVerification(self, request, context):
        logging.log(logging.INFO, f"Received TransactionVerification request orderId: {request.orderId}")
        self.states[request.orderId] = {"should_cancel": False, "vector_clock": [0, 0, 0]}
        response = transaction_verification.VerificationResponse()

        while True:
            if self.states[request.orderId]["should_cancel"]:
                response.isOk = False
                del self.states[request.orderId]
                return response

            if (not self.states[request.orderId]["should_cancel"] and
                    self.states[request.orderId]["vector_clock"][0] == 0):  # transaction verification hasn't been done

                response.isOk = (request.user_name != "" and
                                 request.user_contact != "" and
                                 request.creditcard_nr != "" and
                                 request.items != [] and
                                 request.quantities != []
                                 )
                self.states[request.orderId]["should_cancel"] = not response.isOk
                self.states[request.orderId]["vector_clock"][0] += 1  # increment the vector clock

                if self.states[request.orderId]["should_cancel"]:
                    # send should_cancel=True to all other services
                    self.send_vector_clock_update("fraud_detection", request.orderId)
                    self.send_vector_clock_update("suggestions", request.orderId)
                    del self.states[request.orderId]
                else:
                    # send vector clock updates to dependant services
                    self.send_vector_clock_update("fraud_detection", request.orderId)

            if (not self.states[request.orderId]["should_cancel"] and
                    self.states[request.orderId]["vector_clock"][0] >= 1 and  # initial transaction verification done
                    self.states[request.orderId]["vector_clock"][1] >= 2):  # fraud detection done

                response.isOk = response.isOk and (sum(request.quantities) > 0)
                self.states[request.orderId]["should_cancel"] = not response.isOk
                self.states[request.orderId]["vector_clock"][0] += 1  # increment the vector clock

                if self.states[request.orderId]["should_cancel"]:
                    # send should_cancel=True to all other services
                    self.send_vector_clock_update("fraud_detection", request.orderId)
                    self.send_vector_clock_update("suggestions", request.orderId)
                else:
                    # send vector clock updates to dependant services
                    self.send_vector_clock_update("suggestions", request.orderId)

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
