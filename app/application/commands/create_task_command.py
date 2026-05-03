from pydantic import BaseModel
from uuid import UUID
from typing import Literal, Optional


class CreateTaskCommand(BaseModel):
    owner_id: UUID
    label: str
    category: Optional[str] = None
    note: Optional[str] = None
    status: Literal["active", "suspended", "done"] = "active"
    order: int = 0
