from __future__ import annotations

import dataclasses
from datetime import datetime, timezone

import pytest

from app.domain.entities.user import User
from app.domain.errors import ValidationError


def _base_user() -> User:
    return User.new(email="user@example.com", password_hash="hash")


@pytest.mark.unit
def test_new_user_normalizes_email_ok():
    user = User.new(email="  Foo@Example.Com  ", password_hash="hash")

    assert user.email == "foo@example.com"
    assert user.created_at.tzinfo is timezone.utc
    assert user.updated_at.tzinfo is timezone.utc


@pytest.mark.unit
def test_new_user_invalid_email_ko():
    with pytest.raises(ValidationError):
        User.new(email="invalid-email", password_hash="hash")


@pytest.mark.unit
def test_new_user_blank_password_hash_ko():
    with pytest.raises(ValidationError):
        User.new(email="user@example.com", password_hash=" ")


@pytest.mark.unit
def test_user_is_immutable_ko():
    user = _base_user()
    with pytest.raises(dataclasses.FrozenInstanceError):
        user.email = "other@example.com"  # type: ignore


@pytest.mark.unit
def test_with_display_name_trims_and_bumps_timestamp_ok():
    user = _base_user()
    updated = user.with_display_name("  Bob  ")

    assert updated.display_name == "Bob"
    assert updated.updated_at > user.updated_at


@pytest.mark.unit
def test_with_email_normalizes_and_bumps_timestamp_ok():
    user = _base_user()
    updated = user.with_email("  NEW@Example.Com ")

    assert updated.email == "new@example.com"
    assert updated.updated_at > user.updated_at


@pytest.mark.unit
def test_with_password_hash_updates_and_bumps_timestamp_ok():
    user = _base_user()
    updated = user.with_password_hash("newhash")

    assert updated.password_hash == "newhash"
    assert updated.updated_at > user.updated_at


@pytest.mark.unit
def test_deactivate_and_activate_toggle_flags_ok():
    user = _base_user()

    deactivated = user.deactivate()
    assert deactivated.is_active is False
    assert deactivated.updated_at > user.updated_at

    reactivated = deactivated.activate()
    assert reactivated.is_active is True
    assert reactivated.updated_at > deactivated.updated_at


@pytest.mark.unit
def test_activate_when_already_active_noop_ok():
    user = _base_user()
    assert user.activate() is user


@pytest.mark.unit
def test_deactivate_when_already_inactive_noop_ok():
    user = _base_user().deactivate()
    assert user.deactivate() is user
