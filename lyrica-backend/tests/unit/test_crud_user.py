"""
Unit tests for User CRUD operations.
"""

import pytest

from app.crud.user import user as user_crud
from app.schemas.auth import UserRegister


@pytest.mark.unit
@pytest.mark.asyncio
class TestUserCRUD:
    """Test User CRUD operations."""

    async def test_create_user_with_password(self, db_session):
        """Test creating a user with hashed password."""
        user_in = UserRegister(
            email="newuser@example.com",
            password="Password123!",
            full_name="New User",
            username="newuser",
        )

        user = await user_crud.create_with_password(db=db_session, obj_in=user_in)

        assert user.email == user_in.email
        assert user.full_name == user_in.full_name
        assert user.username == user_in.username
        assert user.password_hash != user_in.password
        assert user.is_active is True
        assert user.is_verified is False
        assert user.role == "user"

    async def test_get_user_by_email(self, db_session, test_user):
        """Test retrieving user by email."""
        user = await user_crud.get_by_email(db=db_session, email=test_user.email)

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    async def test_get_user_by_email_not_found(self, db_session):
        """Test retrieving non-existent user by email."""
        user = await user_crud.get_by_email(db=db_session, email="nonexistent@example.com")

        assert user is None

    async def test_get_user_by_username(self, db_session, test_user):
        """Test retrieving user by username."""
        user = await user_crud.get_by_username(db=db_session, username=test_user.username)

        assert user is not None
        assert user.id == test_user.id
        assert user.username == test_user.username

    async def test_authenticate_success(self, db_session, test_user):
        """Test successful authentication."""
        user = await user_crud.authenticate(
            db=db_session, email=test_user.email, password="TestPassword123!"
        )

        assert user is not None
        assert user.id == test_user.id

    async def test_authenticate_wrong_password(self, db_session, test_user):
        """Test authentication with wrong password."""
        user = await user_crud.authenticate(
            db=db_session, email=test_user.email, password="WrongPassword!"
        )

        assert user is None

    async def test_authenticate_wrong_email(self, db_session):
        """Test authentication with non-existent email."""
        user = await user_crud.authenticate(
            db=db_session, email="nonexistent@example.com", password="Password123!"
        )

        assert user is None

    async def test_is_active(self, test_user):
        """Test checking if user is active."""
        assert await user_crud.is_active(test_user) is True

    async def test_is_verified(self, test_user):
        """Test checking if user is verified."""
        assert await user_crud.is_verified(test_user) is True

    async def test_update_password(self, db_session, test_user):
        """Test updating user password."""
        new_password = "NewPassword456!"
        old_hash = test_user.password_hash

        updated_user = await user_crud.update_password(
            db=db_session, user=test_user, new_password=new_password
        )

        assert updated_user.password_hash != old_hash

        # Verify new password works
        user = await user_crud.authenticate(
            db=db_session, email=test_user.email, password=new_password
        )
        assert user is not None

    async def test_verify_email(self, db_session):
        """Test email verification."""
        from app.core.security import get_password_hash
        from app.models.user import User

        # Create unverified user
        user = User(
            email="unverified@example.com",
            username="unverified",
            password_hash=get_password_hash("Password123!"),
            full_name="Unverified User",
            is_active=True,
            is_verified=False,
            role="user",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.is_verified is False

        # Verify email
        updated_user = await user_crud.verify_email(db=db_session, user=user)

        assert updated_user.is_verified is True
