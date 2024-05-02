from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class PaymentRequest(_message.Message):
    __slots__ = ("orderId", "targetBankAccount", "amount")
    ORDERID_FIELD_NUMBER: _ClassVar[int]
    TARGETBANKACCOUNT_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    orderId: str
    targetBankAccount: str
    amount: float
    def __init__(self, orderId: _Optional[str] = ..., targetBankAccount: _Optional[str] = ..., amount: _Optional[float] = ...) -> None: ...

class ConfirmPaymentRequest(_message.Message):
    __slots__ = ("orderId",)
    ORDERID_FIELD_NUMBER: _ClassVar[int]
    orderId: str
    def __init__(self, orderId: _Optional[str] = ...) -> None: ...

class PaymentResponse(_message.Message):
    __slots__ = ("ok",)
    OK_FIELD_NUMBER: _ClassVar[int]
    ok: bool
    def __init__(self, ok: bool = ...) -> None: ...
