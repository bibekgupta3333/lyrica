"""
API v1 Router
Combines all API v1 endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    audio,
    auth,
    feedback,
    health,
    lyrics,
    music,
    production,
    rag,
    songs,
    songs_complete,
    streaming,
    styles,
    voice,
)

# Create API v1 router
api_router = APIRouter()

# Include endpoint routers

# Health & System
api_router.include_router(health.router, prefix="/health", tags=["Health"])

# Authentication & Authorization
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# RAG & Vector Search
api_router.include_router(rag.router, prefix="/rag", tags=["RAG & Vector Search"])

# Agent-Based Song Generation
api_router.include_router(songs.router, prefix="/songs", tags=["Song Generation (Agents)"])

# Lyrics CRUD
api_router.include_router(lyrics.router, prefix="/lyrics", tags=["Lyrics Management"])

# Feedback
api_router.include_router(feedback.router, prefix="/feedback", tags=["User Feedback"])

# Styles & Genres
api_router.include_router(styles.router, prefix="/styles", tags=["Styles & Genres"])

# Streaming
api_router.include_router(streaming.router, prefix="/stream", tags=["Streaming"])

# Audio Processing
api_router.include_router(audio.router, prefix="/audio", tags=["Audio Processing"])

# Voice Synthesis
api_router.include_router(voice.router, prefix="/voice", tags=["Voice Synthesis"])

# Music Generation
api_router.include_router(music.router, prefix="/music", tags=["Music Generation"])

# Song Production
api_router.include_router(production.router, prefix="/production", tags=["Song Production"])

# Complete Song Generation API (WBS 2.14)
api_router.include_router(songs_complete.router, tags=["Complete Song Generation"])

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
