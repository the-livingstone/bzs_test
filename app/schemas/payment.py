from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.models.payment import Currency, PaymentStatus


class PaymentCreate(BaseModel):
    amount: Decimal = Field(gt=0)
    currency: Currency
    description: str | None = None
    metadata: dict | None = None
    webhook_url: HttpUrl


class PaymentAcceptedResponse(BaseModel):
    payment_id: UUID
    status: PaymentStatus
    created_at: datetime


class PaymentDetailResponse(BaseModel):
    id: UUID
    amount: Decimal
    currency: Currency
    description: str | None
    metadata: dict | None = None
    status: PaymentStatus
    idempotency_key: str
    webhook_url: str
    created_at: datetime
    processed_at: datetime | None
