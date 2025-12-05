"""
Audio feature vector service for ChromaDB.

Stores and retrieves audio feature vectors for similarity search.
"""

import uuid
from pathlib import Path
from typing import Optional

import numpy as np
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mixing_config import AudioFeatureVector
from app.services.production.frequency_balancing import get_frequency_analysis
from app.services.vector_store import vector_store


class AudioFeatureVectorService:
    """Service for storing and retrieving audio feature vectors."""

    def __init__(self):
        """Initialize audio feature vector service."""
        self.collection_name = "audio_features"
        self._collection = None
        logger.success("AudioFeatureVectorService initialized")

    @property
    def collection(self):
        """Get or create ChromaDB collection for audio features."""
        if self._collection is None:
            try:
                self._collection = vector_store.client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={
                        "description": "Audio feature vectors for similarity search",
                        "dimension": 384,  # MFCC + spectral features
                    },
                )
                logger.info(f"Audio features collection ready ({self._collection.count()} vectors)")
            except Exception as e:
                logger.error(f"Failed to get/create audio features collection: {e}")
                raise
        return self._collection

    async def extract_and_store_features(
        self,
        db: AsyncSession,
        audio_file_id: uuid.UUID,
        audio_path: Path,
        feature_type: str = "full",
        reference_track_id: Optional[uuid.UUID] = None,
    ) -> AudioFeatureVector:
        """
        Extract audio features and store in database and ChromaDB.

        Args:
            db: Database session
            audio_file_id: Audio file ID
            audio_path: Path to audio file
            feature_type: Feature type ('frequency', 'spectral', 'rhythm', 'full')
            reference_track_id: Optional reference track ID

        Returns:
            AudioFeatureVector instance
        """
        logger.info(f"Extracting features from: {audio_path} (type: {feature_type})")

        # Get frequency analysis
        freq_analysis = get_frequency_analysis()
        analysis = freq_analysis.analyze_frequency_content(audio_path)

        # Extract features
        import librosa

        y, sr = librosa.load(str(audio_path), sr=None)

        # Extract tempo
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

        # Extract MFCC features (13 coefficients)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfcc_mean = mfcc.mean(axis=1).tolist()

        # Create feature vector (combine MFCC + spectral features)
        feature_vector = mfcc_mean + [
            analysis["spectral_centroid"],
            analysis["spectral_rolloff"],
            analysis["spectral_bandwidth"],
            analysis["zero_crossing_rate"],
        ]

        # Store in ChromaDB
        chromadb_id = str(uuid.uuid4())
        self.collection.add(
            embeddings=[feature_vector],
            ids=[chromadb_id],
            metadatas=[
                {
                    "audio_file_id": str(audio_file_id),
                    "feature_type": feature_type,
                    "tempo": float(tempo),
                    "genre": analysis.get("genre"),
                }
            ],
        )

        # Store in database
        feature_record = AudioFeatureVector(
            audio_file_id=audio_file_id,
            reference_track_id=reference_track_id,
            chromadb_id=chromadb_id,
            vector_dimension=len(feature_vector),
            feature_type=feature_type,
            tempo=float(tempo),
            spectral_centroid=analysis["spectral_centroid"],
            spectral_rolloff=analysis["spectral_rolloff"],
            zero_crossing_rate=analysis["zero_crossing_rate"],
            mfcc_features=mfcc_mean,
            frequency_bands=analysis["frequency_bands"],
            sample_rate=sr,
            duration=len(y) / sr,
        )

        db.add(feature_record)
        await db.commit()
        await db.refresh(feature_record)

        logger.success(f"Audio features stored: {feature_record.id} (ChromaDB: {chromadb_id})")
        return feature_record

    async def find_similar_audio(
        self,
        query_audio_path: Path,
        n_results: int = 5,
        genre: Optional[str] = None,
    ) -> list[dict]:
        """
        Find similar audio files using feature vectors.

        Args:
            query_audio_path: Path to query audio file
            n_results: Number of results to return
            genre: Optional genre filter

        Returns:
            List of similar audio results with metadata
        """
        logger.info(f"Finding similar audio to: {query_audio_path}")

        # Extract features from query audio
        freq_analysis = get_frequency_analysis()
        analysis = freq_analysis.analyze_frequency_content(query_audio_path)

        import librosa

        y, sr = librosa.load(str(query_audio_path), sr=None)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfcc_mean = mfcc.mean(axis=1).tolist()

        query_vector = mfcc_mean + [
            analysis["spectral_centroid"],
            analysis["spectral_rolloff"],
            analysis["spectral_bandwidth"],
            analysis["zero_crossing_rate"],
        ]

        # Search ChromaDB
        where = {"genre": genre} if genre else None
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=n_results,
            where=where,
            include=["metadatas", "distances"],
        )

        # Format results
        similar_audio = []
        if results["ids"] and len(results["ids"][0]) > 0:
            for i, chromadb_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else None

                similar_audio.append(
                    {
                        "chromadb_id": chromadb_id,
                        "audio_file_id": metadata.get("audio_file_id"),
                        "feature_type": metadata.get("feature_type"),
                        "tempo": metadata.get("tempo"),
                        "genre": metadata.get("genre"),
                        "similarity": 1.0 - distance if distance else None,
                    }
                )

        logger.info(f"Found {len(similar_audio)} similar audio files")
        return similar_audio

    async def get_feature_vector(
        self, db: AsyncSession, audio_file_id: uuid.UUID
    ) -> Optional[AudioFeatureVector]:
        """
        Get feature vector by audio file ID.

        Args:
            db: Database session
            audio_file_id: Audio file ID

        Returns:
            AudioFeatureVector instance or None
        """
        result = await db.execute(
            select(AudioFeatureVector).where(AudioFeatureVector.audio_file_id == audio_file_id)
        )
        return result.scalar_one_or_none()

    def count_vectors(self) -> int:
        """Get total number of feature vectors in ChromaDB."""
        return self.collection.count()


# Singleton instance
_audio_feature_service: Optional[AudioFeatureVectorService] = None


def get_audio_feature_service() -> AudioFeatureVectorService:
    """Get or create audio feature vector service instance."""
    global _audio_feature_service
    if _audio_feature_service is None:
        _audio_feature_service = AudioFeatureVectorService()
    return _audio_feature_service
