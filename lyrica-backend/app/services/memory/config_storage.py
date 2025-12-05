"""
Configuration storage service for memory system.

Stores and retrieves mixing configurations with Redis caching.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mixing_config import MixingConfiguration, ReferenceTrack
from app.services.cache import cache_service


class ConfigurationStorageService:
    """Service for storing and retrieving mixing configurations."""

    def __init__(self):
        """Initialize configuration storage service."""
        self.cache_prefix = "mixing_config"
        self.cache_ttl = 3600  # 1 hour
        logger.success("ConfigurationStorageService initialized")

    async def save_configuration(
        self,
        db: AsyncSession,
        config_type: str,
        eq_settings: dict,
        compression_settings: dict,
        stereo_width_settings: dict,
        reverb_settings: dict,
        delay_settings: dict,
        sidechain_settings: dict,
        user_id: Optional[uuid.UUID] = None,
        song_id: Optional[uuid.UUID] = None,
        genre: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_default: bool = False,
        is_public: bool = False,
    ) -> MixingConfiguration:
        """
        Save mixing configuration to database.

        Args:
            db: Database session
            config_type: Configuration type ('manual', 'genre_preset', 'reference_match')
            eq_settings: EQ settings dictionary
            compression_settings: Compression settings dictionary
            stereo_width_settings: Stereo width settings dictionary
            reverb_settings: Reverb settings dictionary
            delay_settings: Delay settings dictionary
            sidechain_settings: Sidechain compression settings dictionary
            user_id: Optional user ID
            song_id: Optional song ID
            genre: Optional genre
            name: Optional configuration name
            description: Optional description
            is_default: Whether this is a default configuration
            is_public: Whether this configuration is public

        Returns:
            Saved MixingConfiguration instance
        """
        logger.info(f"Saving mixing configuration: type={config_type}, genre={genre}")

        config = MixingConfiguration(
            user_id=user_id,
            song_id=song_id,
            config_type=config_type,
            genre=genre,
            eq_settings=eq_settings,
            compression_settings=compression_settings,
            stereo_width_settings=stereo_width_settings,
            reverb_settings=reverb_settings,
            delay_settings=delay_settings,
            sidechain_settings=sidechain_settings,
            name=name,
            description=description,
            is_default=is_default,
            is_public=is_public,
        )

        db.add(config)
        await db.commit()
        await db.refresh(config)

        # Cache the configuration
        await self._cache_configuration(config)

        logger.success(f"Configuration saved: {config.id}")
        return config

    async def get_configuration(
        self, db: AsyncSession, config_id: uuid.UUID
    ) -> Optional[MixingConfiguration]:
        """
        Get mixing configuration by ID.

        Args:
            db: Database session
            config_id: Configuration ID

        Returns:
            MixingConfiguration instance or None
        """
        # Try cache first
        cached = await self._get_cached_configuration(config_id)
        if cached:
            logger.info(f"Configuration retrieved from cache: {config_id}")
            return cached

        # Get from database
        logger.info(f"Retrieving configuration from database: {config_id}")
        result = await db.execute(
            select(MixingConfiguration).where(MixingConfiguration.id == config_id)
        )
        config = result.scalar_one_or_none()

        if config:
            # Cache for future use
            await self._cache_configuration(config)

        return config

    async def get_configurations_by_genre(
        self, db: AsyncSession, genre: str, user_id: Optional[uuid.UUID] = None
    ) -> list[MixingConfiguration]:
        """
        Get configurations by genre.

        Args:
            db: Database session
            genre: Genre name
            user_id: Optional user ID to filter user-specific configs

        Returns:
            List of MixingConfiguration instances
        """
        logger.info(f"Retrieving configurations for genre: {genre}")

        query = select(MixingConfiguration).where(MixingConfiguration.genre == genre)

        if user_id:
            query = query.where(
                (MixingConfiguration.user_id == user_id) | (MixingConfiguration.is_public == True)
            )
        else:
            query = query.where(MixingConfiguration.is_public == True)

        result = await db.execute(query)
        configs = result.scalars().all()

        logger.info(f"Found {len(configs)} configurations for genre {genre}")
        return list(configs)

    async def get_default_configuration(
        self, db: AsyncSession, genre: Optional[str] = None
    ) -> Optional[MixingConfiguration]:
        """
        Get default configuration for a genre.

        Args:
            db: Database session
            genre: Optional genre to filter by

        Returns:
            Default MixingConfiguration or None
        """
        logger.info(f"Retrieving default configuration for genre: {genre}")

        query = select(MixingConfiguration).where(MixingConfiguration.is_default == True)

        if genre:
            query = query.where(MixingConfiguration.genre == genre)

        result = await db.execute(query.order_by(MixingConfiguration.usage_count.desc()))
        config = result.scalar_one_or_none()

        return config

    async def update_configuration_usage(self, db: AsyncSession, config_id: uuid.UUID) -> None:
        """
        Update configuration usage statistics.

        Args:
            db: Database session
            config_id: Configuration ID
        """
        config = await self.get_configuration(db, config_id)
        if config:
            config.usage_count += 1
            config.last_used_at = datetime.utcnow()
            await db.commit()
            await db.refresh(config)

            # Update cache
            await self._cache_configuration(config)

    async def _cache_configuration(self, config: MixingConfiguration) -> None:
        """Cache configuration in Redis."""
        cache_key = f"{self.cache_prefix}:{config.id}"
        config_dict = {
            "id": str(config.id),
            "user_id": str(config.user_id) if config.user_id else None,
            "song_id": str(config.song_id) if config.song_id else None,
            "config_type": config.config_type,
            "genre": config.genre,
            "eq_settings": config.eq_settings,
            "compression_settings": config.compression_settings,
            "stereo_width_settings": config.stereo_width_settings,
            "reverb_settings": config.reverb_settings,
            "delay_settings": config.delay_settings,
            "sidechain_settings": config.sidechain_settings,
            "name": config.name,
            "description": config.description,
            "is_default": config.is_default,
            "is_public": config.is_public,
            "usage_count": config.usage_count,
        }
        await cache_service.set(cache_key, config_dict, ttl=self.cache_ttl)

    async def _get_cached_configuration(
        self, config_id: uuid.UUID
    ) -> Optional[MixingConfiguration]:
        """Get configuration from cache."""
        cache_key = f"{self.cache_prefix}:{config_id}"
        cached = await cache_service.get(cache_key)
        if cached:
            # Convert dict back to model-like object
            # Note: This is a simplified version - in production, you'd want proper deserialization
            return cached
        return None


class ReferenceTrackStorageService:
    """Service for storing and retrieving reference track analyses."""

    def __init__(self):
        """Initialize reference track storage service."""
        self.cache_prefix = "reference_track"
        self.cache_ttl = 7200  # 2 hours
        logger.success("ReferenceTrackStorageService initialized")

    async def save_reference_track(
        self,
        db: AsyncSession,
        title: str,
        audio_file_path: Path,
        frequency_analysis: dict,
        stereo_width_analysis: dict,
        dynamic_range: float,
        avg_loudness: float,
        eq_profile: dict,
        recommendations: list[dict],
        user_id: Optional[uuid.UUID] = None,
        audio_file_id: Optional[uuid.UUID] = None,
        artist: Optional[str] = None,
        album: Optional[str] = None,
        genre: Optional[str] = None,
        description: Optional[str] = None,
        is_public: bool = False,
    ) -> ReferenceTrack:
        """
        Save reference track analysis to database.

        Args:
            db: Database session
            title: Track title
            audio_file_path: Path to audio file
            frequency_analysis: Frequency analysis results
            stereo_width_analysis: Stereo width analysis results
            dynamic_range: Dynamic range value
            avg_loudness: Average loudness value
            eq_profile: EQ profile dictionary
            recommendations: List of mixing recommendations
            user_id: Optional user ID
            audio_file_id: Optional audio file ID
            artist: Optional artist name
            album: Optional album name
            genre: Optional genre
            description: Optional description
            is_public: Whether this reference track is public

        Returns:
            Saved ReferenceTrack instance
        """
        logger.info(f"Saving reference track: {title}")

        reference = ReferenceTrack(
            user_id=user_id,
            title=title,
            artist=artist,
            album=album,
            genre=genre,
            audio_file_path=str(audio_file_path),
            audio_file_id=audio_file_id,
            frequency_analysis=frequency_analysis,
            stereo_width_analysis=stereo_width_analysis,
            dynamic_range=dynamic_range,
            avg_loudness=avg_loudness,
            eq_profile=eq_profile,
            recommendations=recommendations,
            description=description,
            is_public=is_public,
        )

        db.add(reference)
        await db.commit()
        await db.refresh(reference)

        # Cache the reference track
        await self._cache_reference_track(reference)

        logger.success(f"Reference track saved: {reference.id}")
        return reference

    async def get_reference_track(
        self, db: AsyncSession, reference_id: uuid.UUID
    ) -> Optional[ReferenceTrack]:
        """
        Get reference track by ID.

        Args:
            db: Database session
            reference_id: Reference track ID

        Returns:
            ReferenceTrack instance or None
        """
        # Try cache first
        cached = await self._get_cached_reference_track(reference_id)
        if cached:
            logger.info(f"Reference track retrieved from cache: {reference_id}")
            return cached

        # Get from database
        logger.info(f"Retrieving reference track from database: {reference_id}")
        result = await db.execute(select(ReferenceTrack).where(ReferenceTrack.id == reference_id))
        reference = result.scalar_one_or_none()

        if reference:
            # Cache for future use
            await self._cache_reference_track(reference)

        return reference

    async def get_reference_tracks_by_genre(
        self, db: AsyncSession, genre: str, user_id: Optional[uuid.UUID] = None
    ) -> list[ReferenceTrack]:
        """
        Get reference tracks by genre.

        Args:
            db: Database session
            genre: Genre name
            user_id: Optional user ID to filter user-specific tracks

        Returns:
            List of ReferenceTrack instances
        """
        logger.info(f"Retrieving reference tracks for genre: {genre}")

        query = select(ReferenceTrack).where(ReferenceTrack.genre == genre)

        if user_id:
            query = query.where(
                (ReferenceTrack.user_id == user_id) | (ReferenceTrack.is_public == True)
            )
        else:
            query = query.where(ReferenceTrack.is_public == True)

        result = await db.execute(query.order_by(ReferenceTrack.usage_count.desc()))
        tracks = result.scalars().all()

        logger.info(f"Found {len(tracks)} reference tracks for genre {genre}")
        return list(tracks)

    async def update_reference_track_usage(self, db: AsyncSession, reference_id: uuid.UUID) -> None:
        """
        Update reference track usage statistics.

        Args:
            db: Database session
            reference_id: Reference track ID
        """
        reference = await self.get_reference_track(db, reference_id)
        if reference:
            reference.usage_count += 1
            await db.commit()
            await db.refresh(reference)

            # Update cache
            await self._cache_reference_track(reference)

    async def _cache_reference_track(self, reference: ReferenceTrack) -> None:
        """Cache reference track in Redis."""
        cache_key = f"{self.cache_prefix}:{reference.id}"
        reference_dict = {
            "id": str(reference.id),
            "user_id": str(reference.user_id) if reference.user_id else None,
            "title": reference.title,
            "artist": reference.artist,
            "album": reference.album,
            "genre": reference.genre,
            "audio_file_path": reference.audio_file_path,
            "frequency_analysis": reference.frequency_analysis,
            "stereo_width_analysis": reference.stereo_width_analysis,
            "dynamic_range": reference.dynamic_range,
            "avg_loudness": reference.avg_loudness,
            "eq_profile": reference.eq_profile,
            "recommendations": reference.recommendations,
        }
        await cache_service.set(cache_key, reference_dict, ttl=self.cache_ttl)

    async def _get_cached_reference_track(self, reference_id: uuid.UUID) -> Optional[dict]:
        """Get reference track from cache."""
        cache_key = f"{self.cache_prefix}:{reference_id}"
        return await cache_service.get(cache_key)


# Singleton instances
_config_storage_service: Optional[ConfigurationStorageService] = None
_reference_storage_service: Optional[ReferenceTrackStorageService] = None


def get_config_storage() -> ConfigurationStorageService:
    """Get or create configuration storage service instance."""
    global _config_storage_service
    if _config_storage_service is None:
        _config_storage_service = ConfigurationStorageService()
    return _config_storage_service


def get_reference_storage() -> ReferenceTrackStorageService:
    """Get or create reference track storage service instance."""
    global _reference_storage_service
    if _reference_storage_service is None:
        _reference_storage_service = ReferenceTrackStorageService()
    return _reference_storage_service
