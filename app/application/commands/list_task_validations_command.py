from uuid import UUID

from pydantic import BaseModel


class ListTaskValidationsCommand(BaseModel):
    task_id: UUID
