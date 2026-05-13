from fastapi import APIRouter
from api.schemas import CardDetailsIn, CustomerCreateIn, CustomerOut
from stripe_payment.customer import (
    attach_payment_method,
    create_customer,
    delete_customer,
    retrieve_customer,
)
from stripe_payment.models import Address, CardDetails, CustomerData

router = APIRouter(prefix="/customers", tags=["customers"])


def _to_customer_out(result) -> CustomerOut:
    return CustomerOut(
        customer_id=result.customer_id,
        email=result.email,
        name=result.name,
        payment_method_id=result.payment_method_id,
        metadata=result.metadata,
    )


@router.post("", response_model=CustomerOut, status_code=201)
def create_customer_endpoint(body: CustomerCreateIn):
    address = None
    if body.address:
        a = body.address
        address = Address(
            line1=a.line1, city=a.city, country=a.country,
            line2=a.line2, postal_code=a.postal_code, state=a.state,
        )
    data = CustomerData(
        email=body.email, name=body.name, phone=body.phone,
        address=address, metadata=body.metadata,
    )
    return _to_customer_out(create_customer(data))


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer_endpoint(customer_id: str):
    return _to_customer_out(retrieve_customer(customer_id))


@router.delete("/{customer_id}", status_code=204)
def delete_customer_endpoint(customer_id: str):
    delete_customer(customer_id)


@router.post("/{customer_id}/payment-methods", response_model=CustomerOut)
def attach_payment_method_endpoint(customer_id: str, body: CardDetailsIn):
    card = CardDetails(
        number=body.number, exp_month=body.exp_month,
        exp_year=body.exp_year, cvc=body.cvc, name=body.name,
    )
    return _to_customer_out(attach_payment_method(customer_id, card))
