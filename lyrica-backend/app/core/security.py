"""
Security utilities for authentication and authorization.

This module provides JWT token generation/validation and
password hashing using bcrypt.
"""

from datetime import datetime, timedelta
from typing import Any, Optional

from jose import JWTError, jwt
from loguru import logger
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================================================
# Password Hashing
# ============================================================================


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


# ============================================================================
# JWT Token Management
# ============================================================================


def create_access_token(
    subject: str | dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        subject: Token subject (user ID or data dict)
        expires_delta: Token expiration time (default: from settings)

    Returns:
        Encoded JWT token

    Example:
        >>> token = create_access_token(subject="user-uuid")
        >>> token = create_access_token(
        ...     subject={"user_id": "uuid", "email": "user@example.com"},
        ...     expires_delta=timedelta(hours=24)
        ... )
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    # Build payload
    if isinstance(subject, dict):
        to_encode = subject.copy()
    else:
        to_encode = {"sub": str(subject)}

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})

    # Encode JWT
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    return encoded_jwt


def create_refresh_token(
    subject: str | dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT refresh token.

    Args:
        subject: Token subject (user ID or data dict)
        expires_delta: Token expiration time (default: 7 days)

    Returns:
        Encoded JWT refresh token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)

    if isinstance(subject, dict):
        to_encode = subject.copy()
    else:
        to_encode = {"sub": str(subject)}

    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})

    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    return encoded_jwt


def decode_token(token: str) -> Optional[dict[str, Any]]:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload or None if invalid

    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload

    except JWTError as e:
        logger.warning(f"JWT decode error: {str(e)}")
        raise


def verify_token(token: str) -> Optional[str]:
    """
    Verify a JWT token and extract the subject (user ID).

    Args:
        token: JWT token string

    Returns:
        User ID (subject) from token or None if invalid
    """
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")

        if user_id is None:
            return None

        return user_id

    except JWTError:
        return None


def verify_refresh_token(token: str) -> Optional[str]:
    """
    Verify a refresh token and extract the subject.

    Args:
        token: JWT refresh token string

    Returns:
        User ID (subject) from token or None if invalid
    """
    try:
        payload = decode_token(token)

        # Check if it's a refresh token
        if payload.get("type") != "refresh":
            logger.warning("Token is not a refresh token")
            return None

        user_id: str = payload.get("sub")

        if user_id is None:
            return None

        return user_id

    except JWTError:
        return None


# ============================================================================
# API Key Management
# ============================================================================


def generate_api_key() -> str:
    """
    Generate a secure API key for mobile/external access.

    Returns:
        API key string (40 characters)

    Example:
        >>> api_key = generate_api_key()
        >>> print(api_key)
        'lyr_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6'
    """
    import secrets

    # Generate 30 random bytes, encode as hex (60 chars), take first 40
    random_part = secrets.token_hex(20)

    # Add prefix for identification
    return f"lyr_{random_part}"


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key for storage.

    Args:
        api_key: Plain API key

    Returns:
        Hashed API key
    """
    # Use same hashing as passwords
    return get_password_hash(api_key)


def verify_api_key(plain_api_key: str, hashed_api_key: str) -> bool:
    """
    Verify an API key against a hashed version.

    Args:
        plain_api_key: Plain API key from request
        hashed_api_key: Hashed API key from database

    Returns:
        True if API key matches, False otherwise
    """
    return verify_password(plain_api_key, hashed_api_key)
