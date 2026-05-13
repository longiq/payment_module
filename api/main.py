import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from api.exception_handlers import EXCEPTION_HANDLERS
from api.routers import customers, payments, webhooks
from stripe_payment.client import init_stripe

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    secret_key = os.getenv("STRIPE_SECRET_KEY")
    if not secret_key:
        raise RuntimeError("STRIPE_SECRET_KEY environment variable is not set.")
    init_stripe(secret_key)
    yield


app = FastAPI(
    title="Payment API",
    description="Stripe payment processing API",
    version="1.0.0",
    lifespan=lifespan,
)

for exc_class, handler in EXCEPTION_HANDLERS.items():
    app.add_exception_handler(exc_class, handler)

app.include_router(customers.router)
app.include_router(payments.router)
app.include_router(webhooks.router)
