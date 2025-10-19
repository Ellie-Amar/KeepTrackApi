from typing import AsyncGenerator

async def get_db() -> AsyncGenerator:
    from app.infrastructure.db.session import SessionLocal  # type: ignore
    async with SessionLocal() as session:
        yield session
