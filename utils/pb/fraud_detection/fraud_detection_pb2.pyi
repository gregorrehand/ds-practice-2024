from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class FraudDetectionRequest(_message.Message):
    __slots__ = ("expirationDate", "orderId", "userName")
    EXPIRATIONDATE_FIELD_NUMBER: _ClassVar[int]
    ORDERID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    expirationDate: str
    orderId: str
    userName: str
    def __init__(self, expirationDate: _Optional[str] = ..., orderId: _Optional[str] = ..., userName: _Optional[str] = ...) -> None: ...

class FraudDetectionResponse(_message.Message):
    __slots__ = ("isOk",)
    ISOK_FIELD_NUMBER: _ClassVar[int]
    isOk: bool
    def __init__(self, isOk: bool = ...) -> None: ...

class VectorClockRequest(_message.Message):
    __slots__ = ("orderId", "vectorClock", "shouldCancel")
    ORDERID_FIELD_NUMBER: _ClassVar[int]
    VECTORCLOCK_FIELD_NUMBER: _ClassVar[int]
    SHOULDCANCEL_FIELD_NUMBER: _ClassVar[int]
    orderId: str
    vectorClock: _containers.RepeatedScalarFieldContainer[int]
    shouldCancel: bool
    def __init__(self, orderId: _Optional[str] = ..., vectorClock: _Optional[_Iterable[int]] = ..., shouldCancel: bool = ...) -> None: ...

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
