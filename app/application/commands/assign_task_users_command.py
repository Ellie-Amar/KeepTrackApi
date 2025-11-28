from uuid import UUID
from typing import List

from pydantic import BaseModel, EmailStr, Field


class AssignTaskUsersCommand(BaseModel):
    task_id: UUID
    requester_id: UUID
    user_emails: List[EmailStr] = Field(min_length=1)
