"""
CRUD operations for Song model.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.song import Song
from app.schemas.song import (
    CompleteSongGenerationRequest,
    SongFromLyricsRequest,
    UpdateSongSettingsRequest,
)


class CRUDSong:
    """CRUD operations for Song model."""

    async def get(self, db: AsyncSession, song_id: uuid.UUID) -> Optional[Song]:
        """Get song by ID."""
        result = await db.execute(select(Song).where(Song.id == song_id))
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        genre: Optional[str] = None,
    ) -> List[Song]:
        """Get songs by user with optional filtering."""
        query = select(Song).where(Song.user_id == user_id)

        if status:
            query = query.where(Song.generation_status == status)
        if genre:
            query = query.where(Song.genre == genre)

        query = query.order_by(desc(Song.created_at)).offset(skip).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_public_songs(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        genre: Optional[str] = None,
    ) -> List[Song]:
        """Get public songs."""
        query = select(Song).where(
            and_(Song.is_public == True, Song.generation_status == "completed")  # noqa: E712
        )

        if genre:
            query = query.where(Song.genre == genre)

        query = query.order_by(desc(Song.created_at)).offset(skip).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def count_by_user(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        status: Optional[str] = None,
    ) -> int:
        """Count songs by user."""
        query = select(func.count(Song.id)).where(Song.user_id == user_id)

        if status:
            query = query.where(Song.generation_status == status)

        result = await db.execute(query)
        return result.scalar() or 0

    async def search(
        self,
        db: AsyncSession,
        query_text: str,
        user_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Song]:
        """Search songs by title, artist, or genre."""
        search_pattern = f"%{query_text}%"
        query = select(Song).where(
            or_(
                Song.title.ilike(search_pattern),
                Song.artist_name.ilike(search_pattern),
                Song.genre.ilike(search_pattern),
                Song.mood.ilike(search_pattern),
            )
        )

        if user_id:
            query = query.where(Song.user_id == user_id)
        else:
            # Only show public songs for general search
            query = query.where(Song.is_public == True)  # noqa: E712

        query = query.order_by(desc(Song.created_at)).offset(skip).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def create(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        obj_in: CompleteSongGenerationRequest | SongFromLyricsRequest,
        lyrics_id: Optional[uuid.UUID] = None,
    ) -> Song:
        """Create a new song."""
        song = Song(
            user_id=user_id,
            lyrics_id=lyrics_id,
            title=obj_in.title or "Untitled Song",
            artist_name=obj_in.artist_name,
            genre=obj_in.genre,
            mood=obj_in.mood,
            bpm=obj_in.bpm,
            key=obj_in.key,
            music_style=obj_in.music_style,
            vocal_pitch_shift=obj_in.vocal_pitch_shift,
            vocal_effects=obj_in.vocal_effects,
            music_params={
                "duration_seconds": obj_in.duration_seconds,
                "bpm": obj_in.bpm,
                "key": obj_in.key,
            },
            generation_status="pending",
            is_public=obj_in.is_public,
        )

        db.add(song)
        await db.commit()
        await db.refresh(song)
        return song

    async def update(
        self,
        db: AsyncSession,
        song_id: uuid.UUID,
        obj_in: UpdateSongSettingsRequest,
    ) -> Optional[Song]:
        """Update song settings."""
        song = await self.get(db, song_id)
        if not song:
            return None

        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(song, field, value)

        song.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(song)
        return song

    async def update_status(
        self,
        db: AsyncSession,
        song_id: uuid.UUID,
        status: str,
        completed: bool = False,
    ) -> Optional[Song]:
        """Update song generation status."""
        song = await self.get(db, song_id)
        if not song:
            return None

        song.generation_status = status
        song.updated_at = datetime.utcnow()

        if completed:
            song.completed_at = datetime.utcnow()

        await db.commit()
        await db.refresh(song)
        return song

    async def update_file_references(
        self,
        db: AsyncSession,
        song_id: uuid.UUID,
        final_audio_file_id: Optional[uuid.UUID] = None,
        vocal_track_file_id: Optional[uuid.UUID] = None,
        instrumental_track_file_id: Optional[uuid.UUID] = None,
    ) -> Optional[Song]:
        """Update song file references."""
        song = await self.get(db, song_id)
        if not song:
            return None

        if final_audio_file_id:
            song.final_audio_file_id = final_audio_file_id
        if vocal_track_file_id:
            song.vocal_track_file_id = vocal_track_file_id
        if instrumental_track_file_id:
            song.instrumental_track_file_id = instrumental_track_file_id

        song.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(song)
        return song

    async def increment_play_count(
        self,
        db: AsyncSession,
        song_id: uuid.UUID,
    ) -> Optional[Song]:
        """Increment play count."""
        song = await self.get(db, song_id)
        if not song:
            return None

        song.play_count += 1
        await db.commit()
        await db.refresh(song)
        return song

    async def increment_download_count(
        self,
        db: AsyncSession,
        song_id: uuid.UUID,
    ) -> Optional[Song]:
        """Increment download count."""
        song = await self.get(db, song_id)
        if not song:
            return None

        song.download_count += 1
        await db.commit()
        await db.refresh(song)
        return song

    async def increment_like_count(
        self,
        db: AsyncSession,
        song_id: uuid.UUID,
    ) -> Optional[Song]:
        """Increment like count."""
        song = await self.get(db, song_id)
        if not song:
            return None

        song.like_count += 1
        await db.commit()
        await db.refresh(song)
        return song

    async def delete(self, db: AsyncSession, song_id: uuid.UUID) -> bool:
        """Delete song."""
        song = await self.get(db, song_id)
        if not song:
            return False

        await db.delete(song)
        await db.commit()
        return True

    async def get_popular(
        self,
        db: AsyncSession,
        limit: int = 10,
        days: int = 7,
    ) -> List[Song]:
        """Get popular songs (by play count in recent days)."""
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        query = (
            select(Song)
            .where(
                and_(
                    Song.is_public == True,  # noqa: E712
                    Song.generation_status == "completed",
                    Song.created_at >= cutoff_date,
                )
            )
            .order_by(desc(Song.play_count))
            .limit(limit)
        )

        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_trending(
        self,
        db: AsyncSession,
        limit: int = 10,
    ) -> List[Song]:
        """Get trending songs (recent + high engagement)."""
        # Simple trending algorithm: recent songs with high engagement
        query = (
            select(Song)
            .where(
                and_(
                    Song.is_public == True,  # noqa: E712
                    Song.generation_status == "completed",
                )
            )
            .order_by(
                desc(Song.play_count + Song.like_count * 2 + Song.share_count * 3),
                desc(Song.created_at),
            )
            .limit(limit)
        )

        result = await db.execute(query)
        return list(result.scalars().all())


# Singleton instance
crud_song = CRUDSong()
