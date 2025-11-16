from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UpdateTaskValidationCommand(BaseModel):
    validation_id: UUID
    task_id: UUID
    user_id: UUID
    note: Optional[str] = None
