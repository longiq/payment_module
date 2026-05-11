class StripePaymentError(Exception):
    def __init__(self, message: str, code: str = None, stripe_error=None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.stripe_error = stripe_error

    def __str__(self):
        return f"[{self.code}] {self.message}" if self.code else self.message

class CardDeclinedError(StripePaymentError):
    """Raised when a card is declined."""

class InvalidCardError(StripePaymentError):
    """Raised when card details are invalid (wrong number, expired, etc.)."""

class InsufficientFundsError(StripePaymentError):
    """Raised when the card has insufficient funds."""

class CustomerNotFoundError(StripePaymentError):
    """Raised when a Stripe customer ID does not exist."""

class PaymentIntentError(StripePaymentError):
    """Raised when creating or confirming a PaymentIntent fails."""

class ConfigurationError(StripePaymentError):
    """Raised when the Stripe client is not properly configured."""
