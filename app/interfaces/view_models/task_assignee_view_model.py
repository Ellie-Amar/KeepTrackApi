from pydantic import EmailStr, Field

from app.interfaces.view_models.base_view_model import ViewModel


class TaskAssigneesCreate(ViewModel):
    user_emails: list[EmailStr] = Field(min_length=1)
