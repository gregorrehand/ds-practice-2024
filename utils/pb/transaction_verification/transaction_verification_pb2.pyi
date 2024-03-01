from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class VerificationRequest(_message.Message):
    __slots__ = ("user_name", "user_contact", "creditcard_nr", "items", "quantities")
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    USER_CONTACT_FIELD_NUMBER: _ClassVar[int]
    CREDITCARD_NR_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    QUANTITIES_FIELD_NUMBER: _ClassVar[int]
    user_name: str
    user_contact: str
    creditcard_nr: str
    items: _containers.RepeatedScalarFieldContainer[str]
    quantities: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, user_name: _Optional[str] = ..., user_contact: _Optional[str] = ..., creditcard_nr: _Optional[str] = ..., items: _Optional[_Iterable[str]] = ..., quantities: _Optional[_Iterable[int]] = ...) -> None: ...

class VerificationResponse(_message.Message):
    __slots__ = ("isOk",)
    ISOK_FIELD_NUMBER: _ClassVar[int]
    isOk: bool
    def __init__(self, isOk: bool = ...) -> None: ...
