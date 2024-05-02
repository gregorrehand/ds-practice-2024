# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: order_queue.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11order_queue.proto\x12\x0border_queue\"C\n\x0e\x45nqueueRequest\x12\x0f\n\x07orderId\x18\x01 \x01(\t\x12 \n\x05items\x18\x02 \x03(\x0b\x32\x11.order_queue.Item\"&\n\x04Item\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x10\n\x08quantity\x18\x02 \x01(\x05\"\"\n\x0f\x45nqueueResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\"\x10\n\x0e\x44\x65queueRequest\"U\n\x0f\x44\x65queueResponse\x12\x0f\n\x07orderId\x18\x01 \x01(\t\x12 \n\x05items\x18\x02 \x03(\x0b\x32\x11.order_queue.Item\x12\x0f\n\x07success\x18\x03 \x01(\x08\x32\xa3\x01\n\x11OrderQueueService\x12\x46\n\x07\x45nqueue\x12\x1b.order_queue.EnqueueRequest\x1a\x1c.order_queue.EnqueueResponse\"\x00\x12\x46\n\x07\x44\x65queue\x12\x1b.order_queue.DequeueRequest\x1a\x1c.order_queue.DequeueResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'order_queue_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_ENQUEUEREQUEST']._serialized_start=34
  _globals['_ENQUEUEREQUEST']._serialized_end=101
  _globals['_ITEM']._serialized_start=103
  _globals['_ITEM']._serialized_end=141
  _globals['_ENQUEUERESPONSE']._serialized_start=143
  _globals['_ENQUEUERESPONSE']._serialized_end=177
  _globals['_DEQUEUEREQUEST']._serialized_start=179
  _globals['_DEQUEUEREQUEST']._serialized_end=195
  _globals['_DEQUEUERESPONSE']._serialized_start=197
  _globals['_DEQUEUERESPONSE']._serialized_end=282
  _globals['_ORDERQUEUESERVICE']._serialized_start=285
  _globals['_ORDERQUEUESERVICE']._serialized_end=448
# @@protoc_insertion_point(module_scope)