"""
Integration tests for authentication endpoints.
"""

import pytest
from httpx import AsyncClient

from app.models.user import User


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
                "username": "newuser",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert data["is_active"] is True
        assert data["role"] == "user"
        assert "id" in data

    async def test_register_duplicate_email(self, client: AsyncClient, test_user: User):
        """Test registering with duplicate email."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "password": "Password123!",
                "full_name": "Duplicate User",
            },
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    async def test_register_short_password(self, client: AsyncClient):
        """Test registration with short password."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "short@example.com",
                "password": "short",
                "full_name": "Short Password",
            },
        )

        assert response.status_code == 422  # Validation error

    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "Password123!",
                "full_name": "Invalid Email",
            },
        )

        assert response.status_code == 422  # Validation error


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.asyncio
class TestLogin:
    """Test user login endpoints."""

    async def test_login_oauth2_success(self, client: AsyncClient, test_user: User):
        """Test successful login with OAuth2 format."""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "TestPassword123!",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0

    async def test_login_json_success(self, client: AsyncClient, test_user: User):
        """Test successful login with JSON format."""
        response = await client.post(
            "/api/v1/auth/login/json",
            json={
                "email": test_user.email,
                "password": "TestPassword123!",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_login_wrong_password(self, client: AsyncClient, test_user: User):
        """Test login with wrong password."""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "WrongPassword!",
            },
        )

        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    async def test_login_wrong_email(self, client: AsyncClient):
        """Test login with non-existent email."""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "Password123!",
            },
        )

        assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.asyncio
class TestTokenManagement:
    """Test token refresh and management."""

    async def test_refresh_token(self, client: AsyncClient, test_user: User):
        """Test refreshing access token."""
        # First login
        login_response = await client.post(
            "/api/v1/auth/login",
            data={"username": test_user.email, "password": "TestPassword123!"},
        )
        refresh_token = login_response.json()["refresh_token"]

        # Refresh token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_refresh_invalid_token(self, client: AsyncClient):
        """Test refreshing with invalid token."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid.token.here"},
        )

        assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.asyncio
class TestUserProfile:
    """Test user profile endpoints."""

    async def test_get_profile(self, client: AsyncClient, user_token: str, test_user: User):
        """Test getting user profile."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
        assert data["role"] == test_user.role

    async def test_get_profile_unauthorized(self, client: AsyncClient):
        """Test getting profile without authentication."""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401

    async def test_update_profile(self, client: AsyncClient, user_token: str):
        """Test updating user profile."""
        response = await client.put(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"full_name": "Updated Name"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"

    async def test_change_password(self, client: AsyncClient, user_token: str):
        """Test changing password."""
        response = await client.post(
            "/api/v1/auth/me/password",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "current_password": "TestPassword123!",
                "new_password": "NewPassword456!",
            },
        )

        assert response.status_code == 200
        assert "success" in response.json()["message"].lower()


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.asyncio
class TestAPIKeys:
    """Test API key endpoints."""

    async def test_create_api_key(self, client: AsyncClient, user_token: str):
        """Test creating an API key."""
        response = await client.post(
            "/api/v1/auth/api-keys",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"name": "Test Key", "expires_days": 30},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Key"
        assert "api_key" in data
        assert data["api_key"].startswith("lyr_")

    async def test_list_api_keys(self, client: AsyncClient, user_token: str):
        """Test listing API keys."""
        # Create a key first
        await client.post(
            "/api/v1/auth/api-keys",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"name": "Test Key"},
        )

        # List keys
        response = await client.get(
            "/api/v1/auth/api-keys",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_revoke_api_key(
        self, client: AsyncClient, user_token: str, test_api_key: tuple[str, str]
    ):
        """Test revoking an API key."""
        _, key_id = test_api_key

        response = await client.delete(
            f"/api/v1/auth/api-keys/{key_id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 204


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.asyncio
class TestAuthentication:
    """Test authentication flow."""

    async def test_auth_status(self, client: AsyncClient, user_token: str):
        """Test getting auth status."""
        response = await client.get(
            "/api/v1/auth/status",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True
        assert "user" in data
        assert "permissions" in data

    async def test_test_auth_with_jwt(self, client: AsyncClient, user_token: str):
        """Test auth test endpoint with JWT."""
        response = await client.get(
            "/api/v1/auth/test-auth",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Authentication successful!"

    async def test_test_auth_with_api_key(self, client: AsyncClient, test_api_key: tuple[str, str]):
        """Test auth test endpoint with API key."""
        api_key, _ = test_api_key

        response = await client.get(
            "/api/v1/auth/test-auth",
            headers={"X-API-Key": api_key},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Authentication successful!"
