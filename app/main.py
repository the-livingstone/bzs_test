import logging

from fastapi import FastAPI

from app.api.router import api_router
from app.config import settings

logging.basicConfig(level=logging.INFO)

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
