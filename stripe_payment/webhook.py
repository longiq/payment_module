import os
import stripe
from .client import get_stripe_client
from .exceptions import StripePaymentError


def construct_webhook_event(payload: bytes, sig_header: str, secret: str = None) -> stripe.Event:
    get_stripe_client()
    endpoint_secret = secret or os.getenv("STRIPE_WEBHOOK_SECRET")
    if not endpoint_secret:
        raise StripePaymentError("Webhook secret is required.", code="missing_webhook_secret")
    try:
        return stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except stripe.error.SignatureVerificationError as e:
        raise StripePaymentError("Invalid webhook signature.",
                                 code="invalid_signature", stripe_error=e) from e
    except ValueError as e:
        raise StripePaymentError("Invalid webhook payload.", code="invalid_payload") from e


def handle_payment_intent_events(event: stripe.Event) -> dict:
    intent = event.data.object
    result = {
        "event_type": event.type, "payment_intent_id": intent.id,
        "status": intent.status, "amount": intent.amount, "currency": intent.currency,
        "customer_id": intent.customer, "metadata": dict(intent.metadata),
    }
    if event.type == "payment_intent.payment_failed":
        last_error = intent.last_payment_error
        result["error_message"] = last_error.message if last_error else "Unknown error"
        result["error_code"] = last_error.code if last_error else None
    return result
