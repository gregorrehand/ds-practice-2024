import sys
import os
import logging
import time
import etcd3

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")

utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/order_queue'))
sys.path.insert(0, utils_path)
import order_queue_pb2 as order_queue
import order_queue_pb2_grpc as order_queue_grpc

utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/order_executor'))
sys.path.insert(0, utils_path)
import order_executor_pb2 as order_executor
import order_executor_pb2_grpc as order_executor_grpc

import grpc
from concurrent import futures

logging.getLogger().setLevel(logging.DEBUG)  # set logging level so stuff shows up

class OrderExecutorService():
    def __init__(self):
        self.order_queue_stub = order_queue_grpc.OrderQueueStub(grpc.insecure_channel(os.getenv('ETCD_ADDRESS', 'localhost') + ':' + 50054))
        self.etcd = etcd3.client(host=os.getenv('ETCD_ADDRESS', 'localhost'), port=int(os.getenv('ETCD_PORT', '2379')))
        self.service_id = os.getenv('SERVICE_ID', 'executor1')
        self.election = self.etcd.election('order-executor-election')

    def start(self):
        while True:
            logging.log(logging.DEBUG, f"{self.service_id} is trying to become the leader")
            with self.election as leader: # This line campaigns for leadership and releases it after the block is done
                if leader.leader_value == self.service_id:
                    logging.log(logging.DEBUG, f"{self.service_id} is now the leader")
                    self.execute_order()
                else:
                    logging.log(logging.DEBUG, f"{self.service_id} is not the leader, waiting")
            time.sleep(5)  # Wait a bit before retrying for leadership
    def execute_order(self):
        return True
        try:
            response = self.order_queue_stub.Dequeue(order_queue.DequeueRequest())
            if response.success:
                logging.log(logging.INFO, f"Order {response.order.id} is being executed...")
            else:
                logging.log(logging.INFO, "No order to execute.")
                time.sleep(1)
        except grpc.RpcError as e:
            logging.log(logging.ERROR, f"Failed to dequeue order: {e}")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor())
    order_executor_grpc.add_OrderExecutorServiceServicer_to_server(OrderExecutorService(), server)
    port = os.getenv('PORT', '50056')
    server.add_insecure_port("[::]:" + port)
    server.start()
    print(f"Server started. Listening on port {port}.")
    server.wait_for_termination()