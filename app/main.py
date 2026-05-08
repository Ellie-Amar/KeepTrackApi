from __future__ import annotations
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.config.settings import settings
from app.interfaces.rate_limit import limiter
from app.interfaces.routes.task_routes import router as task_router
from app.interfaces.routes.user_routes import router as user_router
from app.interfaces.routes.auth_routes import router as auth_router
from app.interfaces.routes.task_validation_routes import (
    router as task_validation_router,
)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
    )
    app.state.limiter = limiter

    def _rate_limit_handler(request: Request, exc: Exception) -> Response:
        return _rate_limit_exceeded_handler(request, exc)  # type: ignore[arg-type]

    app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)

    @app.get("/v1/health")
    async def health():
        return {"status": "ok"}

    app.include_router(task_router)
    app.include_router(task_validation_router)
    app.include_router(user_router)
    app.include_router(auth_router)

    return app


app = create_app()
