import pytest
from app.application.commands.list_task_assignees_command import (
    ListTaskAssigneesCommand,
)
from app.application.usecases.task.list_task_assignees_usecase import (
    ListTaskAssignees,
)
from app.domain.entities.task import Task
from app.domain.entities.user import User
from app.infrastructure.repositories.in_memory.task_repository import (
    TaskRepositoryInMemory,
)
from app.infrastructure.repositories.in_memory.user_repository import (
    UserRepositoryInMemory,
)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_task_assignees_returns_users_ok():
    user_repo = UserRepositoryInMemory()
    task_repo = TaskRepositoryInMemory()

    owner = User.new(email="owner@example.com", password_hash="x")
    other = User.new(email="other@example.com", password_hash="x")
    await user_repo.add(owner)
    await user_repo.add(other)

    task = Task.new(owner_id=owner.id, label="demo")
    await task_repo.add(task)
    await task_repo.add_assignee(task.id, other.id)

    uc = ListTaskAssignees(task_repo, user_repo)
    result = await uc.execute(ListTaskAssigneesCommand(task_id=task.id))

    ids = {u.id for u in result}
    assert ids == {owner.id, other.id}
