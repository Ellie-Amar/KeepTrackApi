from __future__ import annotations
import dataclasses
from datetime import datetime, timezone
from app.application.ports.task_repository import ITaskRepository
from app.application.commands.update_task_command import UpdateTaskCommand
from app.domain.entities.task import Task


class UpdateTask:
    """Use case to partially update a task by its uuid.
    Note: domain entity remains unchanged; we use dataclasses.replace to build a new instance.
    """

    UPDATABLE_FIELDS = ("label", "note", "category", "status", "order")

    def __init__(self, repo: ITaskRepository) -> None:
        self.repo = repo

    async def execute(self, cmd: UpdateTaskCommand) -> Task | None:
        existing = await self.repo.get(cmd.id)
        if not existing:
            return None

        # detect and prepare update
        new_values = {}
        for field in self.UPDATABLE_FIELDS:
            val = getattr(cmd, field)
            if val is not None:
                new_values[field] = val

        if new_values:
            new_values["updated_at"] = datetime.now(timezone.utc)

        updated = (
            dataclasses.replace(existing, **new_values) if new_values else existing
        )

        await self.repo.update(updated)
        return updated
