import pytest

from app.application.commands.assign_task_users_command import (
    AssignTaskUsersCommand,
)
from app.application.commands.list_task_assignees_command import (
    ListTaskAssigneesCommand,
)
from app.application.usecases.task.assign_task_users_usecase import AssignTaskUsers
from app.application.usecases.task.list_task_assignees_usecase import (
    ListTaskAssignees,
)
from app.domain.entities.task import Task
from app.domain.entities.user import User
from app.domain.errors import ValidationError
from app.infrastructure.repositories.in_memory.task_repository import (
    TaskRepositoryInMemory,
)
from app.infrastructure.repositories.in_memory.user_repository import (
    UserRepositoryInMemory,
)


def _user(email: str) -> User:
    return User.new(email=email, password_hash="x")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_assign_task_users_ok():
    repo = TaskRepositoryInMemory()
    user_repo = UserRepositoryInMemory()
    owner = _user("owner@example.com")
    u1 = _user("a@example.com")
    u2 = _user("b@example.com")
    await user_repo.add(owner)
    await user_repo.add(u1)
    await user_repo.add(u2)
    task = Task.new(owner_id=owner.id, label="demo")
    await repo.add(task)

    uc = AssignTaskUsers(repo, user_repo)
    cmd = AssignTaskUsersCommand(
        task_id=task.id,
        requester_id=owner.id,
        user_emails=[u1.email, u2.email],
    )
    users = await uc.execute(cmd)
    assert users is not None

    assert [u.id for u in users] == [u1.id, u2.id]
    list_uc = ListTaskAssignees(repo, user_repo)
    assignees = await list_uc.execute(ListTaskAssigneesCommand(task_id=task.id))
    assert {u.id for u in assignees} == {owner.id, u1.id, u2.id}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_assign_task_users_missing_email_ko():
    repo = TaskRepositoryInMemory()
    user_repo = UserRepositoryInMemory()
    owner = _user("owner@example.com")
    await user_repo.add(owner)
    task = Task.new(owner_id=owner.id, label="demo")
    await repo.add(task)

    uc = AssignTaskUsers(repo, user_repo)
    cmd = AssignTaskUsersCommand(
        task_id=task.id, requester_id=owner.id, user_emails=["missing@example.com"]
    )
    with pytest.raises(ValidationError):
        await uc.execute(cmd)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_assign_task_users_non_owner_ko():
    repo = TaskRepositoryInMemory()
    user_repo = UserRepositoryInMemory()
    owner = _user("owner@example.com")
    other = _user("other@example.com")
    target = _user("target@example.com")
    await user_repo.add(owner)
    await user_repo.add(other)
    await user_repo.add(target)
    task = Task.new(owner_id=owner.id, label="demo")
    await repo.add(task)

    uc = AssignTaskUsers(repo, user_repo)
    cmd = AssignTaskUsersCommand(
        task_id=task.id, requester_id=other.id, user_emails=[target.email]
    )
    with pytest.raises(ValidationError):
        await uc.execute(cmd)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_assign_task_users_owner_already_assigned_ko():
    repo = TaskRepositoryInMemory()
    user_repo = UserRepositoryInMemory()
    owner = _user("owner@example.com")
    await user_repo.add(owner)
    task = Task.new(owner_id=owner.id, label="demo")
    await repo.add(task)

    uc = AssignTaskUsers(repo, user_repo)
    cmd = AssignTaskUsersCommand(
        task_id=task.id, requester_id=owner.id, user_emails=[owner.email]
    )
    with pytest.raises(ValidationError):
        await uc.execute(cmd)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_assign_task_users_duplicate_emails_dedup_ok():
    repo = TaskRepositoryInMemory()
    user_repo = UserRepositoryInMemory()
    owner = _user("owner@example.com")
    target = _user("target@example.com")
    await user_repo.add(owner)
    await user_repo.add(target)
    task = Task.new(owner_id=owner.id, label="demo")
    await repo.add(task)

    uc = AssignTaskUsers(repo, user_repo)
    users = await uc.execute(
        AssignTaskUsersCommand(
            task_id=task.id,
            requester_id=owner.id,
            user_emails=[target.email, target.email.upper()],
        )
    )
    assert len(users or []) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_assign_task_users_already_assigned_ko():
    repo = TaskRepositoryInMemory()
    user_repo = UserRepositoryInMemory()
    owner = _user("owner@example.com")
    target = _user("target@example.com")
    await user_repo.add(owner)
    await user_repo.add(target)
    task = Task.new(owner_id=owner.id, label="demo")
    await repo.add(task)

    uc = AssignTaskUsers(repo, user_repo)
    cmd = AssignTaskUsersCommand(
        task_id=task.id, requester_id=owner.id, user_emails=[target.email]
    )
    await uc.execute(cmd)
    with pytest.raises(ValidationError):
        await uc.execute(cmd)
