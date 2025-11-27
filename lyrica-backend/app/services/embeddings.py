"""
Embedding Service
Handles text embeddings using sentence-transformers with caching.
"""

import hashlib
from typing import List, Optional

from loguru import logger
from sentence_transformers import SentenceTransformer

from app.core.config import settings


class EmbeddingService:
    """Service for generating text embeddings with caching."""

    def __init__(self):
        """Initialize the embedding service."""
        self.model_name = settings.embedding_model
        self.dimension = settings.embedding_dimension
        self._model: Optional[SentenceTransformer] = None
        self._cache: dict = {}  # Simple in-memory cache
        logger.info(f"Initializing embedding service with model: {self.model_name}")

    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the embedding model."""
        if self._model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            logger.info(
                f"Embedding model loaded. Dimension: {self._model.get_sentence_embedding_dimension()}"
            )
        return self._model

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key from text."""
        return hashlib.md5(text.encode()).hexdigest()

    async def embed_text(self, text: str, use_cache: bool = True) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed
            use_cache: Whether to use cache

        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return [0.0] * self.dimension

        # Check cache
        if use_cache:
            cache_key = self._get_cache_key(text)
            if cache_key in self._cache:
                logger.debug(f"Cache hit for text: {text[:50]}...")
                return self._cache[cache_key]

        # Generate embedding
        try:
            embedding = self.model.encode(text, convert_to_tensor=False).tolist()

            # Cache the result
            if use_cache:
                cache_key = self._get_cache_key(text)
                self._cache[cache_key] = embedding
                logger.debug(f"Cached embedding for text: {text[:50]}...")

            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    async def embed_texts(
        self, texts: List[str], use_cache: bool = True, batch_size: int = 32
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed
            use_cache: Whether to use cache
            batch_size: Batch size for processing

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        embeddings = []
        uncached_texts = []
        uncached_indices = []

        # Check cache for each text
        for i, text in enumerate(texts):
            if not text or not text.strip():
                embeddings.append([0.0] * self.dimension)
                continue

            if use_cache:
                cache_key = self._get_cache_key(text)
                if cache_key in self._cache:
                    embeddings.append(self._cache[cache_key])
                    continue

            uncached_texts.append(text)
            uncached_indices.append(i)
            embeddings.append(None)  # Placeholder

        # Generate embeddings for uncached texts
        if uncached_texts:
            try:
                logger.info(f"Generating embeddings for {len(uncached_texts)} texts")
                new_embeddings = self.model.encode(
                    uncached_texts, batch_size=batch_size, convert_to_tensor=False
                ).tolist()

                # Update results and cache
                for idx, text, embedding in zip(uncached_indices, uncached_texts, new_embeddings):
                    embeddings[idx] = embedding
                    if use_cache:
                        cache_key = self._get_cache_key(text)
                        self._cache[cache_key] = embedding

            except Exception as e:
                logger.error(f"Error generating batch embeddings: {e}")
                raise

        return embeddings

    def clear_cache(self):
        """Clear the embedding cache."""
        self._cache.clear()
        logger.info("Embedding cache cleared")

    def get_cache_size(self) -> int:
        """Get the number of cached embeddings."""
        return len(self._cache)


# Global embedding service instance
embedding_service = EmbeddingService()
