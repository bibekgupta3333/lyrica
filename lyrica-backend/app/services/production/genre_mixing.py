"""
Genre-specific mixing service.

This module provides genre classification, genre-specific mixing presets,
and reference track analysis for professional mixing.
"""

import warnings
from pathlib import Path
from typing import Optional

import librosa
import numpy as np
from loguru import logger

from app.core.music_config import MusicGenre
from app.services.production.frequency_balancing import get_frequency_analysis

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


class GenreClassificationService:
    """Service for classifying music genre from audio features."""

    def __init__(self):
        """Initialize genre classification service."""
        self.freq_analysis = get_frequency_analysis()
        logger.success("GenreClassificationService initialized")

    def classify_genre(self, audio_path: Path) -> dict:
        """
        Classify music genre from audio features.

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary containing:
            - predicted_genre: Most likely genre (MusicGenre enum)
            - confidence: Confidence score (0.0-1.0)
            - genre_scores: Scores for all genres
            - features: Extracted audio features used for classification
        """
        logger.info(f"Classifying genre: {audio_path}")

        # Extract audio features
        features = self._extract_classification_features(audio_path)

        # Classify using rule-based approach (can be replaced with ML model)
        genre_scores = self._classify_from_features(features)

        # Get top genre
        top_genre_str = max(genre_scores, key=genre_scores.get)
        confidence = genre_scores[top_genre_str]

        # Convert to enum
        try:
            predicted_genre = MusicGenre(top_genre_str)
        except ValueError:
            predicted_genre = MusicGenre.POP  # Default fallback
            confidence = 0.5

        result = {
            "predicted_genre": predicted_genre,
            "confidence": float(confidence),
            "genre_scores": {k: float(v) for k, v in genre_scores.items()},
            "features": features,
        }

        logger.info(f"Predicted genre: {predicted_genre.value} (confidence: {confidence:.2f})")
        return result

    def _extract_classification_features(self, audio_path: Path) -> dict:
        """Extract audio features for genre classification."""
        y, sr = librosa.load(str(audio_path), sr=None)

        # Get frequency analysis
        freq_analysis = self.freq_analysis.analyze_frequency_content(audio_path, sr=sr)

        # Extract tempo
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

        # Extract rhythm features
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)
        if len(onset_times) > 1:
            inter_onset_intervals = np.diff(onset_times)
            rhythm_regularity = 1.0 / (1.0 + np.std(inter_onset_intervals))
        else:
            rhythm_regularity = 0.5

        # Extract spectral features
        spectral_centroid = freq_analysis["spectral_centroid"]
        spectral_rolloff = freq_analysis["spectral_rolloff"]
        zero_crossing_rate = freq_analysis["zero_crossing_rate"]

        # Extract frequency band energies
        bands = freq_analysis["frequency_bands"]
        bass_energy = bands.get("bass", 0) + bands.get("sub_bass", 0)
        mid_energy = bands.get("mid", 0) + bands.get("low_mid", 0)
        treble_energy = bands.get("treble", 0) + bands.get("high_mid", 0)

        # Extract dynamic range
        rms = librosa.feature.rms(y=y)[0]
        dynamic_range = np.max(rms) - np.min(rms)

        features = {
            "tempo": float(tempo),
            "rhythm_regularity": float(rhythm_regularity),
            "spectral_centroid": float(spectral_centroid),
            "spectral_rolloff": float(spectral_rolloff),
            "zero_crossing_rate": float(zero_crossing_rate),
            "bass_energy": float(bass_energy),
            "mid_energy": float(mid_energy),
            "treble_energy": float(treble_energy),
            "dynamic_range": float(dynamic_range),
        }

        return features

    def _classify_from_features(self, features: dict) -> dict[str, float]:
        """Classify genre from extracted features using rule-based approach."""
        tempo = features["tempo"]
        bass_energy = features["bass_energy"]
        mid_energy = features["mid_energy"]
        treble_energy = features["treble_energy"]
        spectral_centroid = features["spectral_centroid"]
        rhythm_regularity = features["rhythm_regularity"]
        dynamic_range = features["dynamic_range"]

        scores = {}

        # Pop: Moderate tempo, balanced frequencies, high regularity
        pop_score = 0.0
        if 100 <= tempo <= 130:
            pop_score += 0.3
        if 20 <= mid_energy <= 40:
            pop_score += 0.2
        if rhythm_regularity > 0.7:
            pop_score += 0.2
        if 1500 <= spectral_centroid <= 3000:
            pop_score += 0.3
        scores["pop"] = min(pop_score, 1.0)

        # Rock: Higher tempo, more mid-range, aggressive
        rock_score = 0.0
        if 110 <= tempo <= 140:
            rock_score += 0.3
        if mid_energy > 30:
            rock_score += 0.2
        if spectral_centroid > 2000:
            rock_score += 0.2
        if dynamic_range > 0.3:
            rock_score += 0.3
        scores["rock"] = min(rock_score, 1.0)

        # Hip-Hop: Lower tempo, heavy bass, rhythmic
        hiphop_score = 0.0
        if 80 <= tempo <= 110:
            hiphop_score += 0.3
        if bass_energy > 30:
            hiphop_score += 0.3
        if rhythm_regularity > 0.8:
            hiphop_score += 0.2
        if treble_energy < 25:
            hiphop_score += 0.2
        scores["hiphop"] = min(hiphop_score, 1.0)

        # Electronic: Higher tempo, heavy bass and treble
        electronic_score = 0.0
        if 120 <= tempo <= 140:
            electronic_score += 0.3
        if bass_energy > 25:
            electronic_score += 0.2
        if treble_energy > 30:
            electronic_score += 0.2
        if rhythm_regularity > 0.9:
            electronic_score += 0.3
        scores["electronic"] = min(electronic_score, 1.0)

        # Jazz: Moderate tempo, balanced, dynamic
        jazz_score = 0.0
        if 100 <= tempo <= 160:
            jazz_score += 0.2
        if 20 <= mid_energy <= 35:
            jazz_score += 0.2
        if dynamic_range > 0.4:
            jazz_score += 0.3
        if rhythm_regularity < 0.6:
            jazz_score += 0.3
        scores["jazz"] = min(jazz_score, 1.0)

        # Classical: Lower tempo, balanced, very dynamic
        classical_score = 0.0
        if 60 <= tempo <= 120:
            classical_score += 0.3
        if dynamic_range > 0.5:
            classical_score += 0.3
        if treble_energy > 25:
            classical_score += 0.2
        if rhythm_regularity < 0.5:
            classical_score += 0.2
        scores["classical"] = min(classical_score, 1.0)

        # Country: Moderate tempo, mid-range focused
        country_score = 0.0
        if 90 <= tempo <= 120:
            country_score += 0.3
        if mid_energy > 25:
            country_score += 0.3
        if bass_energy < 20:
            country_score += 0.2
        if 1500 <= spectral_centroid <= 2500:
            country_score += 0.2
        scores["country"] = min(country_score, 1.0)

        # R&B: Lower tempo, balanced, smooth
        rnb_score = 0.0
        if 70 <= tempo <= 110:
            rnb_score += 0.3
        if 20 <= mid_energy <= 35:
            rnb_score += 0.2
        if bass_energy > 20:
            rnb_score += 0.2
        if rhythm_regularity > 0.7:
            rnb_score += 0.3
        scores["rnb"] = min(rnb_score, 1.0)

        # Metal: Very high tempo, aggressive, heavy
        metal_score = 0.0
        if tempo > 140:
            metal_score += 0.3
        if mid_energy > 35:
            metal_score += 0.2
        if bass_energy > 25:
            metal_score += 0.2
        if spectral_centroid > 2500:
            metal_score += 0.3
        scores["metal"] = min(metal_score, 1.0)

        # Ambient: Low tempo, treble-focused, minimal
        ambient_score = 0.0
        if tempo < 90:
            ambient_score += 0.3
        if treble_energy > 30:
            ambient_score += 0.3
        if bass_energy < 15:
            ambient_score += 0.2
        if dynamic_range < 0.2:
            ambient_score += 0.2
        scores["ambient"] = min(ambient_score, 1.0)

        # Normalize scores
        total_score = sum(scores.values())
        if total_score > 0:
            scores = {k: v / total_score for k, v in scores.items()}
        else:
            # Default to pop if no match
            scores = {k: 0.0 for k in scores}
            scores["pop"] = 1.0

        return scores


class GenreMixingPresetsService:
    """Service for genre-specific mixing presets."""

    def __init__(self):
        """Initialize genre mixing presets service."""
        logger.success("GenreMixingPresetsService initialized")

    def get_mixing_preset(self, genre: MusicGenre) -> dict:
        """
        Get comprehensive mixing preset for a genre.

        Args:
            genre: Music genre

        Returns:
            Dictionary containing mixing settings:
            - eq: EQ settings
            - compression: Compression settings
            - stereo_width: Stereo width settings
            - reverb: Reverb settings
            - delay: Delay settings
            - sidechain: Sidechain compression settings
            - vocals_processing: Vocals-specific settings
            - music_processing: Music-specific settings
        """
        presets = {
            MusicGenre.POP: {
                "eq": {
                    "vocals": [
                        {"frequency": 2000, "gain_db": 1.5, "q": 1.0},  # Presence
                        {"frequency": 8000, "gain_db": 1.0, "q": 1.0},  # Air
                    ],
                    "music": [
                        {"frequency": 2000, "gain_db": 1.0, "q": 1.0},
                        {"frequency": 100, "gain_db": -1.0, "q": 2.0},  # Cut mud
                    ],
                },
                "compression": {
                    "vocals": {"threshold": -18.0, "ratio": 3.0, "attack": 5.0, "release": 50.0},
                    "music": {"threshold": -20.0, "ratio": 2.5, "attack": 10.0, "release": 100.0},
                },
                "stereo_width": {"vocals": 1.0, "music": 1.3},
                "reverb": {
                    "vocals": {
                        "room_size": 0.3,
                        "damping": 0.5,
                        "wet_level": 0.2,
                        "pre_delay_ms": 20.0,
                    },
                    "music": {
                        "room_size": 0.4,
                        "damping": 0.5,
                        "wet_level": 0.25,
                        "pre_delay_ms": 25.0,
                    },
                },
                "delay": {
                    "vocals": {
                        "delay_ms": 300.0,
                        "feedback": 0.2,
                        "wet_level": 0.3,
                        "ping_pong": True,
                    },
                    "music": None,  # No delay for pop music typically
                },
                "sidechain": {
                    "threshold_db": -20.0,
                    "ratio": 4.0,
                    "attack_ms": 5.0,
                    "release_ms": 100.0,
                },
            },
            MusicGenre.ROCK: {
                "eq": {
                    "vocals": [
                        {"frequency": 3000, "gain_db": 2.0, "q": 1.0},  # Aggression
                        {"frequency": 100, "gain_db": 1.0, "q": 1.0},  # Low end
                    ],
                    "music": [
                        {"frequency": 3000, "gain_db": 1.5, "q": 1.0},
                        {"frequency": 80, "gain_db": 1.5, "q": 1.5},  # Boost sub-bass
                    ],
                },
                "compression": {
                    "vocals": {"threshold": -16.0, "ratio": 4.0, "attack": 3.0, "release": 40.0},
                    "music": {"threshold": -18.0, "ratio": 3.0, "attack": 5.0, "release": 80.0},
                },
                "stereo_width": {"vocals": 1.0, "music": 1.5},
                "reverb": {
                    "vocals": {
                        "room_size": 0.4,
                        "damping": 0.4,
                        "wet_level": 0.25,
                        "pre_delay_ms": 25.0,
                    },
                    "music": {
                        "room_size": 0.6,
                        "damping": 0.4,
                        "wet_level": 0.3,
                        "pre_delay_ms": 30.0,
                    },
                },
                "delay": {
                    "vocals": {
                        "delay_ms": 400.0,
                        "feedback": 0.3,
                        "wet_level": 0.4,
                        "ping_pong": True,
                    },
                    "music": None,
                },
                "sidechain": {
                    "threshold_db": -18.0,
                    "ratio": 5.0,
                    "attack_ms": 3.0,
                    "release_ms": 80.0,
                },
            },
            MusicGenre.HIPHOP: {
                "eq": {
                    "vocals": [
                        {"frequency": 2000, "gain_db": -1.0, "q": 1.0},  # Cut harsh mids
                        {"frequency": 5000, "gain_db": 1.0, "q": 1.0},  # Clarity
                    ],
                    "music": [
                        {"frequency": 80, "gain_db": 2.0, "q": 1.5},  # Sub-bass
                        {"frequency": 2000, "gain_db": -1.5, "q": 1.0},  # Cut mids
                    ],
                },
                "compression": {
                    "vocals": {"threshold": -20.0, "ratio": 3.5, "attack": 5.0, "release": 60.0},
                    "music": {"threshold": -22.0, "ratio": 2.0, "attack": 15.0, "release": 120.0},
                },
                "stereo_width": {"vocals": 1.0, "music": 1.2},
                "reverb": {
                    "vocals": {
                        "room_size": 0.2,
                        "damping": 0.6,
                        "wet_level": 0.15,
                        "pre_delay_ms": 15.0,
                    },
                    "music": {
                        "room_size": 0.3,
                        "damping": 0.5,
                        "wet_level": 0.2,
                        "pre_delay_ms": 20.0,
                    },
                },
                "delay": {
                    "vocals": {
                        "delay_ms": 250.0,
                        "feedback": 0.15,
                        "wet_level": 0.25,
                        "ping_pong": True,
                    },
                    "music": None,
                },
                "sidechain": {
                    "threshold_db": -22.0,
                    "ratio": 4.5,
                    "attack_ms": 5.0,
                    "release_ms": 120.0,
                },
            },
            MusicGenre.ELECTRONIC: {
                "eq": {
                    "vocals": [
                        {"frequency": 3000, "gain_db": 1.0, "q": 1.0},
                        {"frequency": 8000, "gain_db": 1.5, "q": 1.0},  # Air
                    ],
                    "music": [
                        {"frequency": 60, "gain_db": 1.5, "q": 1.5},  # Sub-bass
                        {"frequency": 5000, "gain_db": 1.0, "q": 1.0},  # Clarity
                    ],
                },
                "compression": {
                    "vocals": {"threshold": -18.0, "ratio": 3.0, "attack": 5.0, "release": 50.0},
                    "music": {"threshold": -20.0, "ratio": 2.5, "attack": 10.0, "release": 100.0},
                },
                "stereo_width": {"vocals": 1.0, "music": 1.6},
                "reverb": {
                    "vocals": {
                        "room_size": 0.3,
                        "damping": 0.5,
                        "wet_level": 0.2,
                        "pre_delay_ms": 20.0,
                    },
                    "music": {
                        "room_size": 0.7,
                        "damping": 0.4,
                        "wet_level": 0.4,
                        "pre_delay_ms": 40.0,
                    },
                },
                "delay": {
                    "vocals": {
                        "delay_ms": 350.0,
                        "feedback": 0.25,
                        "wet_level": 0.3,
                        "ping_pong": True,
                    },
                    "music": {
                        "delay_ms": 500.0,
                        "feedback": 0.3,
                        "wet_level": 0.4,
                        "ping_pong": True,
                    },
                },
                "sidechain": {
                    "threshold_db": -20.0,
                    "ratio": 4.0,
                    "attack_ms": 5.0,
                    "release_ms": 100.0,
                },
            },
            MusicGenre.JAZZ: {
                "eq": {
                    "vocals": [
                        {"frequency": 500, "gain_db": 1.0, "q": 1.0},  # Warmth
                        {"frequency": 3000, "gain_db": -0.5, "q": 1.0},  # Reduce harshness
                    ],
                    "music": [
                        {"frequency": 500, "gain_db": 1.0, "q": 1.0},
                        {"frequency": 8000, "gain_db": -1.0, "q": 1.0},  # Reduce brightness
                    ],
                },
                "compression": {
                    "vocals": {"threshold": -22.0, "ratio": 2.0, "attack": 10.0, "release": 100.0},
                    "music": {"threshold": -24.0, "ratio": 1.5, "attack": 20.0, "release": 150.0},
                },
                "stereo_width": {"vocals": 1.0, "music": 1.4},
                "reverb": {
                    "vocals": {
                        "room_size": 0.5,
                        "damping": 0.6,
                        "wet_level": 0.3,
                        "pre_delay_ms": 30.0,
                    },
                    "music": {
                        "room_size": 0.6,
                        "damping": 0.6,
                        "wet_level": 0.35,
                        "pre_delay_ms": 35.0,
                    },
                },
                "delay": {
                    "vocals": {
                        "delay_ms": 400.0,
                        "feedback": 0.2,
                        "wet_level": 0.25,
                        "ping_pong": True,
                    },
                    "music": None,
                },
                "sidechain": {
                    "threshold_db": -24.0,
                    "ratio": 3.0,
                    "attack_ms": 10.0,
                    "release_ms": 150.0,
                },
            },
        }

        # Default preset (pop-like)
        default_preset = presets.get(MusicGenre.POP)

        return presets.get(genre, default_preset)


class ReferenceTrackAnalysisService:
    """Service for analyzing reference tracks and matching their characteristics."""

    def __init__(self):
        """Initialize reference track analysis service."""
        self.freq_analysis = get_frequency_analysis()
        logger.success("ReferenceTrackAnalysisService initialized")

    def analyze_reference_track(self, reference_path: Path) -> dict:
        """
        Analyze a reference track to extract its mixing characteristics.

        Args:
            reference_path: Path to reference audio file

        Returns:
            Dictionary containing reference characteristics:
            - frequency_analysis: Full frequency analysis
            - stereo_width: Stereo width characteristics
            - dynamic_range: Dynamic range characteristics
            - eq_profile: EQ profile
            - loudness: Perceived loudness
            - recommendations: Mixing recommendations
        """
        logger.info(f"Analyzing reference track: {reference_path}")

        # Get frequency analysis
        freq_analysis = self.freq_analysis.analyze_frequency_content(reference_path)

        # Get stereo width
        from app.services.production.stereo_imaging import get_stereo_imaging

        stereo_imaging = get_stereo_imaging()
        stereo_analysis = stereo_imaging.measure_stereo_width(reference_path)

        # Calculate dynamic range
        y, sr = librosa.load(str(reference_path), sr=None)
        rms = librosa.feature.rms(y=y)[0]
        dynamic_range = float(np.max(rms) - np.min(rms))
        avg_loudness = float(np.mean(rms))

        # Extract EQ profile (frequency band distribution)
        bands = freq_analysis["frequency_bands"]
        eq_profile = {
            "sub_bass": bands.get("sub_bass", 0),
            "bass": bands.get("bass", 0),
            "low_mid": bands.get("low_mid", 0),
            "mid": bands.get("mid", 0),
            "high_mid": bands.get("high_mid", 0),
            "treble": bands.get("treble", 0),
        }

        # Generate recommendations
        recommendations = self._generate_recommendations(
            freq_analysis, stereo_analysis, dynamic_range, eq_profile
        )

        result = {
            "frequency_analysis": freq_analysis,
            "stereo_width": stereo_analysis,
            "dynamic_range": dynamic_range,
            "avg_loudness": avg_loudness,
            "eq_profile": eq_profile,
            "recommendations": recommendations,
        }

        logger.success("Reference track analysis complete")
        return result

    def match_to_reference(
        self, target_path: Path, reference_analysis: dict, output_path: Optional[Path] = None
    ) -> Path:
        """
        Match target audio to reference track characteristics.

        Args:
            target_path: Path to target audio file
            reference_analysis: Reference analysis from analyze_reference_track()
            output_path: Optional output path

        Returns:
            Path to matched audio file
        """
        logger.info(f"Matching target to reference: {target_path}")

        # This would apply EQ, compression, stereo width, etc. to match reference
        # For now, we'll use the frequency balancing service
        from app.services.production.frequency_balancing import get_dynamic_eq

        dynamic_eq = get_dynamic_eq()

        # Apply EQ to match reference frequency profile
        matched_path = dynamic_eq.apply_dynamic_eq(
            target_path,
            reference_analysis=reference_analysis["frequency_analysis"],
            output_path=output_path,
        )

        logger.success(f"Target matched to reference: {matched_path}")
        return matched_path

    def _generate_recommendations(
        self, freq_analysis: dict, stereo_analysis: dict, dynamic_range: float, eq_profile: dict
    ) -> list[dict]:
        """Generate mixing recommendations based on reference analysis."""
        recommendations = []

        # EQ recommendations
        if eq_profile["bass"] > 30:
            recommendations.append(
                {
                    "type": "eq",
                    "target": "music",
                    "frequency": 80,
                    "gain_db": 2.0,
                    "reason": "Reference has strong bass presence",
                }
            )

        if eq_profile["mid"] < 15:
            recommendations.append(
                {
                    "type": "eq",
                    "target": "vocals",
                    "frequency": 1000,
                    "gain_db": 2.0,
                    "reason": "Reference has less mid energy, boost vocals",
                }
            )

        # Stereo width recommendations
        if stereo_analysis["width_score"] > 0.7:
            recommendations.append(
                {
                    "type": "stereo_width",
                    "target": "music",
                    "width_factor": 1.5,
                    "reason": "Reference has wide stereo field",
                }
            )

        # Dynamic range recommendations
        if dynamic_range < 0.2:
            recommendations.append(
                {
                    "type": "compression",
                    "target": "all",
                    "threshold": -20.0,
                    "ratio": 3.0,
                    "reason": "Reference has limited dynamic range",
                }
            )

        return recommendations


# Singleton instances
_genre_classification_service: Optional[GenreClassificationService] = None
_genre_presets_service: Optional[GenreMixingPresetsService] = None
_reference_analysis_service: Optional[ReferenceTrackAnalysisService] = None


def get_genre_classification() -> GenreClassificationService:
    """Get or create genre classification service instance."""
    global _genre_classification_service
    if _genre_classification_service is None:
        _genre_classification_service = GenreClassificationService()
    return _genre_classification_service


def get_genre_mixing_presets() -> GenreMixingPresetsService:
    """Get or create genre mixing presets service instance."""
    global _genre_presets_service
    if _genre_presets_service is None:
        _genre_presets_service = GenreMixingPresetsService()
    return _genre_presets_service


def get_reference_analysis() -> ReferenceTrackAnalysisService:
    """Get or create reference track analysis service instance."""
    global _reference_analysis_service
    if _reference_analysis_service is None:
        _reference_analysis_service = ReferenceTrackAnalysisService()
    return _reference_analysis_service
