from sqlalchemy import delete
from app.infrastructure.db.models import TaskORM, UserORM
from app.infrastructure.db.session import SessionLocal


async def clear_tasks():
    async with SessionLocal() as session:
        await session.execute(delete(TaskORM))
        await session.commit()


async def clear_users():
    async with SessionLocal() as session:
        # tasks depend on users via FK; delete tasks first to avoid violations
        await session.execute(delete(TaskORM))
        await session.execute(delete(UserORM))
        await session.commit()
