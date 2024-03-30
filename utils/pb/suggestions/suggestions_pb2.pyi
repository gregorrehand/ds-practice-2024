from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SuggestionsRequest(_message.Message):
    __slots__ = ("orderId",)
    ORDERID_FIELD_NUMBER: _ClassVar[int]
    orderId: str
    def __init__(self, orderId: _Optional[str] = ...) -> None: ...

class SuggestionsResponse(_message.Message):
    __slots__ = ("suggestions",)
    SUGGESTIONS_FIELD_NUMBER: _ClassVar[int]
    suggestions: _containers.RepeatedCompositeFieldContainer[Suggestion]
    def __init__(self, suggestions: _Optional[_Iterable[_Union[Suggestion, _Mapping]]] = ...) -> None: ...

class Suggestion(_message.Message):
    __slots__ = ("bookId", "title", "author")
    BOOKID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    bookId: int
    title: str
    author: str
    def __init__(self, bookId: _Optional[int] = ..., title: _Optional[str] = ..., author: _Optional[str] = ...) -> None: ...

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
