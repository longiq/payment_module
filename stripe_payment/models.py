from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class PaymentStatus(str, Enum):
    SUCCEEDED = "succeeded"
    PENDING = "pending"
    FAILED = "failed"
    CANCELED = "canceled"
    REQUIRES_ACTION = "requires_action"
    REQUIRES_CONFIRMATION = "requires_confirmation"
    REQUIRES_PAYMENT_METHOD = "requires_payment_method"
    REQUIRES_CAPTURE = "requires_capture"


class Currency(str, Enum):
    USD = "usd"
    EUR = "eur"
    GBP = "gbp"
    VND = "vnd"
    JPY = "jpy"
    SGD = "sgd"
    AUD = "aud"


@dataclass
class CardDetails:
    number: str
    exp_month: int
    exp_year: int
    cvc: str
    name: Optional[str] = None


@dataclass
class Address:
    line1: str
    city: str
    country: str  # ISO 3166-1 alpha-2, e.g. "US", "VN"
    line2: Optional[str] = None
    postal_code: Optional[str] = None
    state: Optional[str] = None


@dataclass
class CustomerData:
    email: str
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[Address] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class PaymentResult:
    payment_intent_id: str
    status: PaymentStatus
    amount: int  # smallest currency unit (cents for USD, đồng for VND)
    currency: str
    customer_id: Optional[str] = None
    payment_method_id: Optional[str] = None
    client_secret: Optional[str] = None
    receipt_url: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    @property
    def amount_display(self) -> str:
        major_units = ["jpy", "vnd"]
        if self.currency.lower() in major_units:
            return f"{self.amount} {self.currency.upper()}"
        return f"{self.amount / 100:.2f} {self.currency.upper()}"


@dataclass
class CustomerResult:
    customer_id: str
    email: str
    name: Optional[str] = None
    payment_method_id: Optional[str] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class RefundResult:
    refund_id: str
    payment_intent_id: str
    amount: int
    currency: str
    status: str
