import pytest
from unittest.mock import patch, MagicMock
import stripe
from stripe_payment.customer import create_customer, attach_payment_method, retrieve_customer, delete_customer
from stripe_payment.models import CustomerData, CardDetails, Address
from stripe_payment.exceptions import CustomerNotFoundError, InvalidCardError, StripePaymentError


def _mock_customer(customer_id="cus_test123", email="test@example.com", name="Test User"):
    c = MagicMock()
    c.id = customer_id
    c.email = email
    c.name = name
    c.metadata = {}
    c.invoice_settings = MagicMock()
    c.invoice_settings.get = MagicMock(return_value=None)
    c.get = MagicMock(return_value=False)
    return c

def _mock_payment_method(pm_id="pm_test456"):
    pm = MagicMock()
    pm.id = pm_id
    return pm


class TestCreateCustomer:
    @patch("stripe_payment.customer.get_stripe_client")
    def test_success(self, mock_get_client):
        mock_stripe = MagicMock()
        mock_get_client.return_value = mock_stripe
        mock_stripe.Customer.create.return_value = _mock_customer()
        result = create_customer(CustomerData(email="test@example.com", name="Test User"))
        assert result.customer_id == "cus_test123"
        assert result.email == "test@example.com"

    @patch("stripe_payment.customer.get_stripe_client")
    def test_with_address(self, mock_get_client):
        mock_stripe = MagicMock()
        mock_get_client.return_value = mock_stripe
        mock_stripe.Customer.create.return_value = _mock_customer()
        create_customer(CustomerData(email="test@example.com",
                        address=Address(line1="123 Main St", city="Hanoi", country="VN")))
        call_kwargs = mock_stripe.Customer.create.call_args[1]
        assert call_kwargs["address"]["country"] == "VN"

    @patch("stripe_payment.customer.get_stripe_client")
    def test_stripe_error_raises(self, mock_get_client):
        mock_stripe = MagicMock()
        mock_get_client.return_value = mock_stripe
        mock_stripe.Customer.create.side_effect = stripe.error.StripeError("Network error")
        with pytest.raises(StripePaymentError):
            create_customer(CustomerData(email="test@example.com"))


class TestAttachPaymentMethod:
    @patch("stripe_payment.customer.get_stripe_client")
    def test_success(self, mock_get_client):
        mock_stripe = MagicMock()
        mock_get_client.return_value = mock_stripe
        mock_stripe.PaymentMethod.create.return_value = _mock_payment_method()
        mock_stripe.Customer.retrieve.return_value = _mock_customer()
        card = CardDetails(number="4242424242424242", exp_month=12, exp_year=2025, cvc="123")
        result = attach_payment_method("cus_test123", card)
        assert result.payment_method_id == "pm_test456"

    @patch("stripe_payment.customer.get_stripe_client")
    def test_invalid_card_raises(self, mock_get_client):
        mock_stripe = MagicMock()
        mock_get_client.return_value = mock_stripe
        mock_stripe.PaymentMethod.create.side_effect = stripe.error.CardError(
            "Your card's security code is invalid.", param="cvc", code="invalid_cvc")
        card = CardDetails(number="4242424242424242", exp_month=12, exp_year=2025, cvc="000")
        with pytest.raises(InvalidCardError):
            attach_payment_method("cus_test123", card)

    @patch("stripe_payment.customer.get_stripe_client")
    def test_customer_not_found_raises(self, mock_get_client):
        mock_stripe = MagicMock()
        mock_get_client.return_value = mock_stripe
        mock_stripe.PaymentMethod.create.return_value = _mock_payment_method()
        mock_stripe.PaymentMethod.attach.side_effect = stripe.error.InvalidRequestError(
            "No such customer: cus_bad", param="customer")
        card = CardDetails(number="4242424242424242", exp_month=12, exp_year=2025, cvc="123")
        with pytest.raises(CustomerNotFoundError):
            attach_payment_method("cus_bad", card)


class TestRetrieveCustomer:
    @patch("stripe_payment.customer.get_stripe_client")
    def test_success(self, mock_get_client):
        mock_stripe = MagicMock()
        mock_get_client.return_value = mock_stripe
        mock_stripe.Customer.retrieve.return_value = _mock_customer()
        assert retrieve_customer("cus_test123").customer_id == "cus_test123"

    @patch("stripe_payment.customer.get_stripe_client")
    def test_not_found_raises(self, mock_get_client):
        mock_stripe = MagicMock()
        mock_get_client.return_value = mock_stripe
        mock_stripe.Customer.retrieve.side_effect = stripe.error.InvalidRequestError(
            "No such customer", param="id")
        with pytest.raises(CustomerNotFoundError):
            retrieve_customer("cus_nonexistent")


class TestDeleteCustomer:
    @patch("stripe_payment.customer.get_stripe_client")
    def test_success(self, mock_get_client):
        mock_stripe = MagicMock()
        mock_get_client.return_value = mock_stripe
        mock_stripe.Customer.delete.return_value = {"deleted": True}
        assert delete_customer("cus_test123") is True

    @patch("stripe_payment.customer.get_stripe_client")
    def test_not_found_raises(self, mock_get_client):
        mock_stripe = MagicMock()
        mock_get_client.return_value = mock_stripe
        mock_stripe.Customer.delete.side_effect = stripe.error.InvalidRequestError(
            "No such customer", param="id")
        with pytest.raises(CustomerNotFoundError):
            delete_customer("cus_bad")
