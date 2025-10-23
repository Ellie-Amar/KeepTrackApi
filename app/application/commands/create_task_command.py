from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class CreateTaskCommand(BaseModel):
    user_id: UUID
    label: str
    category: Optional[str] = None
    note: Optional[str] = None
