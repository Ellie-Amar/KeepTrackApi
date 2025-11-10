from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import Field

from app.interfaces.view_models.base_view_model import ViewModel


class TaskCreate(ViewModel):
    label: str = Field(..., min_length=1)
    note: str | None = None
    category: str | None = None
    order: int = 0


class TaskRead(ViewModel):
    id: UUID
    owner_id: UUID
    label: str
    note: str | None
    category: str | None
    status: str
    order: int | None
    created_at: datetime
    updated_at: datetime


class TaskUpdate(ViewModel):
    label: Optional[str] = Field(default=None, min_length=1)
    note: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    order: Optional[int] = None
