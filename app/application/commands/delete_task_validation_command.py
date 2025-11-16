from uuid import UUID

from pydantic import BaseModel


class DeleteTaskValidationCommand(BaseModel):
    validation_id: UUID
    task_id: UUID
    user_id: UUID
