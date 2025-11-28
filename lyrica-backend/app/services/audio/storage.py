"""
Audio file storage service.

Handles saving, loading, and managing audio files on disk or cloud storage.
"""

import shutil
from pathlib import Path
from typing import BinaryIO, Optional

from loguru import logger

from app.core.audio_config import AudioFormat, get_audio_config


class AudioStorageService:
    """Service for storing and retrieving audio files."""

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize audio storage service.

        Args:
            base_path: Base directory for audio storage
        """
        self.config = get_audio_config()
        self.base_path = base_path or self.config.storage_path

        # Create storage directories
        self._initialize_storage()

    def _initialize_storage(self):
        """Create storage directory structure."""
        directories = [
            self.base_path / "songs",
            self.base_path / "voices",
            self.base_path / "music",
            self.base_path / "temp",
            self.base_path / "waveforms",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Storage directory ready: {directory}")

    def save_audio(
        self,
        file_data: BinaryIO,
        filename: str,
        category: str = "songs",
    ) -> Path:
        """
        Save audio file to storage.

        Args:
            file_data: Audio file binary data
            filename: Target filename
            category: Storage category (songs/voices/music/temp)

        Returns:
            Path to saved file

        Raises:
            ValueError: If category is invalid or file too large
        """
        # Validate category
        valid_categories = ["songs", "voices", "music", "temp", "waveforms"]
        if category not in valid_categories:
            raise ValueError(f"Invalid category. Must be one of: {valid_categories}")

        # Create target path
        target_dir = self.base_path / category
        target_path = target_dir / filename

        # Check file size
        file_data.seek(0, 2)  # Seek to end
        file_size_mb = file_data.tell() / (1024 * 1024)
        file_data.seek(0)  # Reset to start

        if file_size_mb > self.config.max_file_size_mb:
            raise ValueError(
                f"File too large: {file_size_mb:.2f}MB " f"(max: {self.config.max_file_size_mb}MB)"
            )

        # Save file
        with open(target_path, "wb") as f:
            shutil.copyfileobj(file_data, f)

        logger.info(f"Saved audio file: {target_path} ({file_size_mb:.2f}MB)")
        return target_path

    def load_audio(self, filepath: Path) -> BinaryIO:
        """
        Load audio file from storage.

        Args:
            filepath: Path to audio file

        Returns:
            Binary file object

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not filepath.exists():
            raise FileNotFoundError(f"Audio file not found: {filepath}")

        logger.info(f"Loading audio file: {filepath}")
        return open(filepath, "rb")

    def delete_audio(self, filepath: Path) -> bool:
        """
        Delete audio file from storage.

        Args:
            filepath: Path to audio file

        Returns:
            True if deleted, False if file didn't exist
        """
        if not filepath.exists():
            logger.warning(f"File not found for deletion: {filepath}")
            return False

        filepath.unlink()
        logger.info(f"Deleted audio file: {filepath}")
        return True

    def get_file_info(self, filepath: Path) -> dict:
        """
        Get information about an audio file.

        Args:
            filepath: Path to audio file

        Returns:
            Dictionary with file metadata
        """
        if not filepath.exists():
            raise FileNotFoundError(f"Audio file not found: {filepath}")

        stat = filepath.stat()
        return {
            "filename": filepath.name,
            "path": str(filepath),
            "size_bytes": stat.st_size,
            "size_mb": stat.st_size / (1024 * 1024),
            "created_at": stat.st_ctime,
            "modified_at": stat.st_mtime,
        }

    def cleanup_temp_files(self, max_age_hours: int = 24):
        """
        Clean up temporary audio files older than specified age.

        Args:
            max_age_hours: Maximum age in hours
        """
        import time

        temp_dir = self.base_path / "temp"
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600

        deleted_count = 0
        for file_path in temp_dir.glob("*"):
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    file_path.unlink()
                    deleted_count += 1

        logger.info(f"Cleaned up {deleted_count} temp files older than {max_age_hours}h")

    def get_storage_stats(self) -> dict:
        """
        Get storage statistics.

        Returns:
            Dictionary with storage stats
        """
        stats = {
            "base_path": str(self.base_path),
            "categories": {},
            "total_files": 0,
            "total_size_mb": 0,
        }

        for category in ["songs", "voices", "music", "temp", "waveforms"]:
            category_dir = self.base_path / category
            files = list(category_dir.glob("*"))
            total_size = sum(f.stat().st_size for f in files if f.is_file())

            stats["categories"][category] = {
                "file_count": len(files),
                "size_mb": total_size / (1024 * 1024),
            }
            stats["total_files"] += len(files)
            stats["total_size_mb"] += total_size / (1024 * 1024)

        return stats


# Singleton instance
_storage_service: Optional[AudioStorageService] = None


def get_audio_storage() -> AudioStorageService:
    """Get or create audio storage service instance."""
    global _storage_service
    if _storage_service is None:
        _storage_service = AudioStorageService()
    return _storage_service
