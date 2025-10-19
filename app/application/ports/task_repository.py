from abc import ABC, abstractmethod
from app.domain.entities.task import Task


class ITaskRepository(ABC):
    @abstractmethod
    async def add(self, task: Task) -> None: ...

    @abstractmethod
    async def list(self) -> list[Task]: ...
