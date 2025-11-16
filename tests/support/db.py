from sqlalchemy import delete

from app.infrastructure.db.models.task import TaskORM
from app.infrastructure.db.models.task_validation import TaskValidationORM
from app.infrastructure.db.models.user import UserORM
from app.infrastructure.db.session import SessionLocal


async def clear_tasks() -> None:
    async with SessionLocal() as session:
        await session.execute(delete(TaskValidationORM))
        await session.execute(delete(TaskORM))
        await session.commit()


async def clear_users() -> None:
    async with SessionLocal() as session:
        # order is important
        await session.execute(delete(TaskValidationORM))
        await session.execute(delete(TaskORM))
        await session.execute(delete(UserORM))
        await session.commit()
