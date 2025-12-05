"""
Audio quality metrics service.

This module provides audio quality assessment using PESQ, STOI, and MOS metrics.
"""

import warnings
from pathlib import Path
from typing import Optional

import librosa
import numpy as np
from loguru import logger

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


class QualityMetricsService:
    """
    Service for audio quality assessment.

    Provides:
    - PESQ (Perceptual Evaluation of Speech Quality)
    - STOI (Short-Time Objective Intelligibility)
    - MOS (Mean Opinion Score) estimation
    - Overall quality scoring
    """

    def __init__(self):
        """Initialize quality metrics service."""
        self._pesq_available = False
        self._stoi_available = False
        self._check_metrics_availability()

    def _check_metrics_availability(self) -> None:
        """Check availability of quality metric libraries."""
        # Check PESQ
        try:
            import pesq

            self._pesq_available = True
            logger.info("PESQ is available for quality assessment")
        except ImportError:
            self._pesq_available = False
            logger.info(
                "PESQ not available. Install with: pip install pesq. " "Using alternative metrics."
            )

        # Check STOI
        try:
            import pystoi

            self._stoi_available = True
            logger.info("STOI is available for intelligibility assessment")
        except ImportError:
            self._stoi_available = False
            logger.info(
                "STOI not available. Install with: pip install pystoi. "
                "Using alternative metrics."
            )

    def calculate_pesq(
        self, reference_path: Path, degraded_path: Path, sample_rate: int = 16000
    ) -> float:
        """
        Calculate PESQ score (Perceptual Evaluation of Speech Quality).

        Args:
            reference_path: Path to reference (original) audio
            degraded_path: Path to degraded (processed) audio
            sample_rate: Sample rate for PESQ (must be 8000 or 16000)

        Returns:
            PESQ score (-0.5 to 4.5, higher is better)

        Note:
            PESQ requires sample rate of 8000 or 16000 Hz.
            Audio will be resampled if needed.
        """
        if not self._pesq_available:
            logger.warning("PESQ not available, using alternative metric")
            return self._estimate_pesq(reference_path, degraded_path)

        try:
            import pesq

            # Load and resample audio
            ref_audio, ref_sr = librosa.load(str(reference_path), sr=sample_rate, mono=True)
            deg_audio, deg_sr = librosa.load(str(degraded_path), sr=sample_rate, mono=True)

            # Ensure same length
            min_len = min(len(ref_audio), len(deg_audio))
            ref_audio = ref_audio[:min_len]
            deg_audio = deg_audio[:min_len]

            # Calculate PESQ
            pesq_score = pesq.pesq(sample_rate, ref_audio, deg_audio, "wb")

            logger.info(f"PESQ score: {pesq_score:.2f}")
            return float(pesq_score)

        except Exception as e:
            logger.error(f"PESQ calculation failed: {e}")
            return self._estimate_pesq(reference_path, degraded_path)

    def calculate_stoi(
        self, reference_path: Path, degraded_path: Path, sample_rate: int = 16000
    ) -> float:
        """
        Calculate STOI score (Short-Time Objective Intelligibility).

        Args:
            reference_path: Path to reference audio
            degraded_path: Path to degraded audio
            sample_rate: Sample rate for STOI

        Returns:
            STOI score (0.0 to 1.0, higher is better)
        """
        if not self._stoi_available:
            logger.warning("STOI not available, using alternative metric")
            return self._estimate_stoi(reference_path, degraded_path)

        try:
            import pystoi

            # Load audio
            ref_audio, ref_sr = librosa.load(str(reference_path), sr=sample_rate, mono=True)
            deg_audio, deg_sr = librosa.load(str(degraded_path), sr=sample_rate, mono=True)

            # Ensure same length
            min_len = min(len(ref_audio), len(deg_audio))
            ref_audio = ref_audio[:min_len]
            deg_audio = deg_audio[:min_len]

            # Calculate STOI
            stoi_score = pystoi.stoi(ref_audio, deg_audio, sample_rate, extended=False)

            logger.info(f"STOI score: {stoi_score:.3f}")
            return float(stoi_score)

        except Exception as e:
            logger.error(f"STOI calculation failed: {e}")
            return self._estimate_stoi(reference_path, degraded_path)

    def estimate_mos(self, audio_path: Path) -> float:
        """
        Estimate MOS (Mean Opinion Score) from audio features.

        Args:
            audio_path: Path to audio file

        Returns:
            Estimated MOS score (1.0 to 5.0, higher is better)

        Note:
            This is an estimation based on audio features.
            True MOS requires human evaluation.
        """
        logger.info(f"Estimating MOS for: {audio_path}")

        # Load audio
        audio, sr = librosa.load(str(audio_path), sr=None, mono=True)

        # Calculate audio features
        features = self._extract_quality_features(audio, sr)

        # Estimate MOS from features
        # Simple linear model (can be improved with ML)
        mos_score = self._features_to_mos(features)

        logger.info(f"Estimated MOS: {mos_score:.2f}")
        return mos_score

    def _extract_quality_features(self, audio: np.ndarray, sr: int) -> dict:
        """Extract audio features for quality assessment."""
        # Signal-to-noise ratio (estimated)
        signal_power = np.mean(audio**2)
        noise_floor = np.percentile(np.abs(audio), 10) ** 2
        snr = 10 * np.log10(signal_power / (noise_floor + 1e-10))

        # Spectral centroid (brightness)
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr))

        # Zero crossing rate (noise indicator)
        zcr = np.mean(librosa.feature.zero_crossing_rate(audio)[0])

        # Spectral rolloff (high frequency content)
        rolloff = np.mean(librosa.feature.spectral_rolloff(y=audio, sr=sr))

        # Dynamic range
        dynamic_range = np.max(audio) - np.min(audio)

        # Harmonic-to-noise ratio (simplified)
        harmonic, percussive = librosa.effects.hpss(audio)
        harmonic_power = np.mean(harmonic**2)
        percussive_power = np.mean(percussive**2)
        hnr = 10 * np.log10(harmonic_power / (percussive_power + 1e-10))

        return {
            "snr": snr,
            "spectral_centroid": spectral_centroid,
            "zcr": zcr,
            "rolloff": rolloff,
            "dynamic_range": dynamic_range,
            "hnr": hnr,
        }

    def _features_to_mos(self, features: dict) -> float:
        """Convert audio features to MOS estimate."""
        # Normalize features
        snr_norm = np.clip((features["snr"] + 20) / 40, 0, 1)  # -20 to 20 dB
        centroid_norm = np.clip(features["spectral_centroid"] / 5000, 0, 1)
        zcr_norm = np.clip(features["zcr"] / 0.1, 0, 1)
        hnr_norm = np.clip((features["hnr"] + 10) / 30, 0, 1)  # -10 to 20 dB

        # Weighted combination (simple model)
        mos = (
            1.0  # Base score
            + snr_norm * 1.5  # SNR contribution
            + centroid_norm * 0.5  # Brightness contribution
            + (1 - zcr_norm) * 0.5  # Low noise contribution
            + hnr_norm * 1.5  # Harmonic content contribution
        )

        # Scale to 1-5 range
        mos = np.clip(mos, 1.0, 5.0)

        return float(mos)

    def _estimate_pesq(self, reference_path: Path, degraded_path: Path) -> float:
        """Estimate PESQ using alternative method."""
        # Load audio
        ref_audio, ref_sr = librosa.load(str(reference_path), sr=16000, mono=True)
        deg_audio, deg_sr = librosa.load(str(degraded_path), sr=16000, mono=True)

        # Ensure same length
        min_len = min(len(ref_audio), len(deg_audio))
        ref_audio = ref_audio[:min_len]
        deg_audio = deg_audio[:min_len]

        # Calculate correlation
        correlation = np.corrcoef(ref_audio, deg_audio)[0, 1]

        # Estimate PESQ from correlation (rough approximation)
        pesq_estimate = 1.0 + correlation * 3.5

        return float(np.clip(pesq_estimate, 0.0, 4.5))

    def _estimate_stoi(self, reference_path: Path, degraded_path: Path) -> float:
        """Estimate STOI using alternative method."""
        # Load audio
        ref_audio, ref_sr = librosa.load(str(reference_path), sr=16000, mono=True)
        deg_audio, deg_sr = librosa.load(str(degraded_path), sr=16000, mono=True)

        # Ensure same length
        min_len = min(len(ref_audio), len(deg_audio))
        ref_audio = ref_audio[:min_len]
        deg_audio = deg_audio[:min_len]

        # Calculate spectral similarity
        ref_stft = librosa.stft(ref_audio)
        deg_stft = librosa.stft(deg_audio)

        ref_mag = np.abs(ref_stft)
        deg_mag = np.abs(deg_stft)

        # Normalize
        ref_mag_norm = ref_mag / (np.max(ref_mag) + 1e-10)
        deg_mag_norm = deg_mag / (np.max(deg_mag) + 1e-10)

        # Calculate similarity
        similarity = np.mean(np.minimum(ref_mag_norm, deg_mag_norm))

        return float(np.clip(similarity, 0.0, 1.0))

    def calculate_all_metrics(
        self,
        reference_path: Optional[Path] = None,
        audio_path: Path = None,
        degraded_path: Optional[Path] = None,
    ) -> dict:
        """
        Calculate all available quality metrics.

        Args:
            reference_path: Path to reference audio (for PESQ/STOI)
            audio_path: Path to audio for MOS estimation
            degraded_path: Path to degraded audio (for PESQ/STOI)

        Returns:
            Dictionary with all metrics:
            {
                "pesq": 3.5,
                "stoi": 0.85,
                "mos": 4.2,
                "overall": 4.0
            }
        """
        metrics = {}

        # Calculate PESQ if reference and degraded provided
        if reference_path and degraded_path:
            metrics["pesq"] = self.calculate_pesq(reference_path, degraded_path)
            metrics["stoi"] = self.calculate_stoi(reference_path, degraded_path)

        # Calculate MOS
        if audio_path:
            metrics["mos"] = self.estimate_mos(audio_path)

        # Calculate overall score
        if metrics:
            scores = [v for v in metrics.values() if isinstance(v, (int, float))]
            if scores:
                # Normalize to 0-5 scale
                normalized_scores = []
                for score in scores:
                    if score <= 1.0:  # STOI
                        normalized_scores.append(score * 5)
                    elif score <= 4.5:  # PESQ
                        normalized_scores.append(score * 5 / 4.5)
                    else:  # MOS
                        normalized_scores.append(score)

                metrics["overall"] = float(np.mean(normalized_scores))

        return metrics


# Singleton instance
_quality_metrics_service: Optional[QualityMetricsService] = None


def get_quality_metrics() -> QualityMetricsService:
    """Get or create quality metrics service instance."""
    global _quality_metrics_service
    if _quality_metrics_service is None:
        _quality_metrics_service = QualityMetricsService()
    return _quality_metrics_service
