import logging
import uuid
from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue, RabbitExchange
from faststream.rabbit.schemas.exchange import ExchangeType
from tenacity import RetryCallState, before_sleep_log, retry, stop_after_attempt, wait_exponential
from consumer.config import settings
from consumer.handlers import process_payment_message
from consumer.session import async_session_factory


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAIN_QUEUE = "payments.new"
DLX_NAME = "payments.dlx"
DLQ_NAME = "payments.new.dlq"

MAX_PROCESS_ATTEMPTS = 3

dlx = RabbitExchange(DLX_NAME, type=ExchangeType.DIRECT, durable=True)
dlq = RabbitQueue(DLQ_NAME, durable=True)


main_queue = RabbitQueue(
    MAIN_QUEUE,
    durable=True,
    arguments={
        "x-dead-letter-exchange": DLX_NAME,
        "x-dead-letter-routing-key": DLQ_NAME,
    },
)

broker = RabbitBroker(settings.rabbitmq_url)
app = FastStream(broker)

async def handle_final_retry(retry_state: RetryCallState):
    logger.error(
        "Payment %s failed after %s attempts, routing to DLQ: %s",
        retry_state.kwargs.get('message', {}).get('payment_id', 'UNKNOWN'),
        MAX_PROCESS_ATTEMPTS,
        retry_state.outcome.exception(),
    )
    await broker.publish(retry_state.kwargs.get('message', {}), exchange=dlx, routing_key=DLQ_NAME)


@broker.subscriber(main_queue)
@retry(
    stop=stop_after_attempt(MAX_PROCESS_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=1),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    retry_error_callback=handle_final_retry,
)
async def on_payment_new(message: dict):
    payment_id = uuid.UUID(message['payment_id'])
    async with async_session_factory() as session:
        await process_payment_message(session, payment_id)

@broker.subscriber(dlq, exchange=dlx)
async def on_dead_letter(message: dict) -> None:
    logger.error("Message in DLQ: %s", message)
