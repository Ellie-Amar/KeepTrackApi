# app/infrastructure/db/session.py
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


DATABASE_URL = settings.database_url
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")
if DATABASE_URL.startswith("postgresql://") and "+asyncpg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# enable NullPool only when tests ask for it.
USE_NULLPOOL = os.getenv("SQLA_NULLPOOL") == "1"

engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False,
    poolclass=NullPool if USE_NULLPOOL else None,  # keep default in dev/prod
)

SessionLocal = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)
