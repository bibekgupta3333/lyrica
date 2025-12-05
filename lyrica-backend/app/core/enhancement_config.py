"""
Unified Enhancement Configuration System.

This module provides a centralized configuration system for voice and mixing enhancement,
with fallback mechanisms and performance optimization.
"""

from typing import Dict, Optional

from loguru import logger
from pydantic import BaseModel, Field

from app.core.config import settings


class EnhancementSettings(BaseModel):
    """Unified enhancement settings with defaults and fallbacks."""

    # Voice Enhancement Defaults
    voice_enhancement_enabled: bool = Field(
        default=True, description="Enable voice enhancement by default"
    )
    neural_vocoder_enabled: bool = Field(
        default=True, description="Use neural vocoder if available"
    )
    prosody_enhancement_enabled: bool = Field(
        default=True, description="Enable prosody enhancement"
    )
    auto_tune_enabled: bool = Field(default=False, description="Enable auto-tune by default")

    # Mixing Enhancement Defaults
    intelligent_mixing_enabled: bool = Field(
        default=True, description="Enable intelligent mixing by default"
    )
    frequency_balancing_enabled: bool = Field(
        default=True, description="Enable frequency balancing"
    )
    sidechain_compression_enabled: bool = Field(
        default=True, description="Enable sidechain compression"
    )
    stereo_imaging_enabled: bool = Field(default=True, description="Enable stereo imaging")
    genre_specific_mixing_enabled: bool = Field(
        default=True, description="Enable genre-specific mixing"
    )

    # Memory & Learning Defaults
    memory_learning_enabled: bool = Field(default=True, description="Enable memory-based learning")
    quality_tracking_enabled: bool = Field(default=True, description="Track quality metrics")

    # Performance Settings
    enable_caching: bool = Field(default=True, description="Enable result caching")
    cache_ttl_seconds: int = Field(default=3600, description="Cache TTL in seconds")
    parallel_processing: bool = Field(
        default=False, description="Enable parallel processing (experimental)"
    )

    # Fallback Settings
    fallback_on_error: bool = Field(
        default=True, description="Fallback to basic processing on error"
    )
    log_failures: bool = Field(default=True, description="Log enhancement failures")

    @classmethod
    def from_settings(cls) -> "EnhancementSettings":
        """Create settings from application settings."""
        return cls(
            voice_enhancement_enabled=getattr(settings, "voice_enhancement_enabled", True),
            neural_vocoder_enabled=getattr(settings, "neural_vocoder_enabled", True),
            prosody_enhancement_enabled=getattr(settings, "prosody_enhancement_enabled", True),
            auto_tune_enabled=getattr(settings, "auto_tune_enabled", False),
            intelligent_mixing_enabled=getattr(settings, "intelligent_mixing_enabled", True),
            frequency_balancing_enabled=getattr(settings, "frequency_balancing_enabled", True),
            sidechain_compression_enabled=getattr(settings, "sidechain_compression_enabled", True),
            stereo_imaging_enabled=getattr(settings, "stereo_imaging_enabled", True),
            genre_specific_mixing_enabled=getattr(settings, "genre_specific_mixing_enabled", True),
            memory_learning_enabled=getattr(settings, "memory_learning_enabled", True),
            quality_tracking_enabled=getattr(settings, "quality_tracking_enabled", True),
            enable_caching=getattr(settings, "enable_caching", True),
            cache_ttl_seconds=getattr(settings, "cache_ttl_seconds", 3600),
            parallel_processing=getattr(settings, "parallel_processing", False),
            fallback_on_error=getattr(settings, "fallback_on_error", True),
            log_failures=getattr(settings, "log_failures", True),
        )


class EnhancementConfigManager:
    """Manages enhancement configuration with fallbacks and error handling."""

    def __init__(self):
        """Initialize configuration manager."""
        self.settings = EnhancementSettings.from_settings()
        logger.success("EnhancementConfigManager initialized")

    def get_config(self, overrides: Optional[Dict] = None) -> EnhancementSettings:
        """
        Get enhancement configuration with optional overrides.

        Args:
            overrides: Optional dictionary to override default settings

        Returns:
            EnhancementSettings instance
        """
        if overrides:
            return EnhancementSettings(**{**self.settings.model_dump(), **overrides})
        return self.settings

    def should_enable_feature(self, feature: str, user_preference: Optional[bool] = None) -> bool:
        """
        Determine if a feature should be enabled.

        Args:
            feature: Feature name (e.g., 'voice_enhancement', 'intelligent_mixing')
            user_preference: Optional user preference override

        Returns:
            True if feature should be enabled
        """
        if user_preference is not None:
            return user_preference

        feature_map = {
            "voice_enhancement": self.settings.voice_enhancement_enabled,
            "neural_vocoder": self.settings.neural_vocoder_enabled,
            "prosody": self.settings.prosody_enhancement_enabled,
            "auto_tune": self.settings.auto_tune_enabled,
            "intelligent_mixing": self.settings.intelligent_mixing_enabled,
            "frequency_balancing": self.settings.frequency_balancing_enabled,
            "sidechain": self.settings.sidechain_compression_enabled,
            "stereo_imaging": self.settings.stereo_imaging_enabled,
            "genre_specific": self.settings.genre_specific_mixing_enabled,
            "memory_learning": self.settings.memory_learning_enabled,
            "quality_tracking": self.settings.quality_tracking_enabled,
        }

        return feature_map.get(feature, False)


# Singleton instance
_config_manager: Optional[EnhancementConfigManager] = None


def get_enhancement_config() -> EnhancementConfigManager:
    """Get or create enhancement configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = EnhancementConfigManager()
    return _config_manager
