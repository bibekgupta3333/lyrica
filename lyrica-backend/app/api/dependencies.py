"""
Common dependencies for API endpoints.

This module provides reusable dependencies for database sessions,
authentication, and authorization.
"""

from typing import Annotated, Optional

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.user import User

# OAuth2 scheme for JWT authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

# HTTP Bearer scheme (alternative)
http_bearer = HTTPBearer()


# ============================================================================
# Database Dependencies
# ============================================================================


async def get_db() -> AsyncSession:
    """
    Get database session dependency.

    Yields:
        Database session

    Example:
        @app.get("/items")
        async def read_items(db: AsyncSession = Depends(get_db)):
            # Use db session
            pass
    """
    async with AsyncSessionLocal() as session:
        yield session


# ============================================================================
# Authentication Dependencies
# ============================================================================


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        token: JWT token from Authorization header
        db: Database session

    Returns:
        Current authenticated user

    Raises:
        HTTPException: If authentication fails
    """
    from uuid import UUID

    from app.core.security import verify_token
    from app.crud.user import user as user_crud

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify token and extract user ID
    user_id_str = verify_token(token)

    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise credentials_exception

    # Get user from database
    user = await user_crud.get(db, id=user_id)

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user (must be authenticated and active).

    Args:
        current_user: Current user from get_current_user

    Returns:
        Active user

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    return current_user


async def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise.

    Args:
        token: JWT token from Authorization header (optional)
        db: Database session

    Returns:
        Current authenticated user or None
    """
    from uuid import UUID

    from app.core.security import verify_token
    from app.crud.user import user as user_crud

    if not token:
        return None

    try:
        user_id_str = verify_token(token)
        if user_id_str is None:
            return None

        user_id = UUID(user_id_str)
        user = await user_crud.get(db, id=user_id)
        return user

    except Exception:
        return None


# ============================================================================
# API Key Authentication (for mobile/external apps)
# ============================================================================


async def get_user_from_api_key(api_key: str, db: AsyncSession) -> Optional[User]:
    """
    Authenticate user using API key.

    Args:
        api_key: API key from request header
        db: Database session

    Returns:
        User associated with API key or None
    """
    from app.crud.api_key import api_key as api_key_crud
    from app.crud.user import user as user_crud

    # Find and validate API key
    db_api_key = await api_key_crud.get_by_key(db, api_key=api_key)

    if not db_api_key:
        return None

    # Get user
    user = await user_crud.get(db, id=db_api_key.user_id)

    return user


async def get_current_user_or_api_key(
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current user from either JWT token or API key.
    Supports both Bearer token and API key authentication.

    Args:
        authorization: Authorization header (Bearer token)
        x_api_key: X-API-Key header
        db: Database session

    Returns:
        Authenticated user

    Raises:
        HTTPException: If authentication fails
    """
    # Try API key first
    if x_api_key:
        user = await get_user_from_api_key(x_api_key, db)
        if user and user.is_active:
            return user

    # Try JWT token
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split("Bearer ")[1]
        return await get_current_user(token=token, db=db)

    # No valid authentication
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated. Provide either Bearer token or X-API-Key header.",
        headers={"WWW-Authenticate": "Bearer"},
    )


# ============================================================================
# Role-Based Access Control (RBAC)
# ============================================================================


def require_role(*roles: str):
    """
    Dependency factory for role-based access control.

    Args:
        *roles: Allowed roles (admin, user, etc.)

    Returns:
        Dependency function that checks user role

    Example:
        @app.get("/admin/users")
        async def list_users(user: User = Depends(require_role("admin"))):
            # Only admins can access
            pass
    """

    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join(roles)}",
            )
        return current_user

    return role_checker


# Pre-defined role checkers
require_admin = require_role("admin")
require_user_or_admin = require_role("user", "admin")
