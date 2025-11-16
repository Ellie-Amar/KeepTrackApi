from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CreateTaskValidationCommand(BaseModel):
    task_id: UUID
    user_id: UUID
    note: Optional[str] = None
