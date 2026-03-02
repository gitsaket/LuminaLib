# 1. Override DATABASE_URL so session.py doesn't try to connect to PostgreSQL.
# 2. Patch JSONB → JSON so SQLite can handle the UserPreferences table.
import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

import sqlalchemy.dialects.postgresql as _pg
from sqlalchemy import JSON as _JSON

_pg.JSONB = _JSON  # type

# Standard imports
import pytest
from collections.abc import AsyncGenerator

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

# Now it's safe to import app modules
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_db
from app.main import create_application

# Import all models so their tables are registered on Base.metadata
import app.models.user 
import app.models.book
import app.models.library

# Clear the lru_cache so settings re-reads our patched env
get_settings.cache_clear()

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestSessionLocal = async_sessionmaker(
    bind=_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


@pytest.fixture(scope="session", autouse=True)
async def _create_tables():
    """Create all tables once per test session."""
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture()
async def db_session(_create_tables) -> AsyncGenerator[AsyncSession, None]:
    """Yield a fresh session; truncate all tables after each test."""
    async with _TestSessionLocal() as session:
        yield session
        await session.rollback()
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()


@pytest.fixture()
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """httpx AsyncClient wired to the FastAPI app with the test DB session."""

    async def _override_get_db():
        yield db_session

    app = create_application()
    app.dependency_overrides[get_db] = _override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture()
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    """Register + log in a test user; return Authorization header."""
    await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
            "full_name": "Test User",
        },
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
