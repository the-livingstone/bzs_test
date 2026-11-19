from typing import Annotated
from app.config import settings

from fastapi import HTTPException, Header, status
from app.db.session import get_session
from app.services.payments import Payments

async def get_payments_service() -> Payments:
    session = get_session()
    return Payments(session)

async def verify_api_key(x_api_key: Annotated[str | None, Header()] = None) -> None:
    if not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")
