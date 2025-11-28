"""
Vocal effects service.

This module provides various vocal effects including reverb, echo,
compression, EQ, and other audio enhancements.
"""

from pathlib import Path
from typing import Optional

import librosa
import numpy as np
import soundfile as sf
from loguru import logger
from pydub import AudioSegment
from pydub.effects import compress_dynamic_range

from app.core.voice_config import get_voice_config


class VocalEffectsService:
    """Service for applying vocal effects."""

    def __init__(self):
        """Initialize vocal effects service."""
        self.config = get_voice_config()

    def add_reverb(
        self,
        audio_path: Path,
        room_size: float = 0.5,
        damping: float = 0.5,
        wet_level: float = 0.3,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Add reverb effect to vocals.

        Args:
            audio_path: Path to audio file
            room_size: Room size (0.0-1.0)
            damping: High-frequency damping (0.0-1.0)
            wet_level: Mix level of effect (0.0-1.0)
            output_path: Optional output path

        Returns:
            Path to audio with reverb

        Note:
            This is a simplified reverb using convolution.
            Professional reverb requires specialized libraries like pedalboard.
        """
        logger.info(f"Adding reverb: room={room_size}, damping={damping}, wet={wet_level}")

        # Load audio
        y, sr = librosa.load(str(audio_path), sr=None)

        # Create simple reverb using convolution with exponential decay
        reverb_duration = 2.0  # seconds
        reverb_samples = int(sr * reverb_duration)

        # Create exponential decay impulse response
        decay_rate = -5 * (1 - room_size)  # Smaller room = faster decay
        t = np.linspace(0, reverb_duration, reverb_samples)
        impulse = np.exp(decay_rate * t) * np.random.randn(reverb_samples) * 0.1

        # Apply damping (low-pass filter)
        if damping > 0:
            from scipy.signal import butter, filtfilt

            cutoff = 5000 * (1 - damping)  # Hz
            b, a = butter(4, cutoff / (sr / 2), btype="low")
            impulse = filtfilt(b, a, impulse)

        # Convolve audio with impulse response
        y_reverb = np.convolve(y, impulse, mode="same")

        # Mix wet and dry signals
        y_mixed = (1 - wet_level) * y + wet_level * y_reverb

        # Normalize to prevent clipping
        y_mixed = y_mixed / np.max(np.abs(y_mixed))

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_reverb")

        # Save
        sf.write(str(output_path), y_mixed, sr)

        logger.success(f"Reverb applied: {output_path}")
        return output_path

    def add_echo(
        self,
        audio_path: Path,
        delay_ms: int = 500,
        decay: float = 0.3,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Add echo effect to vocals.

        Args:
            audio_path: Path to audio file
            delay_ms: Echo delay in milliseconds
            decay: Echo decay factor (0.0-1.0)
            output_path: Optional output path

        Returns:
            Path to audio with echo
        """
        logger.info(f"Adding echo: delay={delay_ms}ms, decay={decay}")

        # Load audio
        y, sr = librosa.load(str(audio_path), sr=None)

        # Calculate delay in samples
        delay_samples = int((delay_ms / 1000) * sr)

        # Create echo
        y_echo = np.zeros_like(y)
        y_echo[delay_samples:] = y[:-delay_samples] * decay

        # Mix original and echo
        y_mixed = y + y_echo

        # Normalize
        y_mixed = y_mixed / np.max(np.abs(y_mixed))

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_echo")

        # Save
        sf.write(str(output_path), y_mixed, sr)

        logger.success(f"Echo applied: {output_path}")
        return output_path

    def apply_compression(
        self,
        audio_path: Path,
        threshold: float = -20.0,
        ratio: float = 4.0,
        attack_ms: float = 5.0,
        release_ms: float = 50.0,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Apply dynamic range compression to vocals.

        Args:
            audio_path: Path to audio file
            threshold: Compression threshold in dB
            ratio: Compression ratio (e.g., 4:1 = 4.0)
            attack_ms: Attack time in milliseconds
            release_ms: Release time in milliseconds
            output_path: Optional output path

        Returns:
            Path to compressed audio
        """
        logger.info(f"Applying compression: threshold={threshold}dB, ratio={ratio}:1")

        # Load with pydub
        audio = AudioSegment.from_file(str(audio_path))

        # Apply compression
        compressed = compress_dynamic_range(
            audio,
            threshold=threshold,
            ratio=ratio,
            attack=attack_ms,
            release=release_ms,
        )

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_compressed")

        # Save
        compressed.export(str(output_path), format=audio_path.suffix[1:])

        logger.success(f"Compression applied: {output_path}")
        return output_path

    def apply_eq(
        self,
        audio_path: Path,
        low_shelf_db: float = 0.0,
        mid_db: float = 0.0,
        high_shelf_db: float = 0.0,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Apply basic 3-band EQ to vocals.

        Args:
            audio_path: Path to audio file
            low_shelf_db: Low frequencies adjustment (dB)
            mid_db: Mid frequencies adjustment (dB)
            high_shelf_db: High frequencies adjustment (dB)
            output_path: Optional output path

        Returns:
            Path to EQ'd audio

        Note:
            This is a simplified EQ. Professional EQ requires specialized DSP.
        """
        logger.info(
            f"Applying EQ: low={low_shelf_db:+.1f}dB, "
            f"mid={mid_db:+.1f}dB, high={high_shelf_db:+.1f}dB"
        )

        # Load audio
        y, sr = librosa.load(str(audio_path), sr=None)

        # Get STFT
        D = librosa.stft(y)

        # Frequency bands (simplified 3-band)
        freq_bins = D.shape[0]
        low_cutoff = int(freq_bins * 0.2)  # Up to 20%
        high_cutoff = int(freq_bins * 0.8)  # From 80%

        # Apply gain to frequency bands
        if low_shelf_db != 0:
            D[:low_cutoff] *= 10 ** (low_shelf_db / 20)

        if mid_db != 0:
            D[low_cutoff:high_cutoff] *= 10 ** (mid_db / 20)

        if high_shelf_db != 0:
            D[high_cutoff:] *= 10 ** (high_shelf_db / 20)

        # Inverse STFT
        y_eq = librosa.istft(D)

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_eq")

        # Save
        sf.write(str(output_path), y_eq, sr)

        logger.success(f"EQ applied: {output_path}")
        return output_path

    def add_harmony(
        self,
        audio_path: Path,
        harmony_intervals: list[int],
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Add harmony vocals by pitch-shifting.

        Args:
            audio_path: Path to audio file
            harmony_intervals: List of intervals in semitones (e.g., [3, 7] for third and fifth)
            output_path: Optional output path

        Returns:
            Path to audio with harmonies

        Example:
            Add major third and perfect fifth: harmony_intervals=[4, 7]
        """
        logger.info(f"Adding harmonies: {harmony_intervals}")

        from pydub import AudioSegment

        # Load original
        original = AudioSegment.from_file(str(audio_path))

        # Generate harmonies
        for interval in harmony_intervals:
            # Create harmony track with pitch shift
            temp_path = audio_path.with_stem(f"{audio_path.stem}_harmony{interval}")
            self.shift_pitch(audio_path, interval, temp_path)

            # Load and mix
            harmony = AudioSegment.from_file(str(temp_path))
            # Reduce volume of harmony (typically -6dB)
            harmony = harmony - 6
            # Mix with original
            original = original.overlay(harmony)

            # Cleanup
            temp_path.unlink()

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_harmony")

        # Save
        original.export(str(output_path), format=audio_path.suffix[1:])

        logger.success(f"Harmonies added: {output_path}")
        return output_path

    def denoise(
        self,
        audio_path: Path,
        noise_reduction_strength: float = 0.5,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Reduce background noise from vocals.

        Args:
            audio_path: Path to audio file
            noise_reduction_strength: Strength of noise reduction (0.0-1.0)
            output_path: Optional output path

        Returns:
            Path to denoised audio

        Note:
            This is a basic spectral gating approach.
            Professional denoising requires specialized models.
        """
        logger.info(f"Denoising audio (strength={noise_reduction_strength})")

        # Load audio
        y, sr = librosa.load(str(audio_path), sr=None)

        # Get magnitude spectrogram
        D = librosa.stft(y)
        magnitude, phase = librosa.magphase(D)

        # Estimate noise floor (from quietest parts)
        noise_floor = np.percentile(magnitude, 10 * noise_reduction_strength)

        # Apply spectral gate
        mask = magnitude > (noise_floor * (1 + noise_reduction_strength))
        magnitude_cleaned = magnitude * mask

        # Reconstruct audio
        D_cleaned = magnitude_cleaned * phase
        y_cleaned = librosa.istft(D_cleaned)

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_denoised")

        # Save
        sf.write(str(output_path), y_cleaned, sr)

        logger.success(f"Denoising applied: {output_path}")
        return output_path


# Singleton instance
_effects_service: Optional[VocalEffectsService] = None


def get_vocal_effects() -> VocalEffectsService:
    """Get or create vocal effects service instance."""
    global _effects_service
    if _effects_service is None:
        _effects_service = VocalEffectsService()
    return _effects_service
