"""
Song production services.

This package provides complete song production capabilities including:
- Song assembly (vocals + music mixing)
- Multi-section song creation
- Lyrics-music synchronization
- Final mastering
- Multi-format export
"""

from app.services.production.mastering import SongMasteringService, get_song_mastering
from app.services.production.song_assembly import SongAssemblyService, get_song_assembly

__all__ = [
    "SongAssemblyService",
    "SongMasteringService",
    "get_song_assembly",
    "get_song_mastering",
]
