"""
Audio format conversion service.

Handles conversion between different audio formats (MP3, WAV, OGG, etc.).
"""

from pathlib import Path
from typing import Optional

from loguru import logger
from pydub import AudioSegment

from app.core.audio_config import AudioFormat, AudioQuality, get_audio_config


class AudioConverterService:
    """Service for converting between audio formats."""

    def __init__(self):
        """Initialize audio converter service."""
        self.config = get_audio_config()

    def convert(
        self,
        input_path: Path,
        output_format: AudioFormat,
        quality: AudioQuality = AudioQuality.HIGH,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Convert audio file to specified format.

        Args:
            input_path: Path to input audio file
            output_format: Target audio format
            quality: Output quality preset
            output_path: Optional output path (auto-generated if None)

        Returns:
            Path to converted audio file

        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If format is unsupported
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Load audio
        logger.info(f"Loading audio from: {input_path}")
        audio = AudioSegment.from_file(str(input_path))

        # Generate output path if not provided
        if output_path is None:
            output_path = input_path.with_suffix(f".{output_format.value}")

        # Convert based on format
        logger.info(f"Converting to {output_format.value} (quality: {quality.value})")

        if output_format == AudioFormat.MP3:
            bitrate = f"{self.config.mp3_bitrate[quality]}k"
            audio.export(
                str(output_path),
                format="mp3",
                bitrate=bitrate,
                parameters=["-q:a", "0"],  # Highest quality VBR
            )

        elif output_format == AudioFormat.WAV:
            audio.export(
                str(output_path),
                format="wav",
            )

        elif output_format == AudioFormat.OGG:
            # OGG Vorbis
            quality_mapping = {
                AudioQuality.LOW: "3",
                AudioQuality.MEDIUM: "6",
                AudioQuality.HIGH: "9",
                AudioQuality.LOSSLESS: "10",
            }
            audio.export(
                str(output_path),
                format="ogg",
                codec="libvorbis",
                parameters=["-q:a", quality_mapping[quality]],
            )

        elif output_format == AudioFormat.FLAC:
            audio.export(
                str(output_path),
                format="flac",
            )

        elif output_format == AudioFormat.M4A:
            # AAC
            bitrate = f"{self.config.mp3_bitrate[quality]}k"
            audio.export(
                str(output_path),
                format="ipod",
                bitrate=bitrate,
                codec="aac",
            )

        else:
            raise ValueError(f"Unsupported format: {output_format}")

        logger.success(f"Converted audio saved to: {output_path}")
        return output_path

    def convert_sample_rate(
        self,
        input_path: Path,
        target_sample_rate: int,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Convert audio to different sample rate.

        Args:
            input_path: Path to input audio file
            target_sample_rate: Target sample rate in Hz
            output_path: Optional output path

        Returns:
            Path to converted audio file
        """
        logger.info(f"Converting sample rate to {target_sample_rate}Hz")

        audio = AudioSegment.from_file(str(input_path))
        audio = audio.set_frame_rate(target_sample_rate)

        if output_path is None:
            output_path = input_path.with_stem(f"{input_path.stem}_{target_sample_rate}hz")

        audio.export(str(output_path), format=input_path.suffix[1:])

        logger.success(f"Sample rate converted: {output_path}")
        return output_path

    def convert_channels(
        self,
        input_path: Path,
        channels: int,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Convert audio to mono or stereo.

        Args:
            input_path: Path to input audio file
            channels: Number of channels (1=mono, 2=stereo)
            output_path: Optional output path

        Returns:
            Path to converted audio file
        """
        logger.info(f"Converting to {channels} channel(s)")

        audio = AudioSegment.from_file(str(input_path))
        audio = audio.set_channels(channels)

        if output_path is None:
            channel_label = "mono" if channels == 1 else "stereo"
            output_path = input_path.with_stem(f"{input_path.stem}_{channel_label}")

        audio.export(str(output_path), format=input_path.suffix[1:])

        logger.success(f"Channels converted: {output_path}")
        return output_path

    def batch_convert(
        self,
        input_paths: list[Path],
        output_format: AudioFormat,
        quality: AudioQuality = AudioQuality.HIGH,
    ) -> list[Path]:
        """
        Convert multiple audio files.

        Args:
            input_paths: List of input file paths
            output_format: Target audio format
            quality: Output quality preset

        Returns:
            List of converted file paths
        """
        logger.info(f"Batch converting {len(input_paths)} files")

        output_paths = []
        for input_path in input_paths:
            try:
                output_path = self.convert(input_path, output_format, quality)
                output_paths.append(output_path)
            except Exception as e:
                logger.error(f"Failed to convert {input_path}: {e}")

        logger.success(
            f"Batch conversion complete: {len(output_paths)}/{len(input_paths)} succeeded"
        )
        return output_paths


# Singleton instance
_converter_service: Optional[AudioConverterService] = None


def get_audio_converter() -> AudioConverterService:
    """Get or create audio converter service instance."""
    global _converter_service
    if _converter_service is None:
        _converter_service = AudioConverterService()
    return _converter_service
