import pytest
from unittest.mock import patch, MagicMock
import stripe
from stripe_payment.payment import (create_payment_intent, confirm_payment_intent,
                                    charge_customer, cancel_payment_intent, refund_payment)
from stripe_payment.models import PaymentStatus
from stripe_payment.exceptions import (CardDeclinedError, InsufficientFundsError,
                                       StripePaymentError)


def _mock_intent(intent_id="pi_test123", status="succeeded", amount=5000,
                 currency="usd", customer="cus_test123", payment_method="pm_test456"):
    intent = MagicMock()
    intent.id = intent_id
    intent.status = status
    intent.amount = amount
    intent.currency = currency
    intent.customer = customer
    intent.payment_method = payment_method
    intent.client_secret = f"{intent_id}_secret_abc"
    intent.metadata = {}
    return intent


class TestCreatePaymentIntent:
    @patch("stripe_payment.payment.get_stripe_client")
    def test_success(self, mock_get_client):
        mock_stripe = MagicMock()
        mock_get_client.return_value = mock_stripe
        mock_stripe.PaymentIntent.create.return_value = _mock_intent()
        result = create_payment_intent(amount=5000, currency="usd")
        assert result.payment_intent_id == "pi_test123"
        assert result.status == PaymentStatus.SUCCEEDED

    @patch("stripe_payment.payment.get_stripe_client")
    def test_amount_display_usd(self, mock_get_client):
        mock_stripe = MagicMock()
        mock_get_client.return_value = mock_stripe
        mock_stripe.PaymentIntent.create.return_value = _mock_intent(amount=5000, currency="usd")
        assert create_payment_intent(5000, "usd").amount_display == "50.00 USD"

    @patch("stripe_payment.payment.get_stripe_client")
    def test_amount_display_vnd(self, mock_get_client):
        mock_stripe = MagicMock()
        mock_get_client.return_value = mock_stripe
        mock_stripe.PaymentIntent.create.return_value = _mock_intent(amount=500000, currency="vnd")
        assert create_payment_intent(500000, "vnd").amount_display == "500000 VND"

    @patch("stripe_payment.payment.get_stripe_client")
    def test_card_declined_raises(self, mock_get_client):
        mock_stripe = MagicMock()
        mock_get_client.return_value = mock_stripe
        err = stripe.error.CardError("Your card was declined.", param=None, code="card_declined")
        err.error = MagicMock()
        err.error.get = MagicMock(return_value="generic_decline")
        mock_stripe.PaymentIntent.create.side_effect = err
        with pytest.raises(CardDeclinedError):
            create_payment_intent(5000, "usd")

    @patch("stripe_payment.payment.get_stripe_client")
    def test_insufficient_funds_raises(self, mock_get_client):
        mock_stripe = MagicMock()
        mock_get_client.return_value = mock_stripe
        err = stripe.error.CardError("Insufficient funds.", param=None, code="card_declined")
        err.error = MagicMock()
        err.error.get = MagicMock(return_value="insufficient_funds")
        mock_stripe.PaymentIntent.create.side_effect = err
        with pytest.raises(InsufficientFundsError):
            create_payment_intent(999999, "usd")

    @patch("stripe_payment.payment.get_stripe_client")
    def test_stripe_error_raises(self, mock_get_client):
        mock_stripe = MagicMock()
        mock_get_client.return_value = mock_stripe
        mock_stripe.PaymentIntent.create.side_effect = stripe.error.StripeError("API error")
        with pytest.raises(StripePaymentError):
            create_payment_intent(5000, "usd")


class TestConfirmPaymentIntent:
    @patch("stripe_payment.payment.get_stripe_client")
    def test_success(self, mock_get_client):
        mock_stripe = MagicMock()
        mock_get_client.return_value = mock_stripe
        mock_stripe.PaymentIntent.confirm.return_value = _mock_intent()
        result = confirm_payment_intent("pi_test123", payment_method_id="pm_test456")
        assert result.status == PaymentStatus.SUCCEEDED


class TestChargeCustomer:
    @patch("stripe_payment.payment.get_stripe_client")
    def test_success(self, mock_get_client):
        mock_stripe = MagicMock()
        mock_get_client.return_value = mock_stripe
        mock_stripe.PaymentIntent.create.return_value = _mock_intent()
        result = charge_customer("cus_test123", "pm_test456", 5000, "usd")
        assert result.status == PaymentStatus.SUCCEEDED
        assert mock_stripe.PaymentIntent.create.call_args[1]["confirm"] is True


class TestRefundPayment:
    @patch("stripe_payment.payment.get_stripe_client")
    def test_full_refund(self, mock_get_client):
        mock_stripe = MagicMock()
        mock_get_client.return_value = mock_stripe
        refund = MagicMock()
        refund.id = "re_test789"
        refund.amount = 5000
        refund.currency = "usd"
        refund.status = "succeeded"
        mock_stripe.Refund.create.return_value = refund
        result = refund_payment("pi_test123")
        assert result.refund_id == "re_test789"
        mock_stripe.Refund.create.assert_called_once_with(payment_intent="pi_test123")

    @patch("stripe_payment.payment.get_stripe_client")
    def test_partial_refund(self, mock_get_client):
        mock_stripe = MagicMock()
        mock_get_client.return_value = mock_stripe
        refund = MagicMock()
        refund.id = "re_partial"
        refund.amount = 2000
        refund.currency = "usd"
        refund.status = "succeeded"
        mock_stripe.Refund.create.return_value = refund
        result = refund_payment("pi_test123", amount=2000, reason="requested_by_customer")
        assert result.amount == 2000


class TestCancelPaymentIntent:
    @patch("stripe_payment.payment.get_stripe_client")
    def test_success(self, mock_get_client):
        mock_stripe = MagicMock()
        mock_get_client.return_value = mock_stripe
        mock_stripe.PaymentIntent.cancel.return_value = _mock_intent(status="canceled")
        result = cancel_payment_intent("pi_test123")
        assert result.status == PaymentStatus.CANCELED
