from typing import List
from uuid import UUID
from app.application.ports.task_repository import ITaskRepository
from app.domain.entities.task import Task


class TaskRepositoryInMemory(ITaskRepository):
    """In-memory task repository for testing"""

    def __init__(self) -> None:
        self._tasks: List[Task] = []

    async def add(self, task: Task) -> None:
        self._tasks.append(task)

    async def list(self) -> List[Task]:
        return list(self._tasks)

    async def clear(self) -> None:
        self._tasks.clear()

    async def get(self, task_id: UUID) -> Task | None:
        for t in self._tasks:
            if t.id == task_id:
                return t
        return None

    async def update(self, task: Task) -> Task:
        for i, t in enumerate(self._tasks):
            if t.id == task.id:
                self._tasks[i] = task
                return task
        return task

    async def delete(self, task_id: UUID) -> None:
        for idx, t in enumerate(self._tasks):
            if t.id == task_id:
                del self._tasks[idx]
                return
