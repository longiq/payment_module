import stripe
from .client import get_stripe_client
from .models import CardDetails, CustomerData, CustomerResult
from .exceptions import CardDeclinedError, InvalidCardError, CustomerNotFoundError, StripePaymentError


def create_customer(data: CustomerData) -> CustomerResult:
    client = get_stripe_client()
    payload = {"email": data.email, "metadata": data.metadata}
    if data.name:
        payload["name"] = data.name
    if data.phone:
        payload["phone"] = data.phone
    if data.address:
        addr = data.address
        payload["address"] = {
            "line1": addr.line1, "line2": addr.line2, "city": addr.city,
            "state": addr.state, "postal_code": addr.postal_code, "country": addr.country,
        }
    try:
        customer = client.Customer.create(**payload)
        return CustomerResult(
            customer_id=customer.id, email=customer.email,
            name=customer.name, metadata=customer.metadata.to_dict() if customer.metadata else {},
        )
    except stripe.error.InvalidRequestError as e:
        raise StripePaymentError(str(e), code="invalid_request", stripe_error=e) from e
    except stripe.error.StripeError as e:
        raise StripePaymentError(str(e), code="stripe_error", stripe_error=e) from e


def attach_payment_method(customer_id: str, card: CardDetails) -> CustomerResult:
    client = get_stripe_client()
    try:
        pm = client.PaymentMethod.create(
            type="card",
            card={"number": card.number, "exp_month": card.exp_month,
                  "exp_year": card.exp_year, "cvc": card.cvc},
            billing_details={"name": card.name} if card.name else {},
        )
        client.PaymentMethod.attach(pm.id, customer=customer_id)
        client.Customer.modify(customer_id, invoice_settings={"default_payment_method": pm.id})
        customer = client.Customer.retrieve(customer_id)
        return CustomerResult(
            customer_id=customer.id, email=customer.email,
            name=customer.name, payment_method_id=pm.id, metadata=customer.metadata.to_dict() if customer.metadata else {},
        )
    except stripe.error.CardError as e:
        _raise_card_error(e)
    except stripe.error.InvalidRequestError as e:
        if "No such customer" in str(e):
            raise CustomerNotFoundError(f"Customer '{customer_id}' not found.",
                                        code="customer_not_found", stripe_error=e) from e
        raise StripePaymentError(str(e), code="invalid_request", stripe_error=e) from e
    except stripe.error.StripeError as e:
        raise StripePaymentError(str(e), code="stripe_error", stripe_error=e) from e


def retrieve_customer(customer_id: str) -> CustomerResult:
    client = get_stripe_client()
    try:
        customer = client.Customer.retrieve(customer_id)
        if customer.get("deleted"):
            raise CustomerNotFoundError(f"Customer '{customer_id}' has been deleted.",
                                        code="customer_deleted")
        pm_id = None
        if customer.invoice_settings:
            pm_id = customer.invoice_settings.get("default_payment_method")
        return CustomerResult(
            customer_id=customer.id, email=customer.email,
            name=customer.name, payment_method_id=pm_id, metadata=customer.metadata.to_dict() if customer.metadata else {},
        )
    except stripe.error.InvalidRequestError as e:
        raise CustomerNotFoundError(f"Customer '{customer_id}' not found.",
                                    code="customer_not_found", stripe_error=e) from e
    except stripe.error.StripeError as e:
        raise StripePaymentError(str(e), code="stripe_error", stripe_error=e) from e


def delete_customer(customer_id: str) -> bool:
    client = get_stripe_client()
    try:
        result = client.Customer.delete(customer_id)
        return result.get("deleted", False)
    except stripe.error.InvalidRequestError as e:
        raise CustomerNotFoundError(f"Customer '{customer_id}' not found.",
                                    code="customer_not_found", stripe_error=e) from e
    except stripe.error.StripeError as e:
        raise StripePaymentError(str(e), code="stripe_error", stripe_error=e) from e


def _raise_card_error(e: stripe.error.CardError) -> None:
    code = e.code
    msg = e.user_message or str(e)
    if code == "card_declined":
        raise CardDeclinedError(msg, code=code, stripe_error=e) from e
    if code in ("invalid_number", "invalid_expiry_month", "invalid_expiry_year",
                "invalid_cvc", "expired_card", "incorrect_number", "incorrect_cvc"):
        raise InvalidCardError(msg, code=code, stripe_error=e) from e
    raise StripePaymentError(msg, code=code, stripe_error=e) from e
