"""
CRUD operations for Lyrics model.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.lyrics import Lyrics, LyricsSection
from app.schemas.lyrics import LyricsCreate, LyricsUpdate


class CRUDLyrics(CRUDBase[Lyrics, LyricsCreate, LyricsUpdate]):
    """CRUD operations for Lyrics model."""

    async def get_by_user(
        self, db: AsyncSession, *, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Lyrics]:
        """
        Get all lyrics for a specific user.

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of lyrics
        """
        result = await db.execute(
            select(Lyrics)
            .where(Lyrics.user_id == user_id)
            .order_by(Lyrics.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_genre(
        self, db: AsyncSession, *, genre: str, skip: int = 0, limit: int = 100
    ) -> List[Lyrics]:
        """
        Get lyrics by genre.

        Args:
            db: Database session
            genre: Music genre
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of lyrics
        """
        result = await db.execute(
            select(Lyrics)
            .where(Lyrics.genre == genre)
            .order_by(Lyrics.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_public(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Lyrics]:
        """
        Get all public lyrics.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of public lyrics
        """
        result = await db.execute(
            select(Lyrics)
            .where(and_(Lyrics.is_public == True, Lyrics.status == "published"))
            .order_by(Lyrics.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create_with_user(
        self, db: AsyncSession, *, obj_in: LyricsCreate, user_id: UUID
    ) -> Lyrics:
        """
        Create lyrics for a specific user.

        Args:
            db: Database session
            obj_in: Lyrics creation schema
            user_id: User ID

        Returns:
            Created lyrics instance
        """
        obj_in_data = obj_in.model_dump()
        db_obj = Lyrics(**obj_in_data, user_id=user_id)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj


# Create singleton instance
lyrics = CRUDLyrics(Lyrics)
