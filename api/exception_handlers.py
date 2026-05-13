from fastapi import Request
from fastapi.responses import JSONResponse
from stripe_payment.exceptions import (
    CustomerNotFoundError,
    CardDeclinedError,
    InvalidCardError,
    InsufficientFundsError,
    PaymentIntentError,
    ConfigurationError,
    StripePaymentError,
)


def _error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


async def customer_not_found_handler(request: Request, exc: CustomerNotFoundError):
    return _error_response(404, exc.code or "customer_not_found", exc.message)


async def card_declined_handler(request: Request, exc: CardDeclinedError):
    return _error_response(402, exc.code or "card_declined", exc.message)


async def invalid_card_handler(request: Request, exc: InvalidCardError):
    return _error_response(422, exc.code or "invalid_card", exc.message)


async def insufficient_funds_handler(request: Request, exc: InsufficientFundsError):
    return _error_response(402, exc.code or "insufficient_funds", exc.message)


async def payment_intent_error_handler(request: Request, exc: PaymentIntentError):
    return _error_response(400, exc.code or "payment_intent_error", exc.message)


async def configuration_error_handler(request: Request, exc: ConfigurationError):
    return _error_response(500, exc.code or "configuration_error", exc.message)


async def stripe_payment_error_handler(request: Request, exc: StripePaymentError):
    return _error_response(400, exc.code or "stripe_error", exc.message)


EXCEPTION_HANDLERS = {
    CustomerNotFoundError: customer_not_found_handler,
    CardDeclinedError: card_declined_handler,
    InvalidCardError: invalid_card_handler,
    InsufficientFundsError: insufficient_funds_handler,
    PaymentIntentError: payment_intent_error_handler,
    ConfigurationError: configuration_error_handler,
    StripePaymentError: stripe_payment_error_handler,
}
