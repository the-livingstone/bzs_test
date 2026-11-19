import asyncio
import random


async def fake_payment_gateway() -> bool:
    # Emulate external gateway: 2–5 s delay, ~90% success
    await asyncio.sleep(random.uniform(2.0, 5.0))
    return random.random() < 0.9
