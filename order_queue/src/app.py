import sys
import os
import logging

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
        return order_queue.EnqueueResponse(success=True)

    def Dequeue(self, request, context):
        if self.queue:
            orderId, items = self.queue.pop(0)
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
