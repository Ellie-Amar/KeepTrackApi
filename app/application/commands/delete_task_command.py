from __future__ import annotations
from pydantic import BaseModel
from uuid import UUID


class DeleteTaskCommand(BaseModel):
    task_id: UUID
