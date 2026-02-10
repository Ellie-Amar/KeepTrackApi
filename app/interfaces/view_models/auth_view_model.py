from __future__ import annotations

from app.interfaces.view_models.base_view_model import ViewModel


class TokenResponse(ViewModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(ViewModel):
    refresh_token: str
