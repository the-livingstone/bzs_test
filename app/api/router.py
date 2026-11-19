from fastapi import APIRouter

from app.api import payments

api_router = APIRouter(prefix="/api")
api_router.include_router(payments.router)
