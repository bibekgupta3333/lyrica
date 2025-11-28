"""
Audio waveform generation service.

Generates visual waveforms and spectrograms from audio files.
"""

import io
from pathlib import Path
from typing import Optional

import librosa
import librosa.display
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from loguru import logger

from app.core.audio_config import get_audio_config

# Use non-interactive backend
matplotlib.use("Agg")


class AudioWaveformService:
    """Service for generating audio waveforms and visualizations."""

    def __init__(self):
        """Initialize waveform service."""
        self.config = get_audio_config()

    def generate_waveform(
        self,
        audio_path: Path,
        output_path: Optional[Path] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        color: Optional[str] = None,
    ) -> Path:
        """
        Generate waveform image from audio file.

        Args:
            audio_path: Path to audio file
            output_path: Optional output path for waveform image
            width: Image width in pixels
            height: Image height in pixels
            color: Waveform color (hex code)

        Returns:
            Path to generated waveform image
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Generating waveform for: {audio_path}")

        # Load audio
        y, sr = librosa.load(str(audio_path))

        # Set dimensions
        width = width or self.config.waveform_width
        height = height or self.config.waveform_height
        color = color or self.config.waveform_color

        # Create figure
        fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)

        # Plot waveform
        librosa.display.waveshow(y, sr=sr, ax=ax, color=color)

        # Style
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        ax.set_title("")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # Generate output path if not provided
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_waveform").with_suffix(".png")

        # Save
        plt.tight_layout()
        plt.savefig(str(output_path), dpi=100, bbox_inches="tight", facecolor="white")
        plt.close()

        logger.success(f"Waveform saved: {output_path}")
        return output_path

    def generate_spectrogram(
        self,
        audio_path: Path,
        output_path: Optional[Path] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> Path:
        """
        Generate spectrogram image from audio file.

        Args:
            audio_path: Path to audio file
            output_path: Optional output path
            width: Image width
            height: Image height

        Returns:
            Path to generated spectrogram image
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Generating spectrogram for: {audio_path}")

        # Load audio
        y, sr = librosa.load(str(audio_path))

        # Compute spectrogram
        D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)

        # Set dimensions
        width = width or self.config.waveform_width
        height = height or self.config.waveform_height

        # Create figure
        fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)

        # Plot spectrogram
        img = librosa.display.specshow(D, y_axis="log", x_axis="time", sr=sr, ax=ax, cmap="viridis")

        # Style
        ax.set_title("")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Frequency (Hz)")
        fig.colorbar(img, ax=ax, format="%+2.0f dB")

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_spectrogram").with_suffix(".png")

        # Save
        plt.tight_layout()
        plt.savefig(str(output_path), dpi=100, bbox_inches="tight", facecolor="white")
        plt.close()

        logger.success(f"Spectrogram saved: {output_path}")
        return output_path

    def generate_mel_spectrogram(
        self,
        audio_path: Path,
        output_path: Optional[Path] = None,
        n_mels: int = 128,
    ) -> Path:
        """
        Generate mel spectrogram.

        Args:
            audio_path: Path to audio file
            output_path: Optional output path
            n_mels: Number of mel bands

        Returns:
            Path to generated mel spectrogram
        """
        logger.info(f"Generating mel spectrogram for: {audio_path}")

        # Load audio
        y, sr = librosa.load(str(audio_path))

        # Compute mel spectrogram
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels)
        S_dB = librosa.power_to_db(S, ref=np.max)

        # Create figure
        fig, ax = plt.subplots(figsize=(18, 2.8), dpi=100)

        # Plot
        img = librosa.display.specshow(
            S_dB, x_axis="time", y_axis="mel", sr=sr, ax=ax, cmap="magma"
        )

        ax.set_title("")
        fig.colorbar(img, ax=ax, format="%+2.0f dB")

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_mel_spectrogram").with_suffix(
                ".png"
            )

        # Save
        plt.tight_layout()
        plt.savefig(str(output_path), dpi=100, bbox_inches="tight")
        plt.close()

        logger.success(f"Mel spectrogram saved: {output_path}")
        return output_path

    def generate_waveform_data(self, audio_path: Path, samples: int = 1000) -> dict:
        """
        Generate waveform data points (for frontend visualization).

        Args:
            audio_path: Path to audio file
            samples: Number of data points to return

        Returns:
            Dictionary with waveform data points
        """
        logger.info(f"Generating waveform data for: {audio_path}")

        # Load audio
        y, sr = librosa.load(str(audio_path))

        # Downsample for visualization
        step = max(1, len(y) // samples)
        y_sampled = y[::step]

        # Calculate time axis
        duration = librosa.get_duration(y=y, sr=sr)
        time_points = np.linspace(0, duration, len(y_sampled))

        data = {
            "time": time_points.tolist(),
            "amplitude": y_sampled.tolist(),
            "sample_rate": int(sr),
            "duration": float(duration),
            "samples": len(y_sampled),
        }

        logger.success(f"Generated {len(y_sampled)} waveform data points")
        return data


# Singleton instance
_waveform_service: Optional[AudioWaveformService] = None


def get_audio_waveform() -> AudioWaveformService:
    """Get or create waveform service instance."""
    global _waveform_service
    if _waveform_service is None:
        _waveform_service = AudioWaveformService()
    return _waveform_service
