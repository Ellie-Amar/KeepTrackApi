from sqlalchemy import delete
from app.infrastructure.db.models import TaskORM
from app.infrastructure.db.session import SessionLocal

async def clear_tasks():
    async with SessionLocal() as session:
        await session.execute(delete(TaskORM))
        await session.commit()
