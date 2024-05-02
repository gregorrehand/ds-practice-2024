# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import payment_pb2 as payment__pb2


class PaymentServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.DoPayment = channel.unary_unary(
                '/payment.PaymentService/DoPayment',
                request_serializer=payment__pb2.PaymentRequest.SerializeToString,
                response_deserializer=payment__pb2.PaymentResponse.FromString,
                )
        self.ConfirmPayment = channel.unary_unary(
                '/payment.PaymentService/ConfirmPayment',
                request_serializer=payment__pb2.ConfirmPaymentRequest.SerializeToString,
                response_deserializer=payment__pb2.PaymentResponse.FromString,
                )


class PaymentServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def DoPayment(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ConfirmPayment(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_PaymentServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'DoPayment': grpc.unary_unary_rpc_method_handler(
                    servicer.DoPayment,
                    request_deserializer=payment__pb2.PaymentRequest.FromString,
                    response_serializer=payment__pb2.PaymentResponse.SerializeToString,
            ),
            'ConfirmPayment': grpc.unary_unary_rpc_method_handler(
                    servicer.ConfirmPayment,
                    request_deserializer=payment__pb2.ConfirmPaymentRequest.FromString,
                    response_serializer=payment__pb2.PaymentResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'payment.PaymentService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class PaymentService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def DoPayment(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/payment.PaymentService/DoPayment',
            payment__pb2.PaymentRequest.SerializeToString,
            payment__pb2.PaymentResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ConfirmPayment(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/payment.PaymentService/ConfirmPayment',
            payment__pb2.ConfirmPaymentRequest.SerializeToString,
            payment__pb2.PaymentResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
