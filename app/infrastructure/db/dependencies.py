from typing import AsyncGenerator
from app.infrastructure.db.session import SessionLocal


async def get_db() -> AsyncGenerator:
    async with SessionLocal() as session:
        yield session
