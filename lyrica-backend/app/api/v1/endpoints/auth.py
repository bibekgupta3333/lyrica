"""
Authentication and Authorization endpoints.

This module provides endpoints for user registration, login,
token refresh, and API key management.
"""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user, get_current_user_or_api_key, get_db
from app.core import security
from app.core.config import settings
from app.crud.api_key import api_key as api_key_crud
from app.crud.user import user as user_crud
from app.models.user import User
from app.schemas.auth import (
    APIKeyCreate,
    APIKeyCreated,
    APIKeyResponse,
    AuthStatus,
    PasswordChange,
    TokenRefreshRequest,
    TokenResponse,
    UserLogin,
    UserProfile,
    UserProfileUpdate,
    UserRegister,
)

router = APIRouter()


# ============================================================================
# Registration & Login
# ============================================================================


@router.post("/register", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserRegister, db: AsyncSession = Depends(get_db)):
    """
    Register a new user.

    Args:
        user_in: User registration data
        db: Database session

    Returns:
        Created user profile

    Raises:
        HTTPException 400: If email already registered
    """
    # Check if email already exists
    existing_user = await user_crud.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Check if username already exists (if provided)
    if user_in.username:
        existing_username = await user_crud.get_by_username(db, username=user_in.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

    # Create user
    user = await user_crud.create_with_password(db, obj_in=user_in)

    logger.info(f"New user registered: {user.email} (id: {user.id})")

    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db),
):
    """
    Login with email and password to get access token.

    Uses OAuth2 password flow for compatibility with OpenAPI docs.
    The 'username' field should contain the email address.

    Args:
        form_data: OAuth2 form data (username=email, password)
        db: Database session

    Returns:
        JWT access and refresh tokens

    Raises:
        HTTPException 401: If authentication fails
    """
    # Authenticate user
    user = await user_crud.authenticate(db, email=form_data.username, password=form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    # Create access and refresh tokens
    access_token = security.create_access_token(subject=str(user.id))
    refresh_token = security.create_refresh_token(subject=str(user.id))

    logger.info(f"User logged in: {user.email} (id: {user.id})")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/login/json", response_model=TokenResponse)
async def login_json(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Login with JSON payload (alternative to OAuth2 form).

    Args:
        user_in: Login credentials (email, password)
        db: Database session

    Returns:
        JWT access and refresh tokens

    Raises:
        HTTPException 401: If authentication fails
    """
    # Authenticate user
    user = await user_crud.authenticate(db, email=user_in.email, password=user_in.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    # Create tokens
    access_token = security.create_access_token(subject=str(user.id))
    refresh_token = security.create_refresh_token(subject=str(user.id))

    logger.info(f"User logged in (JSON): {user.email} (id: {user.id})")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


# ============================================================================
# Token Management
# ============================================================================


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_request: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token using refresh token.

    Args:
        token_request: Refresh token
        db: Database session

    Returns:
        New access and refresh tokens

    Raises:
        HTTPException 401: If refresh token is invalid
    """
    # Verify refresh token
    user_id_str = security.verify_refresh_token(token_request.refresh_token)

    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Get user
    from uuid import UUID

    user_id = UUID(user_id_str)
    user = await user_crud.get(db, id=user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Create new tokens
    access_token = security.create_access_token(subject=str(user.id))
    refresh_token = security.create_refresh_token(subject=str(user.id))

    logger.info(f"Token refreshed for user: {user.email}")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


# ============================================================================
# User Profile
# ============================================================================


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current user profile.

    Args:
        current_user: Current authenticated user

    Returns:
        User profile
    """
    return current_user


@router.put("/me", response_model=UserProfile)
async def update_current_user_profile(
    user_update: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update current user profile.

    Args:
        user_update: Profile update data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated user profile
    """
    # Check username uniqueness if changed
    if user_update.username and user_update.username != current_user.username:
        existing = await user_crud.get_by_username(db, username=user_update.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

    # Update user
    update_data = user_update.model_dump(exclude_unset=True)
    updated_user = await user_crud.update(db, db_obj=current_user, obj_in=update_data)

    logger.info(f"User profile updated: {updated_user.email}")

    return updated_user


@router.post("/me/password")
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Change current user password.

    Args:
        password_change: Password change data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException 400: If current password is incorrect
    """
    # Verify current password
    if not security.verify_password(password_change.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )

    # Update password
    await user_crud.update_password(
        db, user=current_user, new_password=password_change.new_password
    )

    logger.info(f"Password changed for user: {current_user.email}")

    return {"message": "Password changed successfully"}


# ============================================================================
# API Key Management
# ============================================================================


@router.post("/api-keys", response_model=APIKeyCreated, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    api_key_in: APIKeyCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new API key for current user.

    API keys can be used for mobile apps and external integrations.
    The full API key is only shown once - save it securely!

    Args:
        api_key_in: API key creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created API key (with full key - shown only once!)
    """
    db_api_key, plain_key = await api_key_crud.create_for_user(
        db, obj_in=api_key_in, user_id=current_user.id
    )

    logger.info(f"API key created for user {current_user.email}: {db_api_key.name}")

    return APIKeyCreated(
        **db_api_key.__dict__,
        api_key=plain_key,
    )


@router.get("/api-keys", response_model=list[APIKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all API keys for current user.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of API keys (without full key values)
    """
    api_keys = await api_key_crud.get_by_user(db, user_id=current_user.id)
    return api_keys


@router.delete("/api-keys/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    api_key_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Revoke (deactivate) an API key.

    Args:
        api_key_id: API key ID (UUID)
        current_user: Current authenticated user
        db: Database session

    Raises:
        HTTPException 404: If API key not found
        HTTPException 403: If API key doesn't belong to current user
    """
    from uuid import UUID

    try:
        key_id = UUID(api_key_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid API key ID format",
        )

    # Get API key
    db_api_key = await api_key_crud.get(db, id=key_id)

    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    # Check ownership
    if db_api_key.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to revoke this API key",
        )

    # Revoke
    await api_key_crud.revoke(db, api_key_id=key_id)

    logger.info(f"API key revoked by user {current_user.email}: {db_api_key.name}")


# ============================================================================
# Status & Testing
# ============================================================================


@router.get("/status", response_model=AuthStatus)
async def get_auth_status(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current authentication status and permissions.

    Args:
        current_user: Current authenticated user

    Returns:
        Authentication status and user info
    """
    permissions = ["read:own", "write:own"]
    if current_user.role == "admin":
        permissions.extend(["read:all", "write:all", "delete:all"])

    return AuthStatus(
        authenticated=True,
        user=UserProfile.model_validate(current_user),
        permissions=permissions,
    )


@router.get("/test-auth")
async def test_auth(current_user: User = Depends(get_current_user_or_api_key)):
    """
    Test endpoint to verify authentication is working (JWT or API key).

    Args:
        current_user: Current authenticated user

    Returns:
        User info
    """
    return {
        "message": "Authentication successful!",
        "user_id": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role,
    }
