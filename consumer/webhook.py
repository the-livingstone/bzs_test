import logging

import httpx
from tenacity import before_sleep_log, retry, stop_after_attempt, wait_exponential, RetryCallState

logger = logging.getLogger(__name__)
MAX_ATTEMPTS = 3


class WebhookError(Exception):
    def __init__(self, message: str = ""):
        self.message = message

def log_exception(retry_state: RetryCallState):
    logger.error(
        "Webhook failed after %s attempts for %s: %s",
        MAX_ATTEMPTS,
        retry_state.kwargs.get("url"),
        retry_state.outcome.exception(),
    )
    raise WebhookError(retry_state.outcome.exception())

@retry(
    stop=stop_after_attempt(MAX_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=1),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    retry_error_callback=log_exception,
)
async def send_webhook(url: str, payload: dict) -> None:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
