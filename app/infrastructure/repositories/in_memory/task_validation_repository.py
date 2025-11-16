from __future__ import annotations

from collections.abc import Iterable
from typing import List
from uuid import UUID

from app.application.ports.task_validation_repository import ITaskValidationRepository
from app.domain.entities.task_validation import TaskValidation


class TaskValidationRepositoryInMemory(ITaskValidationRepository):
    """In-memory repository for task validations (tests)."""

    def __init__(self) -> None:
        self._validations: List[TaskValidation] = []

    async def add(self, validation: TaskValidation) -> TaskValidation:
        self._validations.append(validation)
        return validation

    async def get(self, validation_id: UUID) -> TaskValidation | None:
        for item in self._validations:
            if item.id == validation_id:
                return item
        return None

    async def list_by_task(self, task_id: UUID) -> list[TaskValidation]:
        return [item for item in self._validations if item.task_id == task_id]

    async def list_by_tasks(self, task_ids: Iterable[UUID]) -> list[TaskValidation]:
        ids = set(task_ids)
        if not ids:
            return []
        return [item for item in self._validations if item.task_id in ids]

    async def update(self, validation: TaskValidation) -> TaskValidation:
        for index, item in enumerate(self._validations):
            if item.id == validation.id:
                self._validations[index] = validation
                break
        return validation

    async def delete(self, validation_id: UUID) -> None:
        self._validations = [
            item for item in self._validations if item.id != validation_id
        ]
