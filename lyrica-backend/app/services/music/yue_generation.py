"""
YuE Full-Song Generation Service.

Integrates YuE model for professional-quality full-song generation.

YuE is an open-source full-song generation model that generates complete songs
with vocals and music together, similar to Suno.ai.

Repository: https://github.com/Decentralised-AI/YuE-Open-Full-song-Music-Generation

Key Features:
- Dual-track in-context learning
- Style transfer
- Voice cloning
- Lyric alignment
- Full-song generation (vocals + music)

Installation:
1. Clone the repository:
   git clone https://github.com/Decentralised-AI/YuE-Open-Full-song-Music-Generation.git
   cd YuE-Open-Full-song-Music-Generation

2. Install dependencies:
   pip install -r requirements.txt

3. Download model weights (follow repository instructions)

4. Install YuE package (if available):
   pip install yue  # Or install from source

Note: The exact installation steps may vary. Check the repository README for
the latest instructions.
"""

from pathlib import Path
from typing import Optional

from loguru import logger

from app.core.music_config import MusicGenre, get_music_config


class YueGenerationService:
    """
    Service for YuE full-song generation.

    YuE generates complete songs with vocals and music together, providing
    professional-quality output similar to commercial services like Suno.ai.
    """

    def __init__(self):
        """Initialize YuE service."""
        self.config = get_music_config()
        self._yue_model = None
        self._yue_available = self._check_yue_availability()

        # Create output directory
        self.config.generated_music_path.mkdir(parents=True, exist_ok=True)

        if self._yue_available:
            logger.success("YuE service initialized - YuE model available")
        else:
            logger.info(
                "YuE service initialized - YuE not available. "
                "Install from: https://github.com/Decentralised-AI/YuE-Open-Full-song-Music-Generation"
            )

    def _check_yue_availability(self) -> bool:
        """
        Check if YuE is available and can be imported.

        Returns:
            True if YuE is available, False otherwise
        """
        try:
            # Try importing YuE
            # Note: The exact import path may vary based on YuE installation
            # Common possibilities:
            # - from yue import YueModel
            # - from yue_model import YueModel
            # - import yue

            # For now, we'll check for common patterns
            # This will be updated once YuE installation is verified

            # Check if yue module exists
            try:
                import importlib

                # Try to find yue module
                importlib.util.find_spec("yue")
                # If found, try importing
                # from yue import YueModel  # Uncomment when YuE is installed
                # return True
            except (ImportError, ModuleNotFoundError):
                pass

            # Alternative: Check if YuE is installed via pip
            # This is a placeholder - actual implementation depends on YuE's API
            return False

        except Exception as e:
            logger.debug(f"YuE availability check failed: {e}")
            return False

    def is_available(self) -> bool:
        """
        Check if YuE is available for use.

        Returns:
            True if YuE is available, False otherwise
        """
        return self._yue_available

    def _load_yue_model(self):
        """
        Load YuE model (lazy loading).

        Raises:
            ImportError: If YuE is not installed
            RuntimeError: If model loading fails
        """
        if not self._yue_available:
            raise ImportError(
                "YuE not installed. "
                "See installation guide: "
                "https://github.com/Decentralised-AI/YuE-Open-Full-song-Music-Generation"
            )

        if self._yue_model is None:
            try:
                # Load YuE model
                # Implementation depends on YuE's actual API
                # Example (to be updated based on actual API):
                # from yue import YueModel
                # self._yue_model = YueModel.from_pretrained("yue-model")
                # Or:
                # self._yue_model = YueModel.load("path/to/model")

                logger.info("Loading YuE model...")
                # Placeholder - actual implementation needed
                # self._yue_model = YueModel.from_pretrained("yue-model")
                logger.success("YuE model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load YuE model: {e}")
                raise RuntimeError(f"YuE model loading failed: {e}") from e

    def generate_full_song(
        self,
        lyrics: str,
        genre: MusicGenre,
        duration: int = 180,
        style: Optional[str] = None,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Generate full song with vocals and music using YuE.

        Args:
            lyrics: Song lyrics (can be plain text or structured)
            genre: Music genre
            duration: Duration in seconds (default: 180 = 3 minutes)
            style: Optional style reference (e.g., "pop", "rock", "acoustic")
            output_path: Optional output path for generated song

        Returns:
            Path to generated full song (WAV format)

        Raises:
            ImportError: If YuE is not installed
            RuntimeError: If generation fails

        Example:
            ```python
            service = YueGenerationService()
            if service.is_available():
                song_path = service.generate_full_song(
                    lyrics="Verse 1...\\nChorus...",
                    genre=MusicGenre.POP,
                    duration=180,
                    style="professional"
                )
            ```
        """
        if not self._yue_available:
            raise ImportError(
                "YuE not installed. "
                "Install from: https://github.com/Decentralised-AI/YuE-Open-Full-song-Music-Generation"
            )

        # Load model if needed
        if self._yue_model is None:
            self._load_yue_model()

        # Generate output path if not provided
        if output_path is None:
            output_path = (
                self.config.generated_music_path / f"yue_song_{genre.value}_{duration}s.wav"
            )

        logger.info(
            f"Generating full song with YuE: genre={genre.value}, "
            f"duration={duration}s, style={style}"
        )

        try:
            # Generate full song using YuE
            # Implementation depends on YuE's actual API
            # Example (to be updated based on actual API):
            # song_audio = self._yue_model.generate(
            #     lyrics=lyrics,
            #     genre=genre.value,
            #     duration=duration,
            #     style=style,
            # )
            #
            # # Save to file
            # import soundfile as sf
            # sf.write(str(output_path), song_audio, sample_rate=44100)

            # Placeholder implementation
            # TODO: Replace with actual YuE API calls once YuE is installed
            logger.warning(
                "YuE generation not yet implemented - placeholder code. "
                "Install YuE and update this method with actual API calls."
            )

            # For now, raise an error to indicate YuE needs to be properly integrated
            raise NotImplementedError(
                "YuE generation not yet implemented. "
                "Please install YuE and update the generate_full_song method "
                "with the actual YuE API calls. "
                "See: https://github.com/Decentralised-AI/YuE-Open-Full-song-Music-Generation"
            )

            # logger.success(f"YuE full song generated: {output_path}")
            # return output_path

        except NotImplementedError:
            raise
        except Exception as e:
            logger.error(f"YuE generation failed: {e}")
            raise RuntimeError(f"YuE generation failed: {e}") from e

    def generate_music_only(
        self,
        prompt: str,
        genre: MusicGenre,
        duration: int = 180,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Generate instrumental music only (without vocals) using YuE.

        Args:
            prompt: Text description of desired music
            genre: Music genre
            duration: Duration in seconds
            output_path: Optional output path

        Returns:
            Path to generated instrumental music

        Raises:
            ImportError: If YuE is not installed
            RuntimeError: If generation fails
        """
        if not self._yue_available:
            raise ImportError(
                "YuE not installed. "
                "Install from: https://github.com/Decentralised-AI/YuE-Open-Full-song-Music-Generation"
            )

        # Load model if needed
        if self._yue_model is None:
            self._load_yue_model()

        # Generate output path if not provided
        if output_path is None:
            output_path = (
                self.config.generated_music_path / f"yue_music_{genre.value}_{duration}s.wav"
            )

        logger.info(
            f"Generating instrumental music with YuE: genre={genre.value}, "
            f"duration={duration}s, prompt={prompt[:50]}..."
        )

        try:
            # Generate instrumental music using YuE
            # Implementation depends on YuE's actual API
            # Example (to be updated based on actual API):
            # music_audio = self._yue_model.generate_music(
            #     prompt=prompt,
            #     genre=genre.value,
            #     duration=duration,
            #     vocals=False,  # Instrumental only
            # )
            #
            # # Save to file
            # import soundfile as sf
            # sf.write(str(output_path), music_audio, sample_rate=44100)

            # Placeholder implementation
            raise NotImplementedError(
                "YuE music generation not yet implemented. "
                "Please install YuE and update this method with actual API calls."
            )

        except NotImplementedError:
            raise
        except Exception as e:
            logger.error(f"YuE music generation failed: {e}")
            raise RuntimeError(f"YuE music generation failed: {e}") from e


def get_yue_generation() -> YueGenerationService:
    """
    Get or create YuE generation service instance (singleton pattern).

    Returns:
        YueGenerationService instance
    """
    global _yue_service_instance
    if "_yue_service_instance" not in globals():
        _yue_service_instance = YueGenerationService()
    return _yue_service_instance
