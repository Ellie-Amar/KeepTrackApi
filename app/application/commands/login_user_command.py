from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field


class LoginUserCommand(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=1, description="User password")
