from __future__ import annotations
import os
import re
import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


def _sync_db_url_from_async(async_url: str | None) -> str | None:
    if not async_url:
        return None
    # postgresql+asyncpg://...  ->  postgresql://...
    return re.sub(r"\+asyncpg", "", async_url)


def pytest_runtest_setup(item):
    if "sql" in item.keywords:
        # 1) load .env for pytest
        load_dotenv(override=False)

        # 2) get URL
        async_url = os.getenv("DATABASE_URL")
        sync_url = _sync_db_url_from_async(async_url)
        if not sync_url:
            pytest.skip("Skipping SQL tests: DATABASE_URL not set")

        # 3) ping to confirm SQLAlchemy sync
        try:
            engine = create_engine(sync_url)
            with engine.connect() as conn:
                conn.execute(text("select 1"))
        except Exception as e:
            pytest.skip(f"Skipping SQL tests: DB not reachable ({e})")
