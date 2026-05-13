from typing import Optional
from pydantic import BaseModel, EmailStr


class AddressIn(BaseModel):
    line1: str
    city: str
    country: str
    line2: Optional[str] = None
    postal_code: Optional[str] = None
    state: Optional[str] = None


class CardDetailsIn(BaseModel):
    number: str
    exp_month: int
    exp_year: int
    cvc: str
    name: Optional[str] = None


class CustomerCreateIn(BaseModel):
    email: str
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[AddressIn] = None
    metadata: dict = {}


class PaymentIntentCreateIn(BaseModel):
    amount: int
    currency: str
    customer_id: Optional[str] = None
    payment_method_id: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[dict] = None
    confirm: bool = False


class PaymentConfirmIn(BaseModel):
    payment_method_id: Optional[str] = None


class ChargeCustomerIn(BaseModel):
    customer_id: str
    payment_method_id: str
    amount: int
    currency: str
    description: Optional[str] = None
    metadata: Optional[dict] = None


class RefundIn(BaseModel):
    payment_intent_id: str
    amount: Optional[int] = None
    reason: Optional[str] = None


class CustomerOut(BaseModel):
    customer_id: str
    email: str
    name: Optional[str] = None
    payment_method_id: Optional[str] = None
    metadata: dict = {}


class PaymentOut(BaseModel):
    payment_intent_id: str
    status: str
    amount: int
    currency: str
    amount_display: str
    customer_id: Optional[str] = None
    payment_method_id: Optional[str] = None
    client_secret: Optional[str] = None
    receipt_url: Optional[str] = None
    metadata: dict = {}


class RefundOut(BaseModel):
    refund_id: str
    payment_intent_id: str
    amount: int
    currency: str
    status: str
