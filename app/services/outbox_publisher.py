import asyncio
import logging
from datetime import datetime, timezone

from faststream.rabbit import RabbitBroker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config import settings
from app.models.outbox import OutboxEvent

logger = logging.getLogger(__name__)


async def publish_pending_outbox(
    session_factory: async_sessionmaker[AsyncSession],
    broker: RabbitBroker,
) -> None:
    async with session_factory() as session:
        result = await session.execute(
            select(OutboxEvent)
            .where(OutboxEvent.published_at.is_(None))
            .order_by(OutboxEvent.created_at)
            .limit(50)
            .with_for_update(skip_locked=True)
        )
        events = result.scalars().all()
        for event in events:
            await broker.publish(event.payload, queue=event.event_type)
            event.published_at = datetime.now(timezone.utc)
        if events:
            await session.commit()
            logger.info("Published %s outbox event(s)", len(events))


async def run_outbox_publisher_loop(session_factory: async_sessionmaker[AsyncSession]) -> None:
    broker = RabbitBroker(settings.rabbitmq_url)
    await broker.connect()
    try:
        while True:
            try:
                await publish_pending_outbox(session_factory, broker)
            except Exception:
                logger.exception("Outbox publish iteration failed")
            await asyncio.sleep(settings.outbox_poll_interval_seconds)
    finally:
        await broker.close()
