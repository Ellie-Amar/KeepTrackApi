from typing import List, Tuple
from uuid import UUID

from app.application.ports.task_repository import ITaskRepository
from app.domain.entities.task import Task


class TaskRepositoryInMemory(ITaskRepository):
    """In-memory task repository for testing."""

    def __init__(self) -> None:
        self._tasks: List[Task] = []
        self._tasks_users: List[Tuple[UUID, UUID]] = []

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
