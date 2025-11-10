from __future__ import annotations
from pydantic import BaseModel
from uuid import UUID


class ListTasksCommand(BaseModel):
    user_id: UUID
