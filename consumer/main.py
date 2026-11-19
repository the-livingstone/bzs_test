import logging
import uuid
from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue
from consumer.config import settings
from consumer.handlers import process_payment_message
from consumer.session import async_session_factory


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAIN_QUEUE = "payments.new"

main_queue = RabbitQueue(
    MAIN_QUEUE,
    durable=True,
)

broker = RabbitBroker(settings.rabbitmq_url)
app = FastStream(broker)

@broker.subscriber(main_queue)
async def on_payment_new(message: dict):
    payment_id = uuid.UUID(message['payment_id'])
    try:
        async with async_session_factory() as session:
            await process_payment_message(session, payment_id)
    except Exception as e:
        logger.error(
            "Payment failed"
        )