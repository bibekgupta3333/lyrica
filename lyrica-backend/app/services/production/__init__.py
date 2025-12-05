"""
Song production services.

This package provides complete song production capabilities including:
- Song assembly (vocals + music mixing)
- Intelligent frequency balancing (dynamic EQ, sidechain compression)
- Stereo imaging and spatial effects (width, reverb, delay)
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
from app.services.production.genre_mixing import (
    GenreClassificationService,
    GenreMixingPresetsService,
    ReferenceTrackAnalysisService,
    get_genre_classification,
    get_genre_mixing_presets,
    get_reference_analysis,
)
from app.services.production.mastering import SongMasteringService, get_song_mastering
from app.services.production.song_assembly import SongAssemblyService, get_song_assembly
from app.services.production.stereo_imaging import StereoImagingService, get_stereo_imaging
from app.services.production.unified_pipeline import UnifiedPipelineService, get_unified_pipeline

__all__ = [
    "SongAssemblyService",
    "SongMasteringService",
    "FrequencyAnalysisService",
    "DynamicEQService",
    "SidechainCompressionService",
    "StereoImagingService",
    "GenreClassificationService",
    "GenreMixingPresetsService",
    "ReferenceTrackAnalysisService",
    "get_song_assembly",
    "get_song_mastering",
    "get_frequency_analysis",
    "get_dynamic_eq",
    "get_sidechain_compression",
    "get_stereo_imaging",
    "get_genre_classification",
    "get_genre_mixing_presets",
    "get_reference_analysis",
    "UnifiedPipelineService",
    "get_unified_pipeline",
]
