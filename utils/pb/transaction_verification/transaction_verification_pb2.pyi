from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class VerificationRequest(_message.Message):
    __slots__ = ("user_name", "user_contact", "creditcard_nr", "items", "quantities", "orderId")
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    USER_CONTACT_FIELD_NUMBER: _ClassVar[int]
    CREDITCARD_NR_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    QUANTITIES_FIELD_NUMBER: _ClassVar[int]
    ORDERID_FIELD_NUMBER: _ClassVar[int]
    user_name: str
    user_contact: str
    creditcard_nr: str
    items: _containers.RepeatedScalarFieldContainer[str]
    quantities: _containers.RepeatedScalarFieldContainer[int]
    orderId: str
    def __init__(self, user_name: _Optional[str] = ..., user_contact: _Optional[str] = ..., creditcard_nr: _Optional[str] = ..., items: _Optional[_Iterable[str]] = ..., quantities: _Optional[_Iterable[int]] = ..., orderId: _Optional[str] = ...) -> None: ...

class VerificationResponse(_message.Message):
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
