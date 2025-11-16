from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Self
from uuid import UUID

from app.domain.entities.base import BaseEntity


@dataclass(frozen=True, slots=True, kw_only=True)
class TaskValidation(BaseEntity):
    task_id: UUID
    user_id: UUID
    user_display_name: str | None = None
    note: str | None = None

    def __post_init__(self) -> None:
        BaseEntity.__post_init__(self)
        normalized_note = self._normalize_note(self.note)
        object.__setattr__(self, "note", normalized_note)

    def with_note(self, note: str | None) -> Self:
        normalized_note = self._normalize_note(note)
        if normalized_note == self.note:
            return self
        return dataclasses.replace(self, note=normalized_note).bump_updated_at()

    @staticmethod
    def _normalize_note(note: str | None) -> str | None:
        if note is None:
            return None
        trimmed = note.strip()
        return trimmed or None
