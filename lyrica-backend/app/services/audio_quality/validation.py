"""
Audio Quality Validation Service.

Validates audio files for quality issues and standards compliance.
"""

from pathlib import Path
from typing import Dict, List, Optional

import librosa
import numpy as np
from loguru import logger
from pydub import AudioSegment


class AudioValidationService:
    """Service for validating audio quality."""

    def __init__(self):
        """Initialize audio validation service."""
        logger.info("Audio validation service initialized")

    def validate_audio_file(
        self,
        audio_path: Path,
        min_duration_seconds: float = 1.0,
        max_duration_seconds: float = 600.0,
        min_sample_rate: int = 16000,
        max_file_size_mb: float = 100.0,
    ) -> Dict:
        """
        Validate audio file against quality standards.

        Args:
            audio_path: Path to audio file
            min_duration_seconds: Minimum acceptable duration
            max_duration_seconds: Maximum acceptable duration
            min_sample_rate: Minimum sample rate
            max_file_size_mb: Maximum file size in MB

        Returns:
            Validation results with passed/failed status and details
        """
        logger.info(f"Validating audio file: {audio_path}")

        results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "metrics": {},
        }

        try:
            # Check file exists
            if not audio_path.exists():
                results["is_valid"] = False
                results["errors"].append(f"File not found: {audio_path}")
                return results

            # Load audio with pydub for basic checks
            audio = AudioSegment.from_file(str(audio_path))
            duration = len(audio) / 1000.0  # Convert to seconds

            results["metrics"]["duration_seconds"] = duration
            results["metrics"]["sample_rate"] = audio.frame_rate
            results["metrics"]["channels"] = audio.channels
            results["metrics"]["bit_depth"] = audio.sample_width * 8

            # Check duration
            if duration < min_duration_seconds:
                results["is_valid"] = False
                results["errors"].append(
                    f"Duration too short: {duration:.2f}s (min: {min_duration_seconds}s)"
                )
            elif duration > max_duration_seconds:
                results["is_valid"] = False
                results["errors"].append(
                    f"Duration too long: {duration:.2f}s (max: {max_duration_seconds}s)"
                )

            # Check sample rate
            if audio.frame_rate < min_sample_rate:
                results["is_valid"] = False
                results["errors"].append(
                    f"Sample rate too low: {audio.frame_rate}Hz (min: {min_sample_rate}Hz)"
                )

            # Check file size
            file_size_mb = audio_path.stat().st_size / (1024 * 1024)
            results["metrics"]["file_size_mb"] = file_size_mb

            if file_size_mb > max_file_size_mb:
                results["warnings"].append(
                    f"Large file size: {file_size_mb:.2f}MB (recommended max: {max_file_size_mb}MB)"
                )

            # Load with librosa for detailed analysis
            y, sr = librosa.load(str(audio_path), sr=None)

            # Check for clipping
            clipping_ratio = self._check_clipping(y)
            results["metrics"]["clipping_ratio"] = clipping_ratio

            if clipping_ratio > 0.01:  # More than 1% clipping
                results["warnings"].append(
                    f"Audio clipping detected: {clipping_ratio * 100:.2f}% of samples"
                )

            # Check for silence
            silence_ratio = self._check_silence(y)
            results["metrics"]["silence_ratio"] = silence_ratio

            if silence_ratio > 0.3:  # More than 30% silence
                results["warnings"].append(
                    f"High silence ratio: {silence_ratio * 100:.2f}% of audio"
                )

            # Check dynamic range
            dynamic_range_db = self._calculate_dynamic_range(y)
            results["metrics"]["dynamic_range_db"] = dynamic_range_db

            if dynamic_range_db < 6.0:
                results["warnings"].append(
                    f"Low dynamic range: {dynamic_range_db:.2f}dB (recommended > 6dB)"
                )

            # Check for DC offset
            dc_offset = float(np.mean(y))
            results["metrics"]["dc_offset"] = dc_offset

            if abs(dc_offset) > 0.01:
                results["warnings"].append(f"DC offset detected: {dc_offset:.4f}")

            logger.success(
                f"Audio validation complete: {'PASSED' if results['is_valid'] else 'FAILED'}"
            )

        except Exception as e:
            logger.error(f"Error validating audio: {e}")
            results["is_valid"] = False
            results["errors"].append(f"Validation error: {str(e)}")

        return results

    def _check_clipping(self, y: np.ndarray, threshold: float = 0.99) -> float:
        """Check for audio clipping."""
        clipped_samples = np.sum(np.abs(y) >= threshold)
        return clipped_samples / len(y)

    def _check_silence(self, y: np.ndarray, threshold_db: float = -40.0) -> float:
        """Check for silence in audio."""
        rms = librosa.feature.rms(y=y)[0]
        rms_db = librosa.amplitude_to_db(rms, ref=np.max)
        silent_frames = np.sum(rms_db < threshold_db)
        return silent_frames / len(rms_db)

    def _calculate_dynamic_range(self, y: np.ndarray) -> float:
        """Calculate dynamic range in dB."""
        if len(y) == 0:
            return 0.0

        rms = np.sqrt(np.mean(y**2))
        peak = np.max(np.abs(y))

        if rms == 0 or peak == 0:
            return 0.0

        dynamic_range = 20 * np.log10(peak / rms)
        return float(dynamic_range)

    def validate_loudness(
        self,
        audio_path: Path,
        target_lufs: float = -14.0,
        tolerance_db: float = 2.0,
    ) -> Dict:
        """
        Validate audio loudness against broadcasting standards.

        Args:
            audio_path: Path to audio file
            target_lufs: Target integrated loudness (LUFS)
            tolerance_db: Acceptable deviation from target

        Returns:
            Validation results
        """
        logger.info(f"Validating loudness: {audio_path}")

        try:
            y, sr = librosa.load(str(audio_path), sr=None)

            # Calculate RMS as proxy for loudness (simplified)
            rms = np.sqrt(np.mean(y**2))
            rms_db = 20 * np.log10(rms) if rms > 0 else -100.0

            # Approximate LUFS conversion (simplified)
            estimated_lufs = rms_db - 3.0

            deviation = abs(estimated_lufs - target_lufs)
            is_valid = deviation <= tolerance_db

            return {
                "is_valid": is_valid,
                "estimated_lufs": estimated_lufs,
                "target_lufs": target_lufs,
                "deviation_db": deviation,
                "message": (
                    "Loudness within acceptable range"
                    if is_valid
                    else f"Loudness deviation: {deviation:.2f}dB"
                ),
            }

        except Exception as e:
            logger.error(f"Error validating loudness: {e}")
            return {
                "is_valid": False,
                "error": str(e),
            }

    def check_quality_score(self, audio_path: Path) -> Dict:
        """
        Calculate overall quality score (0-100).

        Args:
            audio_path: Path to audio file

        Returns:
            Quality score and breakdown
        """
        logger.info(f"Calculating quality score: {audio_path}")

        try:
            validation = self.validate_audio_file(audio_path)
            score = 100.0

            # Deduct points for errors and warnings
            score -= len(validation["errors"]) * 20
            score -= len(validation["warnings"]) * 5

            # Bonus for good metrics
            metrics = validation["metrics"]

            if metrics.get("clipping_ratio", 1.0) < 0.001:
                score += 5  # No clipping

            if metrics.get("dynamic_range_db", 0.0) > 10.0:
                score += 5  # Good dynamic range

            if metrics.get("silence_ratio", 1.0) < 0.1:
                score += 5  # Minimal silence

            score = max(0.0, min(100.0, score))

            return {
                "quality_score": score,
                "grade": self._get_quality_grade(score),
                "validation": validation,
            }

        except Exception as e:
            logger.error(f"Error calculating quality score: {e}")
            return {
                "quality_score": 0.0,
                "grade": "F",
                "error": str(e),
            }

    def _get_quality_grade(self, score: float) -> str:
        """Convert score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"


# Singleton instance
_audio_validation_service: Optional[AudioValidationService] = None


def get_audio_validation() -> AudioValidationService:
    """Get singleton audio validation service."""
    global _audio_validation_service
    if _audio_validation_service is None:
        _audio_validation_service = AudioValidationService()
    return _audio_validation_service
