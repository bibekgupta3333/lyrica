"""
Audio metadata extraction service.

Extracts and manages metadata from audio files (duration, bitrate, format, etc.).
"""

from pathlib import Path
from typing import Optional

import librosa
import soundfile as sf
from loguru import logger
from pydub import AudioSegment

from app.core.audio_config import AudioFormat


class AudioMetadataService:
    """Service for extracting audio file metadata."""

    def extract_metadata(self, filepath: Path) -> dict:
        """
        Extract comprehensive metadata from audio file.

        Args:
            filepath: Path to audio file

        Returns:
            Dictionary with audio metadata

        Example:
            ```python
            metadata = service.extract_metadata(Path("song.mp3"))
            print(f"Duration: {metadata['duration_seconds']}s")
            print(f"Sample rate: {metadata['sample_rate']}Hz")
            ```
        """
        if not filepath.exists():
            raise FileNotFoundError(f"Audio file not found: {filepath}")

        logger.info(f"Extracting metadata from: {filepath}")

        metadata = {
            "filename": filepath.name,
            "format": filepath.suffix[1:].lower(),
            "file_size_bytes": filepath.stat().st_size,
            "file_size_mb": filepath.stat().st_size / (1024 * 1024),
        }

        try:
            # Use librosa for detailed audio analysis
            y, sr = librosa.load(str(filepath), sr=None)

            metadata.update(
                {
                    "duration_seconds": float(librosa.get_duration(y=y, sr=sr)),
                    "sample_rate": int(sr),
                    "channels": 1 if len(y.shape) == 1 else y.shape[0],
                    "samples": len(y),
                }
            )

            # Extract additional features
            metadata["audio_features"] = self._extract_audio_features(y, sr)

            # Use pydub for format-specific info
            audio = AudioSegment.from_file(str(filepath))
            metadata.update(
                {
                    "bit_depth": audio.sample_width * 8,
                    "frame_rate": audio.frame_rate,
                    "frame_count": audio.frame_count(),
                    "rms": audio.rms,  # Root mean square (loudness)
                    "db_fs": audio.dBFS,  # Loudness in dBFS
                    "max_db_fs": audio.max_dBFS,
                }
            )

        except Exception as e:
            logger.warning(f"Could not extract full metadata: {e}")
            # Fallback to basic metadata
            try:
                audio = AudioSegment.from_file(str(filepath))
                metadata.update(
                    {
                        "duration_seconds": len(audio) / 1000.0,
                        "sample_rate": audio.frame_rate,
                        "channels": audio.channels,
                        "bit_depth": audio.sample_width * 8,
                    }
                )
            except Exception as fallback_error:
                logger.error(f"Metadata extraction failed: {fallback_error}")

        logger.success(f"Metadata extracted: {metadata.get('duration_seconds', 0):.2f}s")
        return metadata

    def _extract_audio_features(self, y, sr) -> dict:
        """
        Extract audio features using librosa.

        Args:
            y: Audio time series
            sr: Sample rate

        Returns:
            Dictionary of audio features
        """
        features = {}

        try:
            # Tempo (BPM)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            features["tempo_bpm"] = float(tempo)

            # Zero crossing rate (measure of noisiness)
            zcr = librosa.feature.zero_crossing_rate(y)
            features["zero_crossing_rate"] = float(zcr.mean())

            # Spectral centroid (brightness)
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
            features["spectral_centroid"] = float(spectral_centroids.mean())

            # Spectral rolloff
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            features["spectral_rolloff"] = float(spectral_rolloff.mean())

            # MFCCs (Mel-frequency cepstral coefficients)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            features["mfcc_mean"] = mfccs.mean(axis=1).tolist()

            # RMS Energy
            rms = librosa.feature.rms(y=y)
            features["rms_energy"] = float(rms.mean())

        except Exception as e:
            logger.warning(f"Could not extract audio features: {e}")

        return features

    def get_basic_info(self, filepath: Path) -> dict:
        """
        Get basic audio information quickly.

        Args:
            filepath: Path to audio file

        Returns:
            Dictionary with basic audio info
        """
        if not filepath.exists():
            raise FileNotFoundError(f"Audio file not found: {filepath}")

        try:
            info = sf.info(str(filepath))
            return {
                "duration_seconds": float(info.duration),
                "sample_rate": info.samplerate,
                "channels": info.channels,
                "format": info.format,
                "subtype": info.subtype,
            }
        except Exception as e:
            logger.error(f"Could not read audio info: {e}")
            raise

    def validate_audio_file(self, filepath: Path) -> tuple[bool, Optional[str]]:
        """
        Validate if file is a valid audio file.

        Args:
            filepath: Path to file

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not filepath.exists():
            return False, f"File not found: {filepath}"

        try:
            # Try to load with librosa
            y, sr = librosa.load(str(filepath), duration=1.0)  # Load only 1 second

            if len(y) == 0:
                return False, "Audio file is empty"

            if sr <= 0:
                return False, "Invalid sample rate"

            return True, None

        except Exception as e:
            return False, f"Invalid audio file: {str(e)}"

    def compare_audio_files(self, filepath1: Path, filepath2: Path) -> dict:
        """
        Compare two audio files.

        Args:
            filepath1: First audio file
            filepath2: Second audio file

        Returns:
            Dictionary with comparison results
        """
        metadata1 = self.extract_metadata(filepath1)
        metadata2 = self.extract_metadata(filepath2)

        comparison = {
            "file1": metadata1["filename"],
            "file2": metadata2["filename"],
            "duration_diff_seconds": abs(
                metadata1["duration_seconds"] - metadata2["duration_seconds"]
            ),
            "sample_rate_match": metadata1["sample_rate"] == metadata2["sample_rate"],
            "channels_match": metadata1["channels"] == metadata2["channels"],
            "format_match": metadata1["format"] == metadata2["format"],
            "size_diff_mb": abs(metadata1["file_size_mb"] - metadata2["file_size_mb"]),
        }

        return comparison


# Singleton instance
_metadata_service: Optional[AudioMetadataService] = None


def get_audio_metadata() -> AudioMetadataService:
    """Get or create audio metadata service instance."""
    global _metadata_service
    if _metadata_service is None:
        _metadata_service = AudioMetadataService()
    return _metadata_service
