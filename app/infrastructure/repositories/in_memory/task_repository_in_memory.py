

from typing import List
from app.application.ports.task_repository import ITaskRepository
from app.domain.entities.task import Task


class TaskRepositoryInMemory(ITaskRepository):
    """In-memory task repository for testing"""

    def __init__(self) -> None:
        self._tasks: List[Task] = []

    async def add(self, task:Task) -> None:
        self._tasks.append(task)

    async def list(self) -> List[Task]:
        return list(self._tasks)

    async def clear(self) -> None:
        self._tasks.clear()