from __future__ import annotations

from typing import Iterable, Protocol
from uuid import UUID

from app.domain.entities.task_validation import TaskValidation


class ITaskValidationRepository(Protocol):
    async def add(self, validation: TaskValidation) -> TaskValidation: ...

    async def get(self, validation_id: UUID) -> TaskValidation | None: ...

    async def list_by_task(self, task_id: UUID) -> list[TaskValidation]: ...

    async def list_by_tasks(self, task_ids: Iterable[UUID]) -> list[TaskValidation]: ...

    async def update(self, validation: TaskValidation) -> TaskValidation: ...

    async def delete(self, validation_id: UUID) -> None: ...
