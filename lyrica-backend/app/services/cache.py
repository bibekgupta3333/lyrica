"""
Redis Cache Service
Provides caching functionality for embeddings and expensive operations.
"""

import hashlib
import json
from typing import Any, List, Optional

import redis.asyncio as redis
from loguru import logger

from app.core.config import settings


class CacheService:
    """Service for Redis-based caching."""

    def __init__(self):
        """Initialize cache service."""
        self._redis: Optional[redis.Redis] = None
        self.ttl = 3600  # Default TTL: 1 hour
        logger.info("Cache service initialized")

    async def get_redis(self) -> redis.Redis:
        """Get or create Redis connection."""
        if self._redis is None:
            logger.info(f"Connecting to Redis: {settings.redis_url}")
            self._redis = await redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=settings.redis_max_connections,
            )
            logger.info("Redis connection established")
        return self._redis

    async def close(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            logger.info("Redis connection closed")

    def _generate_key(self, prefix: str, *args) -> str:
        """Generate cache key from prefix and arguments."""
        key_parts = [str(arg) for arg in args]
        key_string = ":".join(key_parts)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"{prefix}:{key_hash}"

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        try:
            client = await self.get_redis()
            value = await client.get(key)

            if value:
                logger.debug(f"Cache hit: {key}")
                return json.loads(value)

            logger.debug(f"Cache miss: {key}")
            return None

        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None = use default)

        Returns:
            True if successful
        """
        try:
            client = await self.get_redis()
            serialized = json.dumps(value)
            expire = ttl if ttl is not None else self.ttl

            await client.setex(key, expire, serialized)
            logger.debug(f"Cache set: {key} (TTL: {expire}s)")
            return True

        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if successful
        """
        try:
            client = await self.get_redis()
            await client.delete(key)
            logger.debug(f"Cache deleted: {key}")
            return True

        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists
        """
        try:
            client = await self.get_redis()
            return await client.exists(key) > 0

        except Exception as e:
            logger.error(f"Error checking cache existence: {e}")
            return False

    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Get cached embedding for text.

        Args:
            text: Text to get embedding for

        Returns:
            Cached embedding or None
        """
        key = self._generate_key("embedding", text)
        return await self.get(key)

    async def set_embedding(
        self, text: str, embedding: List[float], ttl: Optional[int] = None
    ) -> bool:
        """
        Cache embedding for text.

        Args:
            text: Text that was embedded
            embedding: Embedding vector
            ttl: Time to live (None = use default)

        Returns:
            True if successful
        """
        key = self._generate_key("embedding", text)
        return await self.set(key, embedding, ttl)

    async def get_search_results(
        self, query: str, filters: Optional[dict] = None
    ) -> Optional[dict]:
        """
        Get cached search results.

        Args:
            query: Search query
            filters: Search filters

        Returns:
            Cached results or None
        """
        key = self._generate_key("search", query, json.dumps(filters or {}))
        return await self.get(key)

    async def set_search_results(
        self, query: str, filters: Optional[dict], results: dict, ttl: int = 300
    ) -> bool:
        """
        Cache search results.

        Args:
            query: Search query
            filters: Search filters
            results: Search results
            ttl: Time to live (default: 5 minutes)

        Returns:
            True if successful
        """
        key = self._generate_key("search", query, json.dumps(filters or {}))
        return await self.set(key, results, ttl)

    async def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching pattern.

        Args:
            pattern: Redis key pattern (e.g., "embedding:*")

        Returns:
            Number of keys deleted
        """
        try:
            client = await self.get_redis()
            keys = []
            async for key in client.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                deleted = await client.delete(*keys)
                logger.info(f"Cleared {deleted} keys matching pattern: {pattern}")
                return deleted

            return 0

        except Exception as e:
            logger.error(f"Error clearing cache pattern: {e}")
            return 0

    async def get_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        try:
            client = await self.get_redis()
            info = await client.info("stats")

            return {
                "total_connections_received": info.get("total_connections_received", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": (
                    info.get("keyspace_hits", 0)
                    / max(
                        info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0),
                        1,
                    )
                ),
            }

        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}


# Global cache service instance
cache_service = CacheService()
