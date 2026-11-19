from app.db.session import get_session
from app.services.payments import Payments

async def get_payments_service() -> Payments:
    session = get_session()
    return Payments(session)