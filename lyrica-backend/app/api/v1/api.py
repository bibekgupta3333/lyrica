"""
API v1 Router
Combines all API v1 endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health

# Create API v1 router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health"]
)

# TODO: Add more routers as they are implemented
# api_router.include_router(
#     auth.router,
#     prefix="/auth",
#     tags=["Authentication"]
# )
# api_router.include_router(
#     lyrics.router,
#     prefix="/lyrics",
#     tags=["Lyrics"]
# )

