from __future__ import annotations
from pydantic import BaseModel
from uuid import UUID


class GetTaskCommand(BaseModel):
    task_id: UUID
