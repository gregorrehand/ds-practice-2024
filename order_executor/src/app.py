import sys
import os
import logging
import time
import redis
import random

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")

utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/order_queue'))
sys.path.insert(0, utils_path)
import order_queue_pb2 as order_queue
import order_queue_pb2_grpc as order_queue_grpc

utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/books_database'))
sys.path.insert(0, utils_path)
import books_database_pb2 as books_database
import books_database_pb2_grpc as books_database_grpc

utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/order_executor'))
sys.path.insert(0, utils_path)
import order_executor_pb2 as order_executor
import order_executor_pb2_grpc as order_executor_grpc

utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/payment'))
sys.path.insert(0, utils_path)
import payment_pb2 as payment
import payment_pb2_grpc as payment_grpc

import grpc
from concurrent import futures

logging.getLogger().setLevel(logging.DEBUG)  # set logging level so stuff shows up


class OrderExecutorService:
    def __init__(self):
        self.redisClient = redis.Redis(host='redis', port=6379, db=0)
        self.service_id = os.getenv('SERVICE_ID', 'executor1')
        while True:
            #logging.log(logging.DEBUG, f"{self.service_id} is trying to become the leader")
            leader = self.try_to_become_leader()
            if leader:
                #logging.log(logging.DEBUG, f"{self.service_id} is now the leader")
                self.execute_order()
            else:
                #logging.log(logging.DEBUG, f"{self.service_id} is not the leader, waiting")
                time.sleep(0.1)  # Wait a bit before retrying for leadership

    def dequeue_order(self):
        with grpc.insecure_channel('order_queue:50054') as channel:
            stub = order_queue_grpc.OrderQueueServiceStub(channel)
            response = stub.Dequeue(order_queue.DequeueRequest())
        return response

    def execute_order(self):
        try:
            response = self.dequeue_order()
            if response.success:
                orderid = response.orderId
                logging.log(logging.INFO, f"Order {orderid} is being executed...")
                db_ports = [(1, 50060), (2, 50061), (3, 50062)]
                for item in response.items:
                    service, port = random.choice(db_ports)
                    with grpc.insecure_channel(f"books_database_{service}:{port}") as database_channel:
                        with grpc.insecure_channel(f"payment:50063") as payment_channel:
                            database_stub = books_database_grpc.BooksDatabaseServiceStub(database_channel)
                            payment_stub = payment_grpc.PaymentServiceStub(payment_channel)
                            req = books_database.GetStockRequest(
                                title=item.name
                            )

                            # Check, that books_database is ready to commit and has enough stock
                            stock_response = database_stub.GetStock(req)
                            logging.log(logging.DEBUG, f"Get stock response: {stock_response.quantity}")
                            if stock_response.quantity < item.quantity:
                                logging.log(logging.ERROR, f"Failed to execute order {orderid}: Not enough stock for item {item.name}")
                                return

                            # Check, that payment service is ready to commit
                            payment_response = payment_stub.DoPayment(payment.PaymentRequest(
                                orderId=orderid,
                                targetBankAccount="EE73234212312",
                                amount=14.99,
                            ))

                            if not payment_response.ok:
                                logging.log(logging.ERROR, f"Failed to execute order {orderid}: Payment service not ready")
                                return

                            logging.log(logging.DEBUG, f"2PC succeeded for Payment and BooksDatabase. Executing order {orderid}")

                            # Commit the changes: make the payment and update the stock
                            database_stub.SetStock(books_database.SetStockRequest(
                                title=item.name,
                                quantity=stock_response.quantity - item.quantity,
                            ))

                            payment_stub.ConfirmPayment(payment.ConfirmPaymentRequest(
                                orderId=orderid,
                            ))
            else:
                logging.log(logging.INFO, "No order to execute.")
                time.sleep(1)
        except grpc.RpcError as e:
            logging.log(logging.ERROR, f"Failed to dequeue order: {e}")

    def try_to_become_leader(self, ttl_seconds=1):
        acquired = self.redisClient.set('order-executor-election', self.service_id, ex=ttl_seconds, nx=True)
        return bool(acquired)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor())
    order_executor_grpc.add_OrderExecutorServiceServicer_to_server(OrderExecutorService(), server)
    port = os.getenv('PORT', '50056')
    server.add_insecure_port("[::]:" + port)
    server.start()
    print(f"Server started. Listening on port {port}.")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
