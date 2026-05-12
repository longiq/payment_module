from typing import Optional
import stripe
from .client import get_stripe_client
from .models import PaymentResult, PaymentStatus, RefundResult
from .exceptions import (CardDeclinedError, InvalidCardError, InsufficientFundsError,
                         PaymentIntentError, StripePaymentError)


def create_payment_intent(
    amount: int, currency: str,
    customer_id: Optional[str] = None, payment_method_id: Optional[str] = None,
    description: Optional[str] = None, metadata: Optional[dict] = None,
    confirm: bool = False,
) -> PaymentResult:
    client = get_stripe_client()
    payload: dict = {
        "amount": amount, "currency": currency.lower(),
        "automatic_payment_methods": {"enabled": True}, "metadata": metadata or {},
    }
    if customer_id:
        payload["customer"] = customer_id
    if payment_method_id:
        payload["payment_method"] = payment_method_id
    if description:
        payload["description"] = description
    if confirm:
        payload["confirm"] = True
        payload["return_url"] = "https://example.com/payment/return"
    try:
        intent = client.PaymentIntent.create(**payload)
        return _build_result(intent)
    except stripe.error.CardError as e:
        _raise_card_error(e)
    except stripe.error.InvalidRequestError as e:
        raise PaymentIntentError(str(e), code="invalid_request", stripe_error=e) from e
    except stripe.error.StripeError as e:
        raise StripePaymentError(str(e), code="stripe_error", stripe_error=e) from e


def confirm_payment_intent(payment_intent_id: str,
                           payment_method_id: Optional[str] = None) -> PaymentResult:
    client = get_stripe_client()
    payload = {}
    if payment_method_id:
        payload["payment_method"] = payment_method_id
    try:
        intent = client.PaymentIntent.confirm(payment_intent_id, **payload)
        return _build_result(intent)
    except stripe.error.CardError as e:
        _raise_card_error(e)
    except stripe.error.InvalidRequestError as e:
        raise PaymentIntentError(str(e), code="invalid_request", stripe_error=e) from e
    except stripe.error.StripeError as e:
        raise StripePaymentError(str(e), code="stripe_error", stripe_error=e) from e


def charge_customer(customer_id: str, payment_method_id: str, amount: int, currency: str,
                    description: Optional[str] = None, metadata: Optional[dict] = None) -> PaymentResult:
    return create_payment_intent(amount=amount, currency=currency, customer_id=customer_id,
                                 payment_method_id=payment_method_id, description=description,
                                 metadata=metadata, confirm=True)


def retrieve_payment_intent(payment_intent_id: str) -> PaymentResult:
    client = get_stripe_client()
    try:
        intent = client.PaymentIntent.retrieve(payment_intent_id)
        return _build_result(intent)
    except stripe.error.InvalidRequestError as e:
        raise PaymentIntentError(str(e), code="invalid_request", stripe_error=e) from e
    except stripe.error.StripeError as e:
        raise StripePaymentError(str(e), code="stripe_error", stripe_error=e) from e


def cancel_payment_intent(payment_intent_id: str) -> PaymentResult:
    client = get_stripe_client()
    try:
        intent = client.PaymentIntent.cancel(payment_intent_id)
        return _build_result(intent)
    except stripe.error.InvalidRequestError as e:
        raise PaymentIntentError(str(e), code="invalid_request", stripe_error=e) from e
    except stripe.error.StripeError as e:
        raise StripePaymentError(str(e), code="stripe_error", stripe_error=e) from e


def refund_payment(payment_intent_id: str, amount: Optional[int] = None,
                   reason: Optional[str] = None) -> RefundResult:
    client = get_stripe_client()
    payload: dict = {"payment_intent": payment_intent_id}
    if amount is not None:
        payload["amount"] = amount
    if reason:
        payload["reason"] = reason
    try:
        refund = client.Refund.create(**payload)
        return RefundResult(refund_id=refund.id, payment_intent_id=payment_intent_id,
                            amount=refund.amount, currency=refund.currency, status=refund.status)
    except stripe.error.InvalidRequestError as e:
        raise PaymentIntentError(str(e), code="invalid_request", stripe_error=e) from e
    except stripe.error.StripeError as e:
        raise StripePaymentError(str(e), code="stripe_error", stripe_error=e) from e


def _build_result(intent) -> PaymentResult:
    return PaymentResult(
        payment_intent_id=intent.id, status=PaymentStatus(intent.status),
        amount=intent.amount, currency=intent.currency, customer_id=intent.customer,
        payment_method_id=intent.payment_method, client_secret=intent.client_secret,
        metadata=intent.metadata.to_dict() if intent.metadata else {},
    )


def _raise_card_error(e: stripe.error.CardError) -> None:
    code = e.code
    msg = e.user_message or str(e)
    if code == "card_declined":
        decline_code = e.error.get("decline_code", "")
        if decline_code == "insufficient_funds":
            raise InsufficientFundsError(msg, code=code, stripe_error=e) from e
        raise CardDeclinedError(msg, code=code, stripe_error=e) from e
    if code in ("invalid_number", "invalid_expiry_month", "invalid_expiry_year",
                "invalid_cvc", "expired_card", "incorrect_number", "incorrect_cvc"):
        raise InvalidCardError(msg, code=code, stripe_error=e) from e
    raise StripePaymentError(msg, code=code, stripe_error=e) from e
