from __future__ import annotations
from pydantic import EmailStr, Field
from uuid import UUID

from app.interfaces.view_models.base_view_model import ViewModel


class UserCreate(ViewModel):
    email: EmailStr
    password: str = Field(min_length=8)
    display_name: str | None = None


class UserRead(ViewModel):
    id: UUID
    email: EmailStr
    display_name: str | None = None
    is_active: bool
    email_verified: bool
