"""
Unit tests for security module (passwords and JWT tokens).
"""

from datetime import timedelta

import pytest

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_api_key,
    get_password_hash,
    verify_password,
    verify_refresh_token,
    verify_token,
)


@pytest.mark.unit
class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 50
        assert hashed.startswith("$2b$")  # BCrypt prefix

    def test_verify_password_success(self):
        """Test password verification with correct password."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_failure(self):
        """Test password verification with incorrect password."""
        password = "TestPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_different_hashes_same_password(self):
        """Test that same password produces different hashes (salt)."""
        password = "TestPassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)


@pytest.mark.unit
class TestJWTTokens:
    """Test JWT token generation and verification."""

    def test_create_access_token(self):
        """Test access token creation."""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        token = create_access_token(subject=user_id)

        assert isinstance(token, str)
        assert len(token) > 50

    def test_create_access_token_with_expiration(self):
        """Test access token with custom expiration."""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        token = create_access_token(subject=user_id, expires_delta=timedelta(minutes=5))

        assert isinstance(token, str)
        payload = decode_token(token)
        assert payload["sub"] == user_id

    def test_create_refresh_token(self):
        """Test refresh token creation."""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        token = create_refresh_token(subject=user_id)

        assert isinstance(token, str)
        payload = decode_token(token)
        assert payload["type"] == "refresh"

    def test_decode_token(self):
        """Test token decoding."""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        token = create_access_token(subject=user_id)

        payload = decode_token(token)

        assert payload["sub"] == user_id
        assert "exp" in payload
        assert "iat" in payload

    def test_verify_token(self):
        """Test token verification."""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        token = create_access_token(subject=user_id)

        verified_user_id = verify_token(token)

        assert verified_user_id == user_id

    def test_verify_invalid_token(self):
        """Test verification of invalid token."""
        invalid_token = "invalid.token.here"

        verified_user_id = verify_token(invalid_token)

        assert verified_user_id is None

    def test_verify_refresh_token(self):
        """Test refresh token verification."""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        token = create_refresh_token(subject=user_id)

        verified_user_id = verify_refresh_token(token)

        assert verified_user_id == user_id

    def test_verify_access_token_as_refresh(self):
        """Test that access token fails refresh token verification."""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        token = create_access_token(subject=user_id)

        verified_user_id = verify_refresh_token(token)

        assert verified_user_id is None

    def test_token_with_dict_subject(self):
        """Test token creation with dictionary subject."""
        data = {"user_id": "123", "email": "test@example.com"}
        token = create_access_token(subject=data)

        payload = decode_token(token)

        assert payload["user_id"] == "123"
        assert payload["email"] == "test@example.com"


@pytest.mark.unit
class TestAPIKeys:
    """Test API key generation."""

    def test_generate_api_key(self):
        """Test API key generation."""
        api_key = generate_api_key()

        assert isinstance(api_key, str)
        assert api_key.startswith("lyr_")
        assert len(api_key) == 44  # lyr_ (4) + 40 chars

    def test_generate_unique_api_keys(self):
        """Test that generated API keys are unique."""
        key1 = generate_api_key()
        key2 = generate_api_key()

        assert key1 != key2

    def test_api_key_format(self):
        """Test API key format."""
        api_key = generate_api_key()

        assert api_key.startswith("lyr_")
        # Rest should be hexadecimal
        hex_part = api_key[4:]
        assert all(c in "0123456789abcdef" for c in hex_part)
