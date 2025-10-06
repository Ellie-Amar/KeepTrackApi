from fastapi import FastAPI
from app.config.settings import settings

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
    )

    @app.get("/v1/health")
    async def health():
        return {"status": "ok"}

    return app

app = create_app()
