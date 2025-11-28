from uuid import UUID

from pydantic import BaseModel


class ListTaskAssigneesCommand(BaseModel):
    task_id: UUID
