from slowapi import Limiter
from slowapi.util import get_remote_address
from app.config.settings import settings

# IP-based limits. Works behind Render thanks to proxy headers middleware.
limiter = Limiter(
    key_func=get_remote_address,
    headers_enabled=False,
    enabled=settings.app_env.lower() != "test",
)
