from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.session import Base

from ._utils import utcnow
from .tasks_users import tasks_users

if TYPE_CHECKING:
    from .task_validation import TaskValidationORM
    from .user import UserORM


class TaskORM(Base):
    """SQLAlchemy ORM model for the tasks table."""

    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    label: Mapped[str] = mapped_column(Text, nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="active")
    order: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )

    participants: Mapped[list["UserORM"]] = relationship(
        "UserORM",
        secondary=tasks_users,
        lazy="selectin",
        uselist=True,
    )

    validations: Mapped[list["TaskValidationORM"]] = relationship(
        "TaskValidationORM",
        back_populates="task",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
