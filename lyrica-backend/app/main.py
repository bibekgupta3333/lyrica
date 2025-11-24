"""
Lyrica Backend - Main Application
FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.middleware import RequestIDMiddleware, LoggingMiddleware
from app.api.v1.api import api_router
from app import __version__


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
    logger.info("Database connection initialized")
    
    # TODO: Initialize other connections
    # - Redis connection
    # - ChromaDB client
    # - Ollama client
    
    yield
    
    # Shutdown
    logger.info("Shutting down Lyrica Backend API")
    
    # Cleanup connections
    from app.db.session import close_db
    await close_db()
    logger.info("Database connections closed")
    
    # TODO: Cleanup other connections
    # - Close Redis connections
    # - Close ChromaDB connections


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

# Include API v1 router
app.include_router(
    api_router,
    prefix="/api/v1"
)


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
        }
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if settings.debug else "An unexpected error occurred",
            "request_id": getattr(request.state, "request_id", None),
        }
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

