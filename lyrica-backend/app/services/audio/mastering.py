"""
Audio normalization and mastering service.

Applies professional audio mastering techniques including loudness normalization,
limiting, and dynamic range compression.
"""

from pathlib import Path
from typing import Optional

import librosa
import numpy as np
import pyloudnorm as pyln
import soundfile as sf
from loguru import logger
from pydub import AudioSegment
from pydub.effects import compress_dynamic_range, normalize

from app.core.audio_config import get_audio_config


class AudioMasteringService:
    """Service for audio normalization and mastering."""

    def __init__(self):
        """Initialize mastering service."""
        self.config = get_audio_config()

    def normalize_loudness(
        self,
        audio_path: Path,
        target_loudness: float = -14.0,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Normalize audio to target loudness (LUFS standard).

        Args:
            audio_path: Path to audio file
            target_loudness: Target loudness in LUFS (default: -14.0 for streaming)
            output_path: Optional output path

        Returns:
            Path to normalized audio

        Note:
            -14 LUFS is the standard for Spotify, YouTube, etc.
            -16 LUFS is for Apple Music
            -23 LUFS is for broadcast
        """
        logger.info(f"Normalizing loudness to {target_loudness} LUFS")

        # Load audio
        data, rate = sf.read(str(audio_path))

        # Measure loudness
        meter = pyln.Meter(rate)
        loudness = meter.integrated_loudness(data)

        logger.info(f"Current loudness: {loudness:.2f} LUFS")

        # Normalize
        normalized_audio = pyln.normalize.loudness(data, loudness, target_loudness)

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(
                f"{audio_path.stem}_normalized_{int(target_loudness)}lufs"
            )

        # Save
        sf.write(str(output_path), normalized_audio, rate)

        logger.success(
            f"Normalized from {loudness:.2f} to {target_loudness:.2f} LUFS: {output_path}"
        )
        return output_path

    def apply_peak_limiting(
        self,
        audio_path: Path,
        threshold_db: float = -1.0,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Apply peak limiting to prevent clipping.

        Args:
            audio_path: Path to audio file
            threshold_db: Peak limit threshold in dB
            output_path: Optional output path

        Returns:
            Path to limited audio
        """
        logger.info(f"Applying peak limiting at {threshold_db}dBTP")

        # Load audio
        data, rate = sf.read(str(audio_path))

        # Calculate peak
        peak = np.max(np.abs(data))
        peak_db = 20 * np.log10(peak)

        logger.info(f"Current peak: {peak_db:.2f}dB")

        # Apply limiting if needed
        if peak_db > threshold_db:
            # Calculate scaling factor
            scale = 10 ** (threshold_db / 20) / peak
            limited_audio = data * scale

            logger.info(f"Reduced peak from {peak_db:.2f} to {threshold_db}dB")
        else:
            limited_audio = data
            logger.info("No limiting needed (peak already below threshold)")

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_limited")

        # Save
        sf.write(str(output_path), limited_audio, rate)

        logger.success(f"Peak limited audio saved: {output_path}")
        return output_path

    def apply_compression(
        self,
        audio_path: Path,
        threshold: float = -20.0,
        ratio: float = 4.0,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Apply dynamic range compression.

        Args:
            audio_path: Path to audio file
            threshold: Compression threshold in dB
            ratio: Compression ratio (e.g., 4:1 = 4.0)
            output_path: Optional output path

        Returns:
            Path to compressed audio
        """
        logger.info(f"Applying compression: threshold={threshold}dB, ratio={ratio}:1")

        # Load with pydub
        audio = AudioSegment.from_file(str(audio_path))

        # Apply compression
        compressed = compress_dynamic_range(audio, threshold=threshold, ratio=ratio)

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_compressed")

        # Save
        compressed.export(str(output_path), format=audio_path.suffix[1:])

        logger.success(f"Compressed audio saved: {output_path}")
        return output_path

    def apply_harmonic_enhancement(
        self,
        audio_path: Path,
        enhancement_strength: float = 0.3,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        PHASE 3: Apply harmonic enhancement for richer, warmer sound.

        Adds subtle harmonic content to enhance the perceived quality
        and warmth of the audio.

        Args:
            audio_path: Path to audio file
            enhancement_strength: Enhancement strength (0.0-1.0)
            output_path: Optional output path

        Returns:
            Path to enhanced audio

        Example:
            ```python
            enhanced = service.apply_harmonic_enhancement(
                Path("audio.wav"),
                enhancement_strength=0.3
            )
            ```
        """
        logger.info(f"Applying harmonic enhancement: strength={enhancement_strength}")

        # Load audio
        y, sr = librosa.load(str(audio_path), sr=None)

        # Generate harmonics (second and third harmonics)
        # Second harmonic (octave)
        y_harmonic2 = librosa.effects.pitch_shift(y, sr=sr, n_steps=12) * enhancement_strength * 0.3
        # Third harmonic (octave + fifth)
        y_harmonic3 = (
            librosa.effects.pitch_shift(y, sr=sr, n_steps=19) * enhancement_strength * 0.15
        )

        # Mix harmonics with original
        enhanced = y + y_harmonic2 + y_harmonic3

        # Normalize to prevent clipping
        max_val = np.max(np.abs(enhanced))
        if max_val > 0.95:
            enhanced = enhanced / max_val * 0.95

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_harmonic_enhanced")

        # Save
        sf.write(str(output_path), enhanced, sr)

        logger.success(f"Harmonic enhancement applied: {output_path}")
        return output_path

    def enhance_stereo_width(
        self,
        audio_path: Path,
        width_factor: float = 1.1,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        PHASE 3: Enhance stereo width of audio.

        Widens the stereo field for a more immersive sound.

        Args:
            audio_path: Path to audio file
            width_factor: Stereo width factor (1.0 = no change, >1.0 = wider)
            output_path: Optional output path

        Returns:
            Path to enhanced audio

        Example:
            ```python
            widened = service.enhance_stereo_width(
                Path("audio.wav"),
                width_factor=1.2
            )
            ```
        """
        logger.info(f"Enhancing stereo width: factor={width_factor}")

        # Load audio
        y, sr = librosa.load(str(audio_path), sr=None, mono=False)

        # Handle mono audio
        if y.ndim == 1:
            # Convert to stereo
            y = np.array([y, y])

        # Mid/side processing
        mid = (y[0] + y[1]) / 2
        side = (y[0] - y[1]) / 2

        # Enhance side signal
        side_enhanced = side * width_factor

        # Reconstruct stereo
        left = mid + side_enhanced
        right = mid - side_enhanced

        # Normalize to prevent clipping
        max_val = max(np.max(np.abs(left)), np.max(np.abs(right)))
        if max_val > 0.95:
            left = left / max_val * 0.95
            right = right / max_val * 0.95

        enhanced = np.array([left, right])

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_stereo_enhanced")

        # Save
        sf.write(str(output_path), enhanced.T, sr)

        logger.success(f"Stereo width enhanced: {output_path}")
        return output_path

    def master_audio(
        self,
        audio_path: Path,
        target_loudness: float = -14.0,
        peak_limit: float = -1.0,
        apply_compression: bool = True,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Apply complete mastering chain.

        This applies a professional mastering chain:
        1. Dynamic range compression (optional)
        2. Loudness normalization
        3. Peak limiting

        Args:
            audio_path: Path to audio file
            target_loudness: Target loudness in LUFS
            peak_limit: Peak limit in dBTP
            apply_compression: Whether to apply compression
            output_path: Optional output path

        Returns:
            Path to mastered audio
        """
        logger.info("Applying full mastering chain")

        temp_path = audio_path

        # Step 1: Compression (optional)
        if apply_compression:
            temp_path = self.apply_compression(
                temp_path,
                threshold=-20.0,
                ratio=4.0,
                output_path=audio_path.with_stem(f"{audio_path.stem}_temp1"),
            )

        # Step 2: Loudness normalization
        temp_path = self.normalize_loudness(
            temp_path,
            target_loudness=target_loudness,
            output_path=audio_path.with_stem(f"{audio_path.stem}_temp2"),
        )

        # Step 3: Peak limiting
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_mastered")

        final_path = self.apply_peak_limiting(
            temp_path, threshold_db=peak_limit, output_path=output_path
        )

        # Clean up temp files
        if apply_compression:
            audio_path.with_stem(f"{audio_path.stem}_temp1").unlink(missing_ok=True)
        audio_path.with_stem(f"{audio_path.stem}_temp2").unlink(missing_ok=True)

        logger.success(f"Mastering complete: {final_path}")
        return final_path

    def analyze_loudness(self, audio_path: Path) -> dict:
        """
        Analyze audio loudness metrics.

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary with loudness measurements
        """
        logger.info(f"Analyzing loudness: {audio_path}")

        # Load audio
        data, rate = sf.read(str(audio_path))

        # Initialize meter
        meter = pyln.Meter(rate)

        # Measure loudness
        integrated_loudness = meter.integrated_loudness(data)

        # Peak measurements
        peak = np.max(np.abs(data))
        peak_db = 20 * np.log10(peak) if peak > 0 else -np.inf

        # RMS (average loudness)
        rms = np.sqrt(np.mean(data**2))
        rms_db = 20 * np.log10(rms) if rms > 0 else -np.inf

        # Dynamic range
        dynamic_range = peak_db - rms_db

        analysis = {
            "integrated_loudness_lufs": float(integrated_loudness),
            "true_peak_dbtp": float(peak_db),
            "rms_db": float(rms_db),
            "dynamic_range_db": float(dynamic_range),
            "sample_rate": int(rate),
            "duration_seconds": float(len(data) / rate),
        }

        logger.info(f"Loudness: {integrated_loudness:.2f} LUFS")
        logger.info(f"True Peak: {peak_db:.2f} dBTP")
        logger.info(f"Dynamic Range: {dynamic_range:.2f} dB")

        return analysis


# Singleton instance
_mastering_service: Optional[AudioMasteringService] = None


def get_audio_mastering() -> AudioMasteringService:
    """Get or create audio mastering service instance."""
    global _mastering_service
    if _mastering_service is None:
        _mastering_service = AudioMasteringService()
    return _mastering_service
