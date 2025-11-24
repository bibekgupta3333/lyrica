"""
Health Check Endpoints
Provides system health and readiness checks.
"""

from typing import Dict, Any
from fastapi import APIRouter, status
from datetime import datetime
import psutil

from app.core.config import settings
from app import __version__

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
    summary="Health Check",
    description="Check if the API is running and responsive"
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
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
    summary="Readiness Check",
    description="Check if the API is ready to serve requests"
)
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check endpoint (for Kubernetes).
    
    Returns:
        Readiness status with component checks
    """
    # TODO: Add actual checks for dependencies
    # - Database connection
    # - Redis connection
    # - ChromaDB connection
    # - Ollama availability
    
    checks = {
        "database": "healthy",  # TODO: Implement actual check
        "redis": "healthy",     # TODO: Implement actual check
        "chromadb": "healthy",  # TODO: Implement actual check
        "ollama": "healthy",    # TODO: Implement actual check
    }
    
    all_healthy = all(status == "healthy" for status in checks.values())
    
    return {
        "status": "ready" if all_healthy else "not_ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks,
    }


@router.get(
    "/health/live",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
    summary="Liveness Check",
    description="Check if the API is alive (for Kubernetes)"
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
    description="Get system resource metrics"
)
async def system_metrics() -> Dict[str, Any]:
    """
    Get system resource metrics.
    
    Returns:
        System metrics including CPU, memory, disk usage
    """
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
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
    description="Get application information and configuration"
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

