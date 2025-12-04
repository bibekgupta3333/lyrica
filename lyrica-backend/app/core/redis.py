"""
Redis Client Module
Provides Redis connection management for the application.
"""

from typing import Optional

import redis.asyncio as redis
from loguru import logger

from app.core.config import settings


class RedisClient:
    """Redis client manager with connection pooling."""

    def __init__(self):
        """Initialize Redis client manager."""
        self._redis: Optional[redis.Redis] = None
        self._pool: Optional[redis.ConnectionPool] = None

    async def connect(self) -> redis.Redis:
        """
        Establish Redis connection.

        Returns:
            Redis client instance
        """
        if self._redis is None:
            try:
                logger.info(f"Connecting to Redis at {settings.redis_url}")

                # Create connection pool
                self._pool = redis.ConnectionPool.from_url(
                    settings.redis_url,
                    max_connections=settings.redis_max_connections,
                    decode_responses=settings.redis_decode_responses,
                    encoding="utf-8",
                )

                # Create Redis client
                self._redis = redis.Redis(connection_pool=self._pool)

                # Test connection
                await self._redis.ping()

                logger.info("Redis connection established successfully")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise

        return self._redis

    async def disconnect(self) -> None:
        """Close Redis connection and cleanup resources."""
        if self._redis:
            try:
                await self._redis.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")
            finally:
                self._redis = None

        if self._pool:
            try:
                await self._pool.disconnect()
                logger.info("Redis connection pool closed")
            except Exception as e:
                logger.error(f"Error closing Redis pool: {e}")
            finally:
                self._pool = None

    async def health_check(self) -> bool:
        """
        Check if Redis is healthy.

        Returns:
            True if Redis is responding, False otherwise
        """
        try:
            if self._redis is None:
                return False

            await self._redis.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False

    @property
    def client(self) -> Optional[redis.Redis]:
        """Get the Redis client instance."""
        return self._redis


# Global Redis client instance
redis_client = RedisClient()
