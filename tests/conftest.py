import sys
from pathlib import Path

# Dodajemy root projektu do ścieżki
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
import pytest_asyncio
import httpx
from fastapi.routing import APIRoute

from src.main import app
from src.interface.dependencies import get_db_session

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def session():
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import sessionmaker
    from sqlmodel import SQLModel
    from sqlalchemy.pool import StaticPool

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session_maker = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as s:
        yield s

    await engine.dispose()


@pytest_asyncio.fixture
async def client(session):
    from httpx import ASGITransport

    async def override_get_db_session():
        yield session

    app.dependency_overrides[get_db_session] = override_get_db_session

    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
        follow_redirects=True,
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def api_prefix():
    prefixes = set()
    for r in app.routes:
        if isinstance(r, APIRoute):
            path = r.path
            if "/inboxes" in path:
                idx = path.find("/inboxes")
                prefixes.add(path[:idx].rstrip("/"))
    if not prefixes:
        return ""
    return sorted(prefixes, key=len, reverse=True)[0]
