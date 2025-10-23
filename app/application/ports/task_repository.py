from abc import ABC, abstractmethod
from uuid import UUID
from app.domain.entities.task import Task


class ITaskRepository(ABC):
    @abstractmethod
    async def add(self, task: Task) -> None: ...

    @abstractmethod
    async def list(self) -> list[Task]: ...

    @abstractmethod
    async def get(self, task_id: UUID) -> Task | None: ...

    @abstractmethod
    async def update(self, task: Task) -> Task: ...

    @abstractmethod
    async def delete(self, task_id: UUID) -> None: ...
