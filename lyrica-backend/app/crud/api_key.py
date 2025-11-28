"""
CRUD operations for APIKey model.
"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import generate_api_key, hash_api_key, verify_api_key
from app.crud.base import CRUDBase
from app.models.api_key import APIKey
from app.schemas.auth import APIKeyCreate


class CRUDAPIKey(CRUDBase[APIKey, APIKeyCreate, dict]):
    """CRUD operations for APIKey model."""

    async def create_for_user(
        self, db: AsyncSession, *, obj_in: APIKeyCreate, user_id: UUID
    ) -> tuple[APIKey, str]:
        """
        Create a new API key for a user.

        Args:
            db: Database session
            obj_in: API key creation data
            user_id: User ID

        Returns:
            Tuple of (APIKey object, plain API key string)
            Note: Plain key is only returned once and must be saved by caller
        """
        # Generate API key
        plain_key = generate_api_key()
        hashed_key = hash_api_key(plain_key)

        # Calculate expiration
        expires_at = None
        if obj_in.expires_days:
            from datetime import timezone

            expires_at = datetime.now(timezone.utc) + timedelta(days=obj_in.expires_days)

        # Create API key object
        db_obj = APIKey(
            user_id=user_id,
            name=obj_in.name,
            key_hash=hashed_key,
            key_prefix=plain_key[:8],  # Store first 8 chars for identification
            expires_at=expires_at,
            is_active=True,
        )

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        logger.info(f"API key created for user {user_id}: {db_obj.name} (id: {db_obj.id})")

        return db_obj, plain_key

    async def get_by_key(self, db: AsyncSession, *, api_key: str) -> Optional[APIKey]:
        """
        Get API key by plain key string.

        Args:
            db: Database session
            api_key: Plain API key string

        Returns:
            APIKey object if found and valid, None otherwise
        """
        # Get key prefix for faster lookup
        key_prefix = api_key[:8]

        # Find potential matches by prefix
        result = await db.execute(
            select(APIKey).where(APIKey.key_prefix == key_prefix, APIKey.is_active == True)
        )
        potential_keys = result.scalars().all()

        # Verify against hashed keys
        for db_key in potential_keys:
            if verify_api_key(api_key, db_key.key_hash):
                # Check expiration
                from datetime import timezone

                now = datetime.now(timezone.utc)
                if db_key.expires_at and db_key.expires_at < now:
                    logger.warning(f"API key expired: {db_key.name} (id: {db_key.id})")
                    return None

                # Update last used timestamp
                db_key.last_used_at = now
                await db.commit()

                return db_key

        logger.warning(f"API key not found or invalid: {key_prefix}...")
        return None

    async def get_by_user(
        self, db: AsyncSession, *, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[APIKey]:
        """
        Get all API keys for a user.

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of APIKey objects
        """
        result = await db.execute(
            select(APIKey)
            .where(APIKey.user_id == user_id)
            .order_by(APIKey.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def revoke(self, db: AsyncSession, *, api_key_id: UUID) -> Optional[APIKey]:
        """
        Revoke (deactivate) an API key.

        Args:
            db: Database session
            api_key_id: API key ID

        Returns:
            Updated APIKey object or None if not found
        """
        result = await db.execute(select(APIKey).where(APIKey.id == api_key_id))
        db_obj = result.scalar_one_or_none()

        if not db_obj:
            return None

        db_obj.is_active = False
        await db.commit()
        await db.refresh(db_obj)

        logger.info(f"API key revoked: {db_obj.name} (id: {db_obj.id})")

        return db_obj


# Singleton instance
api_key = CRUDAPIKey(APIKey)
