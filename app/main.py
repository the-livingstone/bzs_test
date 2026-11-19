import asyncio
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from app.api.router import api_router
from app.config import settings
from app.db.session import async_session_factory
from app.services.outbox_publisher import run_outbox_publisher_loop

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(_app: FastAPI):
    publisher_task = asyncio.create_task(run_outbox_publisher_loop(async_session_factory))
    yield
    publisher_task.cancel()
    try:
        await publisher_task
    except asyncio.CancelledError:
        pass

_docs_url = "/docs" if settings.debug else None
_redoc_url = "/redoc" if settings.debug else None
_openapi_url = "/openapi.json" if settings.debug else None

app = FastAPI(
    title="Payment Processing Service",
    docs_url=_docs_url,
    redoc_url=_redoc_url,
    openapi_url=_openapi_url,
)
app.include_router(api_router)
