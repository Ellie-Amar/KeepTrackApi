from __future__ import annotations
import os
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from app.config.settings import settings


class Base(DeclarativeBase):
    """Declarative base for ORM models."""

    pass


# Read once at import, do NOT raise if missing (lazy initialization)
DATABASE_URL = settings.database_url

# Normalize driver to asyncpg if a sync-style URL is provided
if (
    DATABASE_URL
    and DATABASE_URL.startswith("postgresql://")
    and "+asyncpg" not in DATABASE_URL
):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Enable NullPool only when tests ask for it (local tests, CI)
USE_NULLPOOL = os.getenv("SQLA_NULLPOOL") == "1"

# Lazily initialized engine/sessionmaker
_engine: AsyncEngine | None = None


def _init_engine_if_needed() -> None:
    """Create engine and sessionmaker on first real DB usage."""
    global _engine, SessionLocal
    if _engine is not None:
        return
    if not DATABASE_URL:
        # Keep a clear runtime error if someone actually tries to use the DB without a URL
        raise RuntimeError("DATABASE_URL is not set")
    _engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        poolclass=NullPool if USE_NULLPOOL else None,  # keep default in dev/prod
    )
    SessionLocal = async_sessionmaker(
        bind=_engine, expire_on_commit=False, class_=AsyncSession
    )


class _UnconfiguredSessionmaker:
    """Callable placeholder that raises a clear error if DB is used without url."""

    def __call__(self, *args, **kwargs):
        # Initialize on demand if possible; else raise a clean error
        _init_engine_if_needed()
        # If init succeeded, the global SessionLocal was swapped to the real one
        return SessionLocal(*args, **kwargs)


SessionLocal = _UnconfiguredSessionmaker()
