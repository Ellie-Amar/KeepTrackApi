import dataclasses
import pytest
from uuid import uuid4
from datetime import datetime, timezone

from app.domain.entities.task import Task
from app.domain.errors import ValidationError


def test_create_defaults_ok():
    """test with minimal valid payload and default fields"""
    t = Task.new(user_id=uuid4(), label="Test")
    assert t.status == "active"
    assert t.order == 0
    assert t.created_at.tzinfo is timezone.utc
    assert t.updated_at.tzinfo is timezone.utc
    assert t.created_at <= t.updated_at


def test_label_is_normalized_ok():
    """test label normalization"""
    t = Task.new(user_id=uuid4(), label="  Read  ")
    assert t.label == "Read"


def test_empty_label_raises_ko():
    """test blank label"""
    with pytest.raises(ValidationError):
        Task.new(user_id=uuid4(), label="   ")


def test_negative_order_raises_ko():
    """test negative order"""
    with pytest.raises(ValidationError):
        now = datetime.now(timezone.utc)
        Task(
            id=uuid4(),
            user_id=uuid4(),
            label="X",
            order=-1,
            created_at=now,
            updated_at=now,
        )


def test_created_at_cannot_be_after_updated_at_ko():
    """test created_at updated_at consistency"""
    after = datetime(2025, 1, 1, tzinfo=timezone.utc)
    before = datetime(2024, 12, 31, tzinfo=timezone.utc)
    with pytest.raises(ValidationError):
        Task(
            id=uuid4(),
            user_id=uuid4(),
            label="X",
            created_at=after,
            updated_at=before,
        )


def test_entity_is_immutable_ko():
    """test frozen dataclass"""
    t = Task.new(user_id=uuid4(), label="X")
    with pytest.raises(dataclasses.FrozenInstanceError):
        t.label = "Y" # type: ignore
