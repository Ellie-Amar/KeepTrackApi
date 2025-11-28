import pytest

from app.application.commands.remove_task_user_command import RemoveTaskUserCommand
from app.application.usecases.task.remove_task_user_usecase import RemoveTaskUser
from app.domain.entities.task import Task
from app.domain.entities.user import User
from app.domain.errors import ValidationError
from app.infrastructure.repositories.in_memory.task_repository import (
    TaskRepositoryInMemory,
)


def _user(email: str) -> User:
    return User.new(email=email, password_hash="x")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_remove_task_user_ok():
    repo = TaskRepositoryInMemory()
    owner = _user("owner@example.com")
    participant = _user("user@example.com")
    task = Task.new(owner_id=owner.id, label="demo")
    await repo.add(task)
    await repo.add_assignee(task.id, participant.id)

    uc = RemoveTaskUser(repo)
    cmd = RemoveTaskUserCommand(
        task_id=task.id, requester_id=owner.id, user_id=participant.id
    )
    assert await uc.execute(cmd) is True
    remaining = await repo.list_assignees(task.id)
    assert participant.id not in remaining


@pytest.mark.unit
@pytest.mark.asyncio
async def test_remove_task_user_owner_target_ko():
    repo = TaskRepositoryInMemory()
    owner = _user("owner@example.com")
    task = Task.new(owner_id=owner.id, label="demo")
    await repo.add(task)

    uc = RemoveTaskUser(repo)
    cmd = RemoveTaskUserCommand(
        task_id=task.id, requester_id=owner.id, user_id=owner.id
    )
    with pytest.raises(ValidationError):
        await uc.execute(cmd)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_remove_task_user_non_owner_ko():
    repo = TaskRepositoryInMemory()
    owner = _user("owner@example.com")
    participant = _user("user@example.com")
    task = Task.new(owner_id=owner.id, label="demo")
    await repo.add(task)
    await repo.add_assignee(task.id, participant.id)

    uc = RemoveTaskUser(repo)
    cmd = RemoveTaskUserCommand(
        task_id=task.id, requester_id=participant.id, user_id=owner.id
    )
    with pytest.raises(ValidationError):
        await uc.execute(cmd)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_remove_task_user_not_participant_ko():
    repo = TaskRepositoryInMemory()
    owner = _user("owner@example.com")
    task = Task.new(owner_id=owner.id, label="demo")
    await repo.add(task)

    uc = RemoveTaskUser(repo)
    missing_user_id = _user("x@example.com").id
    cmd = RemoveTaskUserCommand(
        task_id=task.id, requester_id=owner.id, user_id=missing_user_id
    )
    assert await uc.execute(cmd) is False
