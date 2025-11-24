"""
Pytest configuration and fixtures.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create a test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def headers():
    """Default headers for requests."""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

