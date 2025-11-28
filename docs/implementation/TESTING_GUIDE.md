# Testing Guide

**Comprehensive testing framework for Lyrica backend**

## Overview

The Lyrica backend uses **pytest** with **async support** for comprehensive testing coverage. The test suite includes:

- ✅ **Unit Tests**: Testing individual functions and modules
- ✅ **Integration Tests**: Testing API endpoints and workflows
- ✅ **Code Coverage**: Target >80% coverage
- ⏳ **Load Testing**: Performance and stress testing (planned)

---

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests
│   ├── __init__.py
│   ├── test_security.py     # Security module tests (16 tests)
│   └── test_crud_user.py    # User CRUD tests (11 tests)
├── integration/             # Integration tests
│   ├── __init__.py
│   ├── test_auth_endpoints.py     # Auth API tests (20 tests)
│   ├── test_lyrics_endpoints.py   # Lyrics API tests (9 tests)
│   ├── test_styles_endpoints.py   # Styles API tests (5 tests)
│   └── test_rag_endpoints.py      # RAG API tests (5 tests)
└── e2e/                     # End-to-end tests (planned)
```

---

## Quick Start

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Tests with specific markers
pytest -m unit
pytest -m integration
pytest -m auth
pytest -m rag
```

### Run With Coverage

```bash
# Run tests with coverage report
pytest --cov=app --cov-report=html

# Open coverage report in browser
open htmlcov/index.html
```

### Skip Slow Tests

```bash
pytest -m "not slow"
```

---

## Test Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
asyncio_mode = auto

markers =
    unit: Unit tests
    integration: Integration tests
    auth: Authentication tests
    rag: RAG system tests
    slow: Slow tests

addopts =
    -v
    --cov=app
    --cov-report=html
    --cov-fail-under=80
```

### Coverage Configuration

```ini
[coverage:run]
source = app
omit =
    */tests/*
    */migrations/*
    */__pycache__/*

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
```

---

## Fixtures

### Database Fixtures

```python
@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncSession:
    """Create test database session."""
    # Creates in-memory SQLite database for tests

@pytest_asyncio.fixture
async def client(db_session) -> AsyncClient:
    """HTTP client with database override."""
    # FastAPI test client with database mocking
```

### User Fixtures

```python
@pytest_asyncio.fixture
async def test_user(db_session) -> User:
    """Create test user."""
    # Creates user: test@example.com / TestPassword123!

@pytest_asyncio.fixture
async def admin_user(db_session) -> User:
    """Create admin user."""
    # Creates admin: admin@example.com / AdminPassword123!

@pytest_asyncio.fixture
async def user_token(test_user) -> str:
    """Generate JWT token for test user."""

@pytest_asyncio.fixture
async def test_api_key(test_user) -> tuple[str, str]:
    """Create test API key."""
    # Returns (api_key, key_id)
```

### Data Fixtures

```python
@pytest_asyncio.fixture
async def test_lyrics(db_session, test_user):
    """Create test lyrics."""

@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""

@pytest.fixture
def mock_embedding():
    """Mock embedding vector."""
```

---

## Writing Tests

### Unit Test Example

```python
@pytest.mark.unit
class TestPasswordHashing:
    """Test password hashing."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 50
        assert hashed.startswith("$2b$")

    def test_verify_password_success(self):
        """Test password verification."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True
```

### Integration Test Example

```python
@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.asyncio
class TestRegistration:
    """Test user registration endpoints."""

    async def test_register_new_user(self, client: AsyncClient):
        """Test registering a new user."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "Password123!",
                "full_name": "New User",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
```

### Async Test Example

```python
@pytest.mark.asyncio
async def test_create_user(db_session):
    """Test creating user."""
    user_in = UserRegister(
        email="test@example.com",
        password="Password123!",
        full_name="Test User",
    )

    user = await user_crud.create_with_password(
        db=db_session, obj_in=user_in
    )

    assert user.email == user_in.email
```

---

## Test Markers

Use markers to categorize and selectively run tests:

### Built-in Markers

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.auth` - Authentication tests
- `@pytest.mark.rag` - RAG system tests
- `@pytest.mark.slow` - Slow tests (>5 seconds)
- `@pytest.mark.asyncio` - Async tests

### Running Specific Markers

```bash
# Run only authentication tests
pytest -m auth

# Run integration tests except slow ones
pytest -m "integration and not slow"

# Run multiple markers
pytest -m "auth or rag"
```

---

## Coverage Reports

### Generate Coverage Report

```bash
# HTML report (recommended)
pytest --cov=app --cov-report=html
open htmlcov/index.html

# Terminal report
pytest --cov=app --cov-report=term-missing

# XML report (for CI/CD)
pytest --cov=app --cov-report=xml
```

### Coverage Goals

| Module | Target | Current |
|--------|--------|---------|
| Core Security | >95% | 88.06% |
| Models | >90% | ~96% |
| Schemas | 100% | 100% |
| API Endpoints | >80% | 25-88% |
| Services | >70% | 15-50% |
| **Overall** | **>80%** | **45.84%** |

---

## Current Test Status

### ✅ Completed Tests (16 passing)

**Security Module (100% coverage):**
- ✅ Password hashing & verification (4 tests)
- ✅ JWT token generation & validation (9 tests)
- ✅ API key generation (3 tests)

### ⏳ In Progress Tests

**User CRUD (11 tests created):**
- ⏳ Create user with password
- ⏳ Authenticate user
- ⏳ Update password
- ⏳ Verify email

**Authentication Endpoints (20 tests created):**
- ⏳ User registration (4 tests)
- ⏳ User login (4 tests)
- ⏳ Token management (2 tests)
- ⏳ Profile management (4 tests)
- ⏳ API key management (3 tests)
- ⏳ Auth status (3 tests)

**Other Endpoints (19 tests created):**
- ⏳ Lyrics endpoints (9 tests)
- ⏳ Styles endpoints (5 tests)
- ⏳ RAG endpoints (5 tests)

### 🚧 Pending Tests

- [ ] Agent workflow tests
- [ ] Error handling tests
- [ ] Rate limiting tests
- [ ] Load testing
- [ ] E2E tests

---

## Best Practices

### 1. Test Naming

```python
# Good
def test_user_can_register_with_valid_email():
    pass

# Bad
def test1():
    pass
```

### 2. Arrange-Act-Assert

```python
def test_password_hashing():
    # Arrange
    password = "TestPassword123!"

    # Act
    hashed = get_password_hash(password)

    # Assert
    assert verify_password(password, hashed)
```

### 3. Use Fixtures

```python
# Good - reusable
async def test_get_user(client, test_user):
    response = await client.get(f"/users/{test_user.id}")

# Bad - repetitive
async def test_get_user(client, db):
    user = User(email="test@example.com", ...)
    db.add(user)
    await db.commit()
    response = await client.get(f"/users/{user.id}")
```

### 4. Test One Thing

```python
# Good
def test_password_hashing():
    hashed = get_password_hash("password")
    assert hashed != "password"

def test_password_verification():
    hashed = get_password_hash("password")
    assert verify_password("password", hashed)

# Bad - tests multiple things
def test_password():
    hashed = get_password_hash("password")
    assert hashed != "password"
    assert verify_password("password", hashed)
    assert not verify_password("wrong", hashed)
```

### 5. Use Meaningful Assertions

```python
# Good
assert response.status_code == 201
assert data["email"] == "test@example.com"

# Bad
assert response.status_code  # What status code?
assert data  # What are we checking?
```

---

## Continuous Integration

### GitHub Actions (planned)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Troubleshooting

### Tests Failing Due to Database Issues

```bash
# Check if database is running
docker ps | grep postgres

# Restart database
docker-compose restart postgres
```

### Import Errors

```bash
# Install test dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov httpx
```

### Async Fixtures Not Working

Ensure you're using `@pytest_asyncio.fixture` not `@pytest.fixture`:

```python
# Correct
@pytest_asyncio.fixture
async def test_user(db):
    ...

# Wrong
@pytest.fixture
async def test_user(db):
    ...
```

---

## Next Steps

1. ✅ Complete unit tests for all CRUD operations
2. ✅ Complete integration tests for all API endpoints
3. ⏳ Add agent workflow tests
4. ⏳ Increase coverage to >80%
5. ⏳ Add load testing with Locust
6. ⏳ Set up CI/CD pipeline

---

## Related Documentation

- [API Reference](API_REFERENCE.md)
- [Agent System Guide](AGENT_SYSTEM_GUIDE.md)
- [RAG Implementation](RAG_IMPLEMENTATION.md)
- [Authentication API](AUTH_API_QUICK_REFERENCE.md)

---

**Last Updated**: November 28, 2025  
**Test Coverage**: 45.84% (target: 80%)  
**Tests Passing**: 16/27 (59%)
