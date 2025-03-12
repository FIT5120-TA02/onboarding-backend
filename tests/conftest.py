"""Test configuration module."""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.app.core.config import settings
from src.app.core.db.base_class import Base
from src.app.core.db.session import get_db
from src.app.core.setup import create_app

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for testing.

    Yields:
        Event loop.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create a test database engine.

    Yields:
        Test database engine.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session.

    Args:
        test_engine: Test database engine.

    Yields:
        Test database session.
    """
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    TestSessionLocal = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    async with TestSessionLocal() as session:
        yield session

    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def app(test_db) -> FastAPI:
    """Create a test FastAPI application.

    Args:
        test_db: Test database session.

    Returns:
        Test FastAPI application.
    """
    app = create_app()

    # Override the get_db dependency
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    return app


@pytest.fixture(scope="function")
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client.

    Args:
        app: Test FastAPI application.

    Yields:
        Test client.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client