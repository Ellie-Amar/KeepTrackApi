from collections import defaultdict
from typing import List, Tuple, TYPE_CHECKING
from uuid import UUID

from app.application.ports.task_repository import ITaskRepository
from app.domain.entities.task import Task, TaskWithValidations
from app.domain.entities.task_validation import TaskValidation

if TYPE_CHECKING:
    from app.infrastructure.repositories.in_memory.task_validation_repository import (
        TaskValidationRepositoryInMemory,
    )


class TaskRepositoryInMemory(ITaskRepository):
    """In-memory task repository for testing."""

    def __init__(
        self,
        validation_repo: "TaskValidationRepositoryInMemory | None" = None,
    ) -> None:
        self._tasks: List[Task] = []
        self._tasks_users: List[Tuple[UUID, UUID]] = []
        self._validation_repo = validation_repo

    async def add(self, task: Task) -> None:
        """Add a task and ensure owner ∈ participants."""
        self._tasks.append(task)
        self._tasks_users.append((task.id, task.owner_id))

    async def list(self) -> List[Task]:
        """Return all stored tasks."""
        return list(self._tasks)

    async def clear(self) -> None:
        """Remove all tasks and participants."""
        self._tasks.clear()
        self._tasks_users.clear()

    async def get(self, task_id: UUID) -> Task | None:
        """Find a task by id."""
        for t in self._tasks:
            if t.id == task_id:
                return t
        return None

    async def update(self, task: Task) -> Task:
        """Update a task in memory (simple replacement)."""
        for i, t in enumerate(self._tasks):
            if t.id == task.id:
                self._tasks[i] = task
                return task
        return task

    async def delete(self, task_id: UUID) -> None:
        """Delete a task and its participants."""
        self._tasks = [t for t in self._tasks if t.id != task_id]
        self._tasks_users = [
            (tid, uid) for tid, uid in self._tasks_users if tid != task_id
        ]

    async def list_by_user(self, user_id: UUID) -> List[Task]:
        """Return all tasks where the user is a participant."""
        task_ids = [tid for tid, uid in self._tasks_users if uid == user_id]
        return [t for t in self._tasks if t.id in task_ids]

    async def list_assignees(self, task_id: UUID) -> List[UUID]:
        """Return user ids assigned to the task."""
        return [uid for tid, uid in self._tasks_users if tid == task_id]

    async def add_assignee(self, task_id: UUID, user_id: UUID) -> None:
        """Link a user to a task."""
        self._tasks_users.append((task_id, user_id))

    async def remove_assignee(self, task_id: UUID, user_id: UUID) -> None:
        """Remove a user from a task."""
        self._tasks_users = [
            (tid, uid)
            for tid, uid in self._tasks_users
            if not (tid == task_id and uid == user_id)
        ]

    async def list_with_validations_by_user(
        self, user_id: UUID
    ) -> List[TaskWithValidations]:
        """Return tasks with associated validations if a repo is attached."""
        tasks = await self.list_by_user(user_id)
        validation_map: defaultdict[UUID, list[TaskValidation]] = defaultdict(list)
        if self._validation_repo is not None:
            validations = await self._validation_repo.list_by_tasks(
                [task.id for task in tasks]
            )
            for validation in validations:
                validation_map[validation.task_id].append(validation)

        return [
            TaskWithValidations(
                task=task, validations=list(validation_map.get(task.id, []))
            )
            for task in tasks
        ]

    async def get_with_validations(self, task_id: UUID) -> TaskWithValidations | None:
        """Return a single task with associated validations if available."""
        task = await self.get(task_id)
        if task is None:
            return None
        validations: list[TaskValidation] = []
        if self._validation_repo is not None:
            validations = await self._validation_repo.list_by_task(task_id)
        return TaskWithValidations(task=task, validations=validations)
