from __future__ import annotations
from fastapi import FastAPI
from app.config.settings import settings
from app.interfaces.routes.task_routes import router as task_router
from app.interfaces.routes.user_routes import router as user_router
from app.interfaces.routes.auth_routes import router as auth_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
    )

    @app.get("/v1/health")
    async def health():
        return {"status": "ok"}

    app.include_router(task_router)
    app.include_router(user_router)
    app.include_router(auth_router)

    return app


app = create_app()
