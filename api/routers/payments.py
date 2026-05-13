from fastapi import APIRouter
from api.schemas import (
    ChargeCustomerIn,
    PaymentConfirmIn,
    PaymentIntentCreateIn,
    PaymentOut,
    RefundIn,
    RefundOut,
)
from stripe_payment.payment import (
    cancel_payment_intent,
    charge_customer,
    confirm_payment_intent,
    create_payment_intent,
    refund_payment,
    retrieve_payment_intent,
)

router = APIRouter(prefix="/payments", tags=["payments"])


def _to_payment_out(result) -> PaymentOut:
    return PaymentOut(
        payment_intent_id=result.payment_intent_id,
        status=result.status.value if hasattr(result.status, "value") else result.status,
        amount=result.amount,
        currency=result.currency,
        amount_display=result.amount_display,
        customer_id=result.customer_id,
        payment_method_id=result.payment_method_id,
        client_secret=result.client_secret,
        receipt_url=result.receipt_url,
        metadata=result.metadata,
    )


@router.post("/intents", response_model=PaymentOut, status_code=201)
def create_intent_endpoint(body: PaymentIntentCreateIn):
    result = create_payment_intent(
        amount=body.amount, currency=body.currency,
        customer_id=body.customer_id, payment_method_id=body.payment_method_id,
        description=body.description, metadata=body.metadata, confirm=body.confirm,
    )
    return _to_payment_out(result)


@router.get("/intents/{intent_id}", response_model=PaymentOut)
def get_intent_endpoint(intent_id: str):
    return _to_payment_out(retrieve_payment_intent(intent_id))


@router.post("/intents/{intent_id}/confirm", response_model=PaymentOut)
def confirm_intent_endpoint(intent_id: str, body: PaymentConfirmIn):
    return _to_payment_out(confirm_payment_intent(intent_id, body.payment_method_id))


@router.post("/intents/{intent_id}/cancel", response_model=PaymentOut)
def cancel_intent_endpoint(intent_id: str):
    return _to_payment_out(cancel_payment_intent(intent_id))


@router.post("/charge", response_model=PaymentOut, status_code=201)
def charge_customer_endpoint(body: ChargeCustomerIn):
    result = charge_customer(
        customer_id=body.customer_id, payment_method_id=body.payment_method_id,
        amount=body.amount, currency=body.currency,
        description=body.description, metadata=body.metadata,
    )
    return _to_payment_out(result)


@router.post("/refunds", response_model=RefundOut, status_code=201)
def refund_endpoint(body: RefundIn):
    result = refund_payment(
        payment_intent_id=body.payment_intent_id,
        amount=body.amount, reason=body.reason,
    )
    return RefundOut(
        refund_id=result.refund_id,
        payment_intent_id=result.payment_intent_id,
        amount=result.amount,
        currency=result.currency,
        status=result.status,
    )
