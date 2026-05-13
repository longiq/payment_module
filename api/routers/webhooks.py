from fastapi import APIRouter, Header, Request
from stripe_payment.webhook import construct_webhook_event, handle_payment_intent_events

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(..., alias="stripe-signature"),
):
    payload = await request.body()
    event = construct_webhook_event(payload, stripe_signature)
    result = handle_payment_intent_events(event)
    return {"received": True, "event": result}
