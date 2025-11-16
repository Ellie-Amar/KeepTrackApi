from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.domain.entities.task_validation import TaskValidation


def _now() -> datetime:
    return datetime.now(timezone.utc)


@pytest.mark.unit
def test_task_validation_normalizes_note_ok():
    validation = TaskValidation.new(
        task_id=uuid4(),
        user_id=uuid4(),
        note="  done  ",
        user_display_name="Tester",
    )

    assert validation.note == "done"
    assert validation.user_display_name == "Tester"


@pytest.mark.unit
def test_task_validation_with_note_bumps_timestamp_ok():
    validation = TaskValidation.new(task_id=uuid4(), user_id=uuid4(), note="first")
    original_updated = validation.updated_at

    updated = validation.with_note("second")

    assert updated.note == "second"
    assert updated.updated_at > original_updated


@pytest.mark.unit
def test_task_validation_with_note_no_change_ok():
    validation = TaskValidation.new(task_id=uuid4(), user_id=uuid4(), note="same")

    updated = validation.with_note("same")

    assert updated is validation
