# app/application/commands/update_task_command.py
from __future__ import annotations
from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class UpdateTaskCommand(BaseModel):
    id: UUID
    label: Optional[str] = None
    note: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    order: Optional[int] = None
