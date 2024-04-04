from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Order(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class EnqueueRequest(_message.Message):
    __slots__ = ("orderId",)
    ORDERID_FIELD_NUMBER: _ClassVar[int]
    orderId: str
    def __init__(self, orderId: _Optional[str] = ...) -> None: ...

class EnqueueResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class DequeueRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DequeueResponse(_message.Message):
    __slots__ = ("order", "success")
    ORDER_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    order: Order
    success: bool
    def __init__(self, order: _Optional[_Union[Order, _Mapping]] = ..., success: bool = ...) -> None: ...
