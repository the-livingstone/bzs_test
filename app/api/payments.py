from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.api.deps import get_payments_service
from app.schemas.payment import PaymentAcceptedResponse, PaymentCreate, PaymentDetailResponse
from app.services.payments import Payments

router = APIRouter(prefix="/payments")


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=PaymentAcceptedResponse,
)
async def create_payment(
    body: PaymentCreate,
    service: Annotated[Payments, Depends(get_payments_service)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> PaymentAcceptedResponse:
    if not idempotency_key or not idempotency_key.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Idempotency-Key header is required",
        )
    key = idempotency_key.strip()
    # check existing
    existing = await service.get_payment_by_idempotency_key(key)
    if existing:
        return PaymentAcceptedResponse(
            payment_id=existing.id,
            status=existing.status,
            created_at=existing.created_at,
        )
    # in not create
    created = await service.create_payment(body, key)
    return PaymentAcceptedResponse(
        payment_id=created.id,
        status=created.status,
        created_at=created.created_at,
    )


@router.get(
    "/{payment_id}",
    response_model=PaymentDetailResponse,
)
async def get_payment(
    payment_id: UUID,
    service: Annotated[Payments, Depends(get_payments_service)],
) -> PaymentDetailResponse:
    # get payment
    payment = await service.get_payment_by_id(payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="payment not found",
        )
    return PaymentDetailResponse(
        id=payment.id,
        amount=payment.amount,
        currency=payment.currency,
        description=payment.description,
        metadata=payment.metadata,
        status=payment.status,
        idempotency_key=payment.idempotency_key,
        webhook_url=payment.webhook_url,
        created_at=payment.created_at,
        processed_at=payment.processed_at,
    )