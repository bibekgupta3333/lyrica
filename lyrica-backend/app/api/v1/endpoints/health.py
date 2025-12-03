"""
Health Check Endpoints
Provides system health and readiness checks.
"""

from datetime import datetime
from typing import Any, Dict

import psutil
from fastapi import APIRouter, status

from app import __version__
from app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
    summary="Health Check",
    description="Check if the API is running and responsive",
)
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.

    Returns:
        Health status information
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": __version__,
        "environment": settings.environment,
    }


@router.get(
    "/health/ready",
    response_model=Dict[str, Any],
    summary="Readiness Check",
    description="Check if the API is ready to serve requests",
)
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check endpoint (for Kubernetes).

    Returns:
        Readiness status with component checks

    Status Codes:
        200: All services are healthy
        503: One or more services are unhealthy
    """
    from fastapi.responses import JSONResponse

    checks = {}
    all_healthy = True

    # Database health check
    try:
        from sqlalchemy import text

        from app.db.session import engine

        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = {"status": "healthy", "message": "Database connection successful"}
    except Exception as e:
        checks["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}",
        }
        all_healthy = False

    # Redis health check
    try:
        from app.core.redis import redis_client

        is_healthy = await redis_client.health_check()
        if is_healthy:
            checks["redis"] = {"status": "healthy", "message": "Redis connection successful"}
        else:
            checks["redis"] = {"status": "unhealthy", "message": "Redis ping failed"}
            all_healthy = False
    except Exception as e:
        checks["redis"] = {"status": "unhealthy", "message": f"Redis connection failed: {str(e)}"}
        all_healthy = False

    # ChromaDB health check
    try:
        from app.services.vector_store import vector_store

        # Try to get collection count
        count = vector_store.count()
        checks["chromadb"] = {
            "status": "healthy",
            "message": f"ChromaDB connected ({count} documents)",
        }
    except Exception as e:
        checks["chromadb"] = {
            "status": "unhealthy",
            "message": f"ChromaDB connection failed: {str(e)}",
        }
        all_healthy = False

    # Ollama/LLM health check
    try:
        import httpx

        # Check Ollama API availability
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.ollama_base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name") for m in models]
                checks["ollama"] = {
                    "status": "healthy",
                    "message": f"Ollama available ({len(models)} models)",
                    "models": model_names[:5],  # Show first 5 models
                }
            else:
                checks["ollama"] = {
                    "status": "unhealthy",
                    "message": f"Ollama API returned status {response.status_code}",
                }
                all_healthy = False
    except Exception as e:
        checks["ollama"] = {"status": "degraded", "message": f"Ollama not available: {str(e)}"}
        # Don't mark as unhealthy - Ollama is optional for some features

    response_data = {
        "status": "ready" if all_healthy else "not_ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks,
    }

    # Return 503 if not all services are healthy
    status_code = status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(status_code=status_code, content=response_data)


@router.get(
    "/health/live",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
    summary="Liveness Check",
    description="Check if the API is alive (for Kubernetes)",
)
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check endpoint (for Kubernetes).

    Returns:
        Liveness status
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get(
    "/health/metrics",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
    summary="System Metrics",
    description="Get system resource metrics",
)
async def system_metrics() -> Dict[str, Any]:
    """
    Get system resource metrics.

    Returns:
        System metrics including CPU, memory, disk usage
    """
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "cpu": {
            "percent": cpu_percent,
            "cores": psutil.cpu_count(),
        },
        "memory": {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percent": memory.percent,
        },
        "disk": {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent,
        },
    }


@router.get(
    "/health/info",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
    summary="Application Info",
    description="Get application information and configuration",
)
async def application_info() -> Dict[str, Any]:
    """
    Get application information.

    Returns:
        Application configuration and settings
    """
    return {
        "application": {
            "name": settings.app_name,
            "version": __version__,
            "environment": settings.environment,
            "debug": settings.debug,
        },
        "ollama": {
            "base_url": settings.ollama_base_url,
            "model": settings.ollama_model,
        },
        "features": {
            "streaming": settings.enable_streaming,
            "metrics": settings.enable_metrics,
            "tracing": settings.enable_tracing,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }
