"""
Middleware Configuration
Custom middleware for request/response processing.
"""

import time
import uuid
from typing import Callable, Tuple, cast

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID to each request."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with unique ID."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        result = await call_next(request)
        response: Response = cast(Response, result)
        response.headers["X-Request-ID"] = request_id

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response details."""
        start_time = time.time()
        request_id = getattr(request.state, "request_id", "unknown")

        # Log request
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client_host": request.client.host if request.client else None,
            },
        )

        # Process request
        try:
            result = await call_next(request)
            response: Response = cast(Response, result)

            # Calculate processing time
            process_time = time.time() - start_time

            # Log response
            logger.info(
                f"Request completed: {request.method} {request.url.path} - {response.status_code}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time": f"{process_time:.3f}s",
                },
            )

            # Add processing time header
            response.headers["X-Process-Time"] = f"{process_time:.3f}"

            return response

        except Exception as e:
            process_time = time.time() - start_time

            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "process_time": f"{process_time:.3f}s",
                },
            )
            raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Redis-based rate limiting middleware.

    Implements sliding window rate limiting per IP address and user.
    Uses Redis for distributed rate limiting across multiple instances.
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
        from fastapi import status
        from fastapi.responses import JSONResponse

        # Skip rate limiting for health checks and metrics
        if request.url.path.startswith("/api/v1/health") or request.url.path.startswith("/metrics"):
            result = await call_next(request)
            return cast(Response, result)

        # Get client identifier (IP address or user ID)
        client_id = self._get_client_id(request)

        # Check rate limit
        is_allowed, retry_after = await self._check_rate_limit(client_id)

        if not is_allowed:
            logger.warning(
                f"Rate limit exceeded for {client_id} on {request.url.path}",
                extra={
                    "client_id": client_id,
                    "path": request.url.path,
                    "method": request.method,
                },
            )

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
        response: Response = await call_next(request)

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

    async def _check_rate_limit(self, client_id: str) -> Tuple[bool, int]:
        """
        Check if client has exceeded rate limit using Redis.

        Args:
            client_id: Client identifier

        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        from app.core.redis import redis_client

        key = f"rate_limit:{client_id}"
        current_time = int(time.time())
        window_start = current_time - self.period

        try:
            redis = await redis_client.connect()

            # Use Redis sliding window with sorted set
            # Remove old entries outside the window
            await redis.zremrangebyscore(key, 0, window_start)

            # Count current requests in window
            count: int = int(await redis.zcard(key))

            # Check if limit exceeded
            if count >= self.calls:
                # Get oldest entry to calculate retry_after
                oldest: list = await redis.zrange(key, 0, 0, withscores=True)
                if oldest and len(oldest) > 0:
                    # oldest[0] is a tuple: (member, score)
                    oldest_entry: Tuple[str, float] = oldest[0]
                    oldest_time = int(oldest_entry[1])
                    retry_after = self.period - (current_time - oldest_time)
                else:
                    retry_after = self.period

                # Set expiration on the key
                await redis.expire(key, self.period)
                return False, max(1, retry_after)

            # Add current request to sorted set
            await redis.zadd(key, {str(current_time): current_time})
            await redis.expire(key, self.period)

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
        from app.core.redis import redis_client

        key = f"rate_limit:{client_id}"
        current_time = int(time.time())
        window_start = current_time - self.period

        try:
            redis = await redis_client.connect()

            # Remove old entries
            await redis.zremrangebyscore(key, 0, window_start)

            # Count current requests
            count: int = int(await redis.zcard(key))

            return max(0, self.calls - count)

        except Exception:
            return self.calls
