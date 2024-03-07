from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class FraudDetectionRequest(_message.Message):
    __slots__ = ("expirationDate",)
    EXPIRATIONDATE_FIELD_NUMBER: _ClassVar[int]
    expirationDate: str
    def __init__(self, expirationDate: _Optional[str] = ...) -> None: ...

class FraudDetectionResponse(_message.Message):
    __slots__ = ("isOk",)
    ISOK_FIELD_NUMBER: _ClassVar[int]
    isOk: bool
    def __init__(self, isOk: bool = ...) -> None: ...
