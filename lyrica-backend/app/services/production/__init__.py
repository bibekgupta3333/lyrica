"""
Song production services.

This package provides complete song production capabilities including:
- Song assembly (vocals + music mixing)
- Intelligent frequency balancing (dynamic EQ, sidechain compression)
- Multi-section song creation
- Lyrics-music synchronization
- Final mastering
- Multi-format export
"""

from app.services.production.frequency_balancing import (
    DynamicEQService,
    FrequencyAnalysisService,
    SidechainCompressionService,
    get_dynamic_eq,
    get_frequency_analysis,
    get_sidechain_compression,
)
from app.services.production.mastering import SongMasteringService, get_song_mastering
from app.services.production.song_assembly import SongAssemblyService, get_song_assembly

__all__ = [
    "SongAssemblyService",
    "SongMasteringService",
    "FrequencyAnalysisService",
    "DynamicEQService",
    "SidechainCompressionService",
    "get_song_assembly",
    "get_song_mastering",
    "get_frequency_analysis",
    "get_dynamic_eq",
    "get_sidechain_compression",
]
