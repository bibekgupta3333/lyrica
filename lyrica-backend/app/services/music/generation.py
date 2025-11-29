"""
Music generation service using MusicGen/AudioCraft.

This module provides AI-powered music generation capabilities including
genre-based generation, melody creation, and instrumental composition.
"""

from pathlib import Path
from typing import Optional

from loguru import logger

from app.core.music_config import (
    MusicGenre,
    MusicKey,
    MusicMood,
    get_genre_bpm_range,
    get_music_config,
)


class MusicGenerationService:
    """Service for AI-powered music generation."""

    def __init__(self):
        """Initialize music generation service."""
        self.config = get_music_config()
        self._musicgen_model = None

        # Create directories
        self.config.generated_music_path.mkdir(parents=True, exist_ok=True)
        self.config.music_models_path.mkdir(parents=True, exist_ok=True)

    def _load_musicgen_model(self):
        """Load MusicGen model (lazy loading)."""
        if self._musicgen_model is None:
            try:
                from audiocraft.models import MusicGen

                logger.info(f"Loading MusicGen model: {self.config.model_name}")
                self._musicgen_model = MusicGen.get_pretrained(
                    self.config.model_name,
                    device="cuda" if self.config.use_gpu else "cpu",
                )
                logger.success("MusicGen model loaded successfully")
            except ImportError:
                logger.error("AudioCraft not installed. Install with: pip install audiocraft")
                raise
            except Exception as e:
                logger.error(f"Failed to load MusicGen model: {e}")
                raise

    def generate_music(
        self,
        prompt: str,
        duration: int = 30,
        output_path: Optional[Path] = None,
        temperature: float = 1.0,
    ) -> Path:
        """
        Generate music from text prompt.

        Args:
            prompt: Text description of desired music
            duration: Duration in seconds
            output_path: Optional output path
            temperature: Sampling temperature (0.5-2.0)

        Returns:
            Path to generated audio file

        Example:
            ```python
            service = MusicGenerationService()
            audio_path = service.generate_music(
                prompt="upbeat pop music with piano and drums",
                duration=30
            )
            ```
        """
        self._load_musicgen_model()

        logger.info(f"Generating music: '{prompt}' ({duration}s)")

        try:
            # Set generation parameters
            self._musicgen_model.set_generation_params(
                duration=min(duration, self.config.max_generation_length),
                temperature=temperature,
            )

            # Generate music
            wav = self._musicgen_model.generate([prompt])

            # Save to file
            if output_path is None:
                output_path = self.config.generated_music_path / f"music_{prompt[:20]}.wav"

            import torchaudio

            torchaudio.save(
                str(output_path),
                wav[0].cpu(),
                sample_rate=self._musicgen_model.sample_rate,
            )

            logger.success(f"Music generated: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Music generation failed: {e}")
            raise

    def generate_by_genre(
        self,
        genre: MusicGenre,
        mood: Optional[MusicMood] = None,
        key: Optional[MusicKey] = None,
        bpm: Optional[int] = None,
        duration: int = 30,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Generate music for specific genre.

        Args:
            genre: Music genre
            mood: Optional mood/emotion
            key: Optional musical key
            bpm: Optional tempo (beats per minute)
            duration: Duration in seconds
            output_path: Optional output path

        Returns:
            Path to generated audio file

        Example:
            ```python
            audio_path = service.generate_by_genre(
                genre=MusicGenre.POP,
                mood=MusicMood.HAPPY,
                key=MusicKey.C_MAJOR,
                bpm=120,
                duration=30
            )
            ```
        """
        # Build prompt from parameters
        prompt_parts = [genre.value, "music"]

        if mood:
            prompt_parts.insert(0, mood.value)

        if key:
            prompt_parts.append(f"in {key.value}")

        if bpm:
            prompt_parts.append(f"at {bpm} BPM")
        else:
            # Use typical BPM for genre
            min_bpm, max_bpm = get_genre_bpm_range(genre)
            typical_bpm = (min_bpm + max_bpm) // 2
            prompt_parts.append(f"at {typical_bpm} BPM")

        prompt = " ".join(prompt_parts)

        logger.info(f"Generating {genre.value} music with prompt: '{prompt}'")

        return self.generate_music(prompt=prompt, duration=duration, output_path=output_path)

    def generate_instrumental(
        self,
        instruments: list[str],
        genre: Optional[MusicGenre] = None,
        duration: int = 30,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Generate instrumental music with specific instruments.

        Args:
            instruments: List of instruments (e.g., ["piano", "guitar", "drums"])
            genre: Optional genre
            duration: Duration in seconds
            output_path: Optional output path

        Returns:
            Path to generated audio file

        Example:
            ```python
            audio_path = service.generate_instrumental(
                instruments=["piano", "violin", "cello"],
                genre=MusicGenre.CLASSICAL,
                duration=60
            )
            ```
        """
        # Build prompt
        instruments_str = ", ".join(instruments)
        prompt_parts = [instruments_str]

        if genre:
            prompt_parts.append(genre.value)

        prompt_parts.append("instrumental music")
        prompt = " ".join(prompt_parts)

        logger.info(f"Generating instrumental with: {instruments_str}")

        return self.generate_music(prompt=prompt, duration=duration, output_path=output_path)

    def generate_with_melody(
        self,
        melody_audio_path: Path,
        genre: Optional[MusicGenre] = None,
        duration: int = 30,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Generate music based on a melody audio file.

        Args:
            melody_audio_path: Path to melody audio file
            genre: Optional genre
            duration: Duration in seconds
            output_path: Optional output path

        Returns:
            Path to generated audio file

        Note:
            This uses MusicGen's melody conditioning feature.
        """
        self._load_musicgen_model()

        logger.info(f"Generating music from melody: {melody_audio_path}")

        try:
            import torchaudio

            # Load melody audio
            melody, sr = torchaudio.load(str(melody_audio_path))

            # Build prompt
            prompt = f"{genre.value} music" if genre else "music"

            # Generate with melody conditioning
            self._musicgen_model.set_generation_params(duration=duration)
            wav = self._musicgen_model.generate_with_chroma(
                descriptions=[prompt], melody_wavs=melody[None], melody_sample_rate=sr
            )

            # Save to file
            if output_path is None:
                output_path = self.config.generated_music_path / f"music_melody_{duration}s.wav"

            torchaudio.save(
                str(output_path),
                wav[0].cpu(),
                sample_rate=self._musicgen_model.sample_rate,
            )

            logger.success(f"Music generated with melody: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Melody-based generation failed: {e}")
            raise

    def generate_structure(
        self,
        sections: list[tuple[str, int]],
        genre: MusicGenre,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Generate music with specific structure (intro, verse, chorus, etc.).

        Args:
            sections: List of (section_name, duration) tuples
            genre: Music genre
            output_path: Optional output path

        Returns:
            Path to generated audio file

        Example:
            ```python
            sections = [
                ("intro", 8),
                ("verse", 16),
                ("chorus", 16),
                ("verse", 16),
                ("chorus", 16),
                ("outro", 8)
            ]
            audio_path = service.generate_structure(
                sections=sections,
                genre=MusicGenre.POP
            )
            ```
        """
        from pydub import AudioSegment

        logger.info(f"Generating structured {genre.value} music")

        segments = []

        for section_name, section_duration in sections:
            logger.info(f"Generating {section_name} ({section_duration}s)")

            # Customize prompt based on section
            if section_name == "intro":
                prompt = f"intro for {genre.value} song, gentle build-up"
            elif section_name == "verse":
                prompt = f"{genre.value} verse, melodic and rhythmic"
            elif section_name == "chorus":
                prompt = f"{genre.value} chorus, energetic and catchy"
            elif section_name == "bridge":
                prompt = f"{genre.value} bridge, contrasting section"
            elif section_name == "outro":
                prompt = f"{genre.value} outro, fade out"
            else:
                prompt = f"{genre.value} {section_name}"

            # Generate section
            temp_path = self.config.generated_music_path / f"temp_{section_name}.wav"
            self.generate_music(prompt=prompt, duration=section_duration, output_path=temp_path)

            # Load and add to segments
            segment = AudioSegment.from_file(str(temp_path))
            segments.append(segment)

            # Cleanup temp file
            temp_path.unlink()

        # Combine all sections
        combined = sum(segments)

        # Save final audio
        if output_path is None:
            output_path = self.config.generated_music_path / f"music_structured_{genre.value}.wav"

        combined.export(str(output_path), format="wav")

        logger.success(f"Structured music generated: {output_path}")
        return output_path


# Singleton instance
_music_generation_service: Optional[MusicGenerationService] = None


def get_music_generation() -> MusicGenerationService:
    """Get or create music generation service instance."""
    global _music_generation_service
    if _music_generation_service is None:
        _music_generation_service = MusicGenerationService()
    return _music_generation_service
