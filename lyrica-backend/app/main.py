"""
Lyrica Backend - Main Application
FastAPI application entry point.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app

from app import __version__
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import logger, setup_logging
from app.core.middleware import LoggingMiddleware, RateLimitMiddleware, RequestIDMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Manages startup and shutdown events.
    """
    # Startup
    logger.info("Starting Lyrica Backend API")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Version: {__version__}")

    # Initialize database connection
    from app.db.session import engine

    # Ensure database engine is initialized
    if engine:
        logger.info("Database connection initialized")

    # Initialize Redis connection
    try:
        from app.core.redis import redis_client

        await redis_client.connect()
        logger.info("Redis connection initialized")
    except Exception as e:
        logger.warning(f"Redis initialization failed: {e}")

    # Initialize ChromaDB client
    try:
        from app.services.vector_store import vector_store

        # Access the client property to trigger lazy initialization
        _ = vector_store.client
        logger.info("ChromaDB client initialized")
    except Exception as e:
        logger.warning(f"ChromaDB initialization failed: {e}")

    # Initialize Ollama client (verify connection)
    try:
        from app.services.llm.factory import llm_factory

        # This will initialize the LLM service based on settings
        llm_service = llm_factory.get_service()
        logger.info(f"LLM service initialized: {llm_service.provider.value}")
    except Exception as e:
        logger.warning(f"LLM service initialization failed: {e}")

    yield

    # Shutdown
    logger.info("Shutting down Lyrica Backend API")

    # Cleanup connections
    from app.db.session import close_db

    await close_db()
    logger.info("Database connections closed")

    # Cleanup Redis connections
    try:
        from app.core.redis import redis_client

        await redis_client.disconnect()
        logger.info("Redis connections closed")
    except Exception as e:
        logger.warning(f"Redis cleanup failed: {e}")

    # Cleanup ChromaDB connections
    try:
        from app.services.cache import cache_service

        await cache_service.close()
        logger.info("Cache service closed")
    except Exception as e:
        logger.warning(f"Cache service cleanup failed: {e}")


# Initialize logging
setup_logging()

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Agentic Song Lyrics Generator - Backend API",
    version=__version__,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url="/openapi.json" if not settings.is_production else None,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Add custom middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)

# Add rate limiting middleware if enabled
if settings.rate_limit_enabled:
    app.add_middleware(
        RateLimitMiddleware,
        calls=settings.rate_limit_per_minute,
        period=settings.rate_limit_window_seconds,
    )
    logger.info(
        f"Rate limiting enabled: {settings.rate_limit_per_minute} requests per "
        f"{settings.rate_limit_window_seconds} seconds"
    )

# Include API v1 router
app.include_router(api_router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint."""
    return {
        "application": settings.app_name,
        "version": __version__,
        "status": "running",
        "docs": "/docs" if not settings.is_production else "disabled",
    }


# Add Prometheus metrics endpoint if enabled
if settings.enable_metrics:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all unhandled exceptions."""
    logger.error(
        f"Unhandled exception: {exc}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "error_type": type(exc).__name__,
        },
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if settings.debug else "An unexpected error occurred",
            "request_id": getattr(request.state, "request_id", None),
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        workers=settings.workers if not settings.reload else 1,
        log_level=settings.log_level.lower(),
    )
