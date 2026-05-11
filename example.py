"""
Stripe Payment Module - Usage Examples
Run: STRIPE_SECRET_KEY=sk_test_... python example.py

Test cards:
    Success:            4242 4242 4242 4242
    Card declined:      4000 0000 0000 0002
    Insufficient funds: 4000 0000 0000 9995
"""
import os
from stripe_payment import (init_stripe, create_customer, attach_payment_method,
                            create_payment_intent, charge_customer, refund_payment, delete_customer)
from stripe_payment.models import CustomerData, CardDetails, Address, Currency
from stripe_payment.exceptions import CardDeclinedError, InsufficientFundsError, StripePaymentError


def main():
    init_stripe(os.getenv("STRIPE_SECRET_KEY"))

    # Tạo customer
    customer = create_customer(CustomerData(
        email="nguyen.van.a@example.com", name="Nguyen Van A", phone="+84901234567",
        address=Address(line1="123 Nguyen Hue", city="Ho Chi Minh City", country="VN"),
        metadata={"user_id": "usr_001"},
    ))
    print(f"Customer: {customer.customer_id}")

    # Gắn thẻ
    result = attach_payment_method(customer.customer_id,
        CardDetails(number="4242424242424242", exp_month=12, exp_year=2026, cvc="123"))
    print(f"Payment method: {result.payment_method_id}")

    # Charge tiền
    try:
        payment = charge_customer(
            customer_id=customer.customer_id, payment_method_id=result.payment_method_id,
            amount=150000, currency=Currency.USD, description="Premium plan - monthly",
        )
        print(f"Charged: {payment.amount_display} | Status: {payment.status.value}")

        # Refund
        refund = refund_payment(payment.payment_intent_id)
        print(f"Refunded: {refund.refund_id}")

    except CardDeclinedError as e:
        print(f"Card declined: {e}")
    except InsufficientFundsError as e:
        print(f"Insufficient funds: {e}")
    except StripePaymentError as e:
        print(f"Payment error [{e.code}]: {e}")

    # Cleanup
    delete_customer(customer.customer_id)


if __name__ == "__main__":
    main()
