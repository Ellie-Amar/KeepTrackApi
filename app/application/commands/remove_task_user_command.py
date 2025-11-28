from uuid import UUID

from pydantic import BaseModel


class RemoveTaskUserCommand(BaseModel):
    task_id: UUID
    requester_id: UUID
    user_id: UUID
