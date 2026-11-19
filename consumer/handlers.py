import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment, PaymentStatus
from consumer.gateway import fake_payment_gateway
from consumer.webhook import send_webhook

logger = logging.getLogger(__name__)

async def process_payment_message(session: AsyncSession, payment_id: uuid.UUID):
    result = await session.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    if not payment:
        logger.error("Payment %s not found", payment_id)
        return
    if payment.status != PaymentStatus.pending:
        logger.info("Payment %s already processed (%s), skipping", payment_id, payment.status)
        return

    #do the thing
    success = await fake_payment_gateway()
    payment.status = PaymentStatus.succeeded if success else PaymentStatus.failed
    payment.processed_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(payment)
    payload = {
        "payment_id": str(payment.id),
        "status": payment.status.value,
        "amount": str(payment.amount),
        "currency": payment.currency.value,
        "processed_at": payment.processed_at.isoformat(),
    }

    await send_webhook(url=payment.webhook_url, payload=payload)
