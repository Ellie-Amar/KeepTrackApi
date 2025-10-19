from __future__ import annotations

async def clear_tasks() -> None:
    """Delete all rows from tasks table (async)."""
    # Lazy imports to avoid touching DB settings during test collection
    from sqlalchemy import delete  # type: ignore
    from app.infrastructure.db.session import SessionLocal  # type: ignore
    from app.infrastructure.db.models import TaskORM  # type: ignore

    async with SessionLocal() as session:
        await session.execute(delete(TaskORM))
        await session.commit()
