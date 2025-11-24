"""
User schemas for API requests and responses.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# Shared properties
class UserBase(BaseModel):
    """Base user schema."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = True


# Properties to receive via API on creation
class UserCreate(UserBase):
    """User creation schema."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8, max_length=100)


# Properties to receive via API on update
class UserUpdate(UserBase):
    """User update schema."""
    password: Optional[str] = Field(None, min_length=8, max_length=100)


# Properties to return via API
class User(UserBase):
    """User response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    email: EmailStr
    username: str
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None


# Properties stored in DB
class UserInDB(User):
    """User in database schema (includes password hash)."""
    password_hash: str

