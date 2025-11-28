"""
Authentication schemas for API requests and responses.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# ============================================================================
# User Registration & Login
# ============================================================================


class UserRegister(BaseModel):
    """User registration request schema."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=100, description="Password (min 8 chars)")
    full_name: str = Field(..., min_length=1, max_length=255, description="Full name")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username")


class UserLogin(BaseModel):
    """User login request schema."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="Password")


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class TokenRefreshRequest(BaseModel):
    """Token refresh request schema."""

    refresh_token: str = Field(..., description="Refresh token")


class TokenVerifyRequest(BaseModel):
    """Token verification request schema."""

    token: str = Field(..., description="Token to verify")


class TokenVerifyResponse(BaseModel):
    """Token verification response schema."""

    valid: bool = Field(..., description="Whether token is valid")
    user_id: Optional[UUID] = Field(None, description="User ID from token")
    expires_at: Optional[datetime] = Field(None, description="Token expiration time")


# ============================================================================
# Password Management
# ============================================================================


class PasswordChange(BaseModel):
    """Password change request schema."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")


class PasswordReset(BaseModel):
    """Password reset request schema."""

    email: EmailStr = Field(..., description="Email address")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema."""

    token: str = Field(..., description="Reset token from email")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")


# ============================================================================
# API Key Management
# ============================================================================


class APIKeyCreate(BaseModel):
    """API key creation request schema."""

    name: str = Field(..., min_length=1, max_length=255, description="API key name/description")
    expires_days: Optional[int] = Field(
        None, ge=1, le=365, description="Days until expiration (default: never)"
    )


class APIKeyResponse(BaseModel):
    """API key response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    key_prefix: str = Field(..., description="First 8 chars of key (for identification)")
    created_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    is_active: bool


class APIKeyCreated(APIKeyResponse):
    """API key creation response with full key (only shown once)."""

    api_key: str = Field(..., description="Full API key (save this - shown only once!)")


# ============================================================================
# User Profile
# ============================================================================


class UserProfile(BaseModel):
    """User profile response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    full_name: str
    username: Optional[str]
    is_active: bool
    is_verified: bool
    role: str
    created_at: datetime
    updated_at: datetime


class UserProfileUpdate(BaseModel):
    """User profile update schema."""

    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    username: Optional[str] = Field(None, min_length=3, max_length=50)


# ============================================================================
# Authentication Status
# ============================================================================


class AuthStatus(BaseModel):
    """Authentication status response."""

    authenticated: bool
    user: Optional[UserProfile]
    permissions: list[str] = Field(default_factory=list)
