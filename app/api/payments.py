from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.schemas.payment import PaymentAcceptedResponse, PaymentCreate, PaymentDetailResponse

router = APIRouter(prefix="/payments")


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=PaymentAcceptedResponse,
)
async def create_payment(
    body: PaymentCreate,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> PaymentAcceptedResponse:
    if not idempotency_key or not idempotency_key.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Idempotency-Key header is required",
        )
    key = idempotency_key.strip()
    # check existing
    # in not create
    return PaymentAcceptedResponse()


@router.get(
    "/{payment_id}",
    response_model=PaymentDetailResponse,
)
async def get_payment(
    payment_id: UUID,
) -> PaymentDetailResponse:
    # get payment
    return PaymentDetailResponse()