"""
Pytest configuration and fixtures.

This module provides shared fixtures for all tests.
"""

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.base_class import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User

# Test database URL (PostgreSQL test database)
# Uses a separate test database to avoid affecting development data
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/lyrica_test"


# ============================================================================
# Simple Client Fixture (no database override)
# ============================================================================


@pytest_asyncio.fixture
async def simple_client() -> AsyncGenerator[AsyncClient, None]:
    """Create a simple test HTTP client without database override."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client


# ============================================================================
# Database Fixtures
# ============================================================================


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """Create a test database engine."""
    # Import all models to ensure they're registered
    from app import models  # noqa: F401

    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session_maker = sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session_maker() as session:
        yield session
        await session.rollback()
        await session.close()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test HTTP client with database override."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ============================================================================
# User Fixtures
# ============================================================================


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    from app.core.security import get_password_hash

    user = User(
        email="test@example.com",
        username="testuser",
        password_hash=get_password_hash("TestPassword123!"),
        full_name="Test User",
        is_active=True,
        is_verified=True,
        role="user",
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create an admin user."""
    from app.core.security import get_password_hash

    user = User(
        email="admin@example.com",
        username="admin",
        password_hash=get_password_hash("AdminPassword123!"),
        full_name="Admin User",
        is_active=True,
        is_verified=True,
        role="admin",
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest_asyncio.fixture
async def user_token(test_user: User) -> str:
    """Generate JWT token for test user."""
    from app.core.security import create_access_token

    return create_access_token(subject=str(test_user.id))


@pytest_asyncio.fixture
async def admin_token(admin_user: User) -> str:
    """Generate JWT token for admin user."""
    from app.core.security import create_access_token

    return create_access_token(subject=str(admin_user.id))


# ============================================================================
# API Key Fixtures
# ============================================================================


@pytest_asyncio.fixture
async def test_api_key(db_session: AsyncSession, test_user: User) -> tuple[str, str]:
    """Create a test API key and return (key, key_id)."""
    from app.crud.api_key import api_key as api_key_crud
    from app.schemas.auth import APIKeyCreate

    api_key_in = APIKeyCreate(name="Test API Key", expires_days=30)

    db_api_key, plain_key = await api_key_crud.create_for_user(
        db=db_session, obj_in=api_key_in, user_id=test_user.id
    )

    return plain_key, str(db_api_key.id)


# ============================================================================
# Lyrics Fixtures
# ============================================================================


@pytest_asyncio.fixture
async def test_lyrics(db_session: AsyncSession, test_user: User):
    """Create test lyrics."""
    from app.models.lyrics import Lyrics

    lyrics = Lyrics(
        user_id=test_user.id,
        title="Test Song",
        content="[Verse 1]\nTest lyrics content\n[Chorus]\nTest chorus",
        genre="pop",
        mood="happy",
        theme="love",
        is_public=True,
        quality_score=8.5,
    )

    db_session.add(lyrics)
    await db_session.commit()
    await db_session.refresh(lyrics)

    return lyrics


# ============================================================================
# Mock Fixtures
# ============================================================================


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    return {
        "title": "Generated Song",
        "lyrics": "[Verse 1]\nGenerated content\n[Chorus]\nGenerated chorus",
        "sections": [
            {"type": "verse", "number": 1, "content": "Generated content"},
            {"type": "chorus", "number": 1, "content": "Generated chorus"},
        ],
    }


@pytest.fixture
def mock_embedding():
    """Mock embedding vector for testing."""
    import numpy as np

    return np.random.rand(384).tolist()  # 384-dimensional vector


# ============================================================================
# Utility Functions
# ============================================================================


def assert_valid_uuid(uuid_string: str) -> bool:
    """Assert that a string is a valid UUID."""
    from uuid import UUID

    try:
        UUID(uuid_string)
        return True
    except ValueError:
        return False
