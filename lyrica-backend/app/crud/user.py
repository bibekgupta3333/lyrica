"""
CRUD operations for User model.
"""

from typing import Optional
from uuid import UUID

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.auth import UserRegister


class CRUDUser(CRUDBase[User, UserRegister, dict]):
    """CRUD operations for User model."""

    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """
        Get user by email address.

        Args:
            db: Database session
            email: Email address

        Returns:
            User object if found, None otherwise
        """
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, db: AsyncSession, *, username: str) -> Optional[User]:
        """
        Get user by username.

        Args:
            db: Database session
            username: Username

        Returns:
            User object if found, None otherwise
        """
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def create_with_password(self, db: AsyncSession, *, obj_in: UserRegister) -> User:
        """
        Create a new user with hashed password.

        Args:
            db: Database session
            obj_in: User registration data

        Returns:
            Created user object
        """
        # Hash password
        hashed_password = get_password_hash(obj_in.password)

        # Create user object
        db_obj = User(
            email=obj_in.email,
            password_hash=hashed_password,
            full_name=obj_in.full_name,
            username=obj_in.username,
            is_active=True,
            is_verified=False,  # Require email verification
        )

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        logger.info(f"User created: {db_obj.email} (id: {db_obj.id})")

        return db_obj

    async def authenticate(self, db: AsyncSession, *, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email and password.

        Args:
            db: Database session
            email: Email address
            password: Plain text password

        Returns:
            User object if authentication successful, None otherwise
        """
        user = await self.get_by_email(db, email=email)

        if not user:
            logger.warning(f"Authentication failed: user not found (email: {email})")
            return None

        if not verify_password(password, user.password_hash):
            logger.warning(f"Authentication failed: invalid password (email: {email})")
            return None

        if not user.is_active:
            logger.warning(f"Authentication failed: user inactive (email: {email})")
            return None

        logger.info(f"User authenticated: {user.email} (id: {user.id})")
        return user

    async def is_active(self, user: User) -> bool:
        """
        Check if user is active.

        Args:
            user: User object

        Returns:
            True if user is active, False otherwise
        """
        return user.is_active

    async def is_verified(self, user: User) -> bool:
        """
        Check if user is verified.

        Args:
            user: User object

        Returns:
            True if user is verified, False otherwise
        """
        return user.is_verified

    async def update_password(self, db: AsyncSession, *, user: User, new_password: str) -> User:
        """
        Update user password.

        Args:
            db: Database session
            user: User object
            new_password: New plain text password

        Returns:
            Updated user object
        """
        hashed_password = get_password_hash(new_password)
        user.password_hash = hashed_password

        await db.commit()
        await db.refresh(user)

        logger.info(f"Password updated for user: {user.email}")

        return user

    async def verify_email(self, db: AsyncSession, *, user: User) -> User:
        """
        Mark user email as verified.

        Args:
            db: Database session
            user: User object

        Returns:
            Updated user object
        """
        user.is_verified = True

        await db.commit()
        await db.refresh(user)

        logger.info(f"Email verified for user: {user.email}")

        return user


# Singleton instance
user = CRUDUser(User)
