import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment, PaymentStatus
from app.schemas.payment import PaymentCreate


class Payments:
    PAYMENTS_NEW_EVENT = "payments.new"

    def __init__(self, session: AsyncSession):
        self.session = session



    async def get_payment_by_id(self, payment_id: uuid.UUID) -> Payment | None:
        result = await self.session.execute(select(Payment).where(Payment.id == payment_id))
        return result.scalar_one_or_none()


    async def get_payment_by_idempotency_key(self, key: str) -> Payment | None:
        result = await self.session.execute(select(Payment).where(Payment.idempotency_key == key))
        return result.scalar_one_or_none()


    async def create_payment(
        self,
        body: PaymentCreate,
        idempotency_key: str,
    ) -> Payment:
        payment = Payment(
            amount=body.amount,
            currency=body.currency,
            description=body.description,
            metadata_=body.metadata,
            webhook_url=str(body.webhook_url),
            idempotency_key=idempotency_key,
            status=PaymentStatus.pending,
        )
        self.session.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)
        return payment
