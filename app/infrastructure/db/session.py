from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
import os


class Base(DeclarativeBase):
    """Declarative base for ORM models."""
    pass


def get_database_url() -> str:
    """Read DATABASE_URL from var envs"""
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    return url

engine: AsyncEngine = create_async_engine(
    get_database_url(),
    echo=False,  # true for logs
    pool_pre_ping=True,  # reconnect automatically if needed
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
