"""
CRUD operations for User model.
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD operations for User model."""
    
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            db: Database session
            email: User email
        
        Returns:
            User instance or None
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
            User instance or None
        """
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """
        Create new user with hashed password.
        
        Args:
            db: Database session
            obj_in: User creation schema
        
        Returns:
            Created user instance
        """
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            password_hash=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_active=obj_in.is_active if obj_in.is_active is not None else True,
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def authenticate(
        self,
        db: AsyncSession,
        *,
        email: str,
        password: str
    ) -> Optional[User]:
        """
        Authenticate user by email and password.
        
        Args:
            db: Database session
            email: User email
            password: Plain text password
        
        Returns:
            User instance if authenticated, None otherwise
        """
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
    
    def is_active(self, user: User) -> bool:
        """Check if user is active."""
        return user.is_active
    
    def is_superuser(self, user: User) -> bool:
        """Check if user is superuser."""
        return user.is_superuser


# Create singleton instance
user = CRUDUser(User)

