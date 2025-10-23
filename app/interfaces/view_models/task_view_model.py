from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel

class ViewModel(BaseModel):
    model_config = {
        "alias_generator": to_camel, # snake → camel
        "populate_by_name": True, # accepts snake_case inputs
        "from_attributes": True, # permits reading attributes
    }

class TaskCreate(ViewModel):
    user_id: UUID
    label: str = Field(..., min_length=1)
    note: str | None = None
    category: str | None = None


class TaskRead(ViewModel):
    id: UUID
    user_id: UUID
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
