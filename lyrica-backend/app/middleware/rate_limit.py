"""
Rate limiting middleware using Redis.

This module implements rate limiting to prevent abuse and ensure
fair resource allocation across users.
"""

import time
from typing import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.services.cache import cache_service


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using Redis for distributed rate limiting.

    Implements sliding window rate limiting per IP address and user.
    """

    def __init__(self, app, calls: int = 60, period: int = 60):
        """
        Initialize rate limiter.

        Args:
            app: FastAPI application
            calls: Number of calls allowed per period
            period: Time period in seconds (default: 60 seconds)
        """
        super().__init__(app)
        self.calls = calls
        self.period = period

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and check rate limit.

        Args:
            request: HTTP request
            call_next: Next middleware/endpoint

        Returns:
            HTTP response (or 429 if rate limited)
        """
        # Skip rate limiting for health checks
        if request.url.path.startswith("/api/v1/health"):
            return await call_next(request)

        # Get client identifier (IP address or user ID)
        client_id = self._get_client_id(request)

        # Check rate limit
        is_allowed, retry_after = await self._check_rate_limit(client_id)

        if not is_allowed:
            logger.warning(f"Rate limit exceeded for {client_id} on {request.url.path}")

            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Too Many Requests",
                    "message": f"Rate limit exceeded. Try again in {retry_after} seconds.",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        remaining = await self._get_remaining(client_id)
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + self.period)

        return response

    def _get_client_id(self, request: Request) -> str:
        """
        Get unique identifier for client.

        Uses user ID if authenticated, otherwise IP address.

        Args:
            request: HTTP request

        Returns:
            Client identifier string
        """
        # Try to get user ID from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"

        # Fall back to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Get first IP in case of multiple proxies
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        return f"ip:{client_ip}"

    async def _check_rate_limit(self, client_id: str) -> tuple[bool, int]:
        """
        Check if client has exceeded rate limit.

        Args:
            client_id: Client identifier

        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        key = f"rate_limit:{client_id}"
        current_time = int(time.time())
        window_start = current_time - self.period

        try:
            # Get or initialize counter
            cached = await cache_service.get(key)

            if cached is None:
                # First request in window
                await cache_service.set(
                    key, {"count": 1, "window_start": current_time}, ttl=self.period
                )
                return True, 0

            # Parse cached data
            count = cached.get("count", 0)
            window_start_cached = cached.get("window_start", current_time)

            # Check if window has expired
            if current_time - window_start_cached >= self.period:
                # Reset window
                await cache_service.set(
                    key, {"count": 1, "window_start": current_time}, ttl=self.period
                )
                return True, 0

            # Check if limit exceeded
            if count >= self.calls:
                retry_after = self.period - (current_time - window_start_cached)
                return False, retry_after

            # Increment counter
            await cache_service.set(
                key,
                {"count": count + 1, "window_start": window_start_cached},
                ttl=self.period,
            )

            return True, 0

        except Exception as e:
            logger.error(f"Rate limit check error: {str(e)}")
            # Allow request on error (fail open)
            return True, 0

    async def _get_remaining(self, client_id: str) -> int:
        """
        Get remaining requests in current window.

        Args:
            client_id: Client identifier

        Returns:
            Number of remaining requests
        """
        key = f"rate_limit:{client_id}"

        try:
            cached = await cache_service.get(key)
            if cached is None:
                return self.calls

            count = cached.get("count", 0)
            return max(0, self.calls - count)

        except Exception:
            return self.calls


def create_rate_limiter(calls: int = None, period: int = 60):
    """
    Factory function to create rate limiter with custom limits.

    Args:
        calls: Number of calls allowed (default: from settings)
        period: Time period in seconds (default: 60)

    Returns:
        RateLimitMiddleware instance
    """
    if calls is None:
        calls = settings.rate_limit_per_minute

    def _create_middleware(app):
        return RateLimitMiddleware(app, calls=calls, period=period)

    return _create_middleware
