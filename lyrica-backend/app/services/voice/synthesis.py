"""
Voice synthesis service using multiple TTS engines.

This module provides text-to-speech capabilities using various TTS engines
including Bark, Coqui TTS, and others.
"""

from pathlib import Path
from typing import Optional

from loguru import logger

from app.core.voice_config import TTSEngine, VoiceProfile, get_voice_config


class VoiceSynthesisService:
    """Service for voice synthesis (Text-to-Speech)."""

    def __init__(self):
        """Initialize voice synthesis service."""
        self.config = get_voice_config()
        self._bark_model = None
        self._coqui_model = None

        # Create voice directories
        self.config.voice_models_path.mkdir(parents=True, exist_ok=True)
        self.config.generated_voices_path.mkdir(parents=True, exist_ok=True)

    def _load_bark_model(self):
        """Load Bark TTS model (lazy loading)."""
        if self._bark_model is None:
            try:
                from bark import SAMPLE_RATE, generate_audio, preload_models

                logger.info("Loading Bark TTS model...")
                preload_models()
                self._bark_model = {
                    "generate": generate_audio,
                    "sample_rate": SAMPLE_RATE,
                }
                logger.success("Bark model loaded successfully")
            except ImportError:
                logger.error("Bark not installed. Install with: pip install bark")
                raise
            except Exception as e:
                logger.error(f"Failed to load Bark model: {e}")
                raise

    def _load_coqui_model(self):
        """Load Coqui TTS model (lazy loading)."""
        if self._coqui_model is None:
            try:
                from TTS.api import TTS

                logger.info("Loading Coqui TTS model...")
                # Use a fast, multilingual model
                tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts")
                self._coqui_model = tts
                logger.success("Coqui TTS model loaded successfully")
            except ImportError:
                logger.error("Coqui TTS not installed. Install with: pip install TTS")
                raise
            except Exception as e:
                logger.error(f"Failed to load Coqui model: {e}")
                raise

    def synthesize_text(
        self,
        text: str,
        voice_profile: VoiceProfile,
        output_path: Path,
        temperature: float = 0.7,
        speed: float = 1.0,
    ) -> Path:
        """
        Synthesize speech from text using specified voice profile.

        Args:
            text: Text to synthesize
            voice_profile: Voice profile to use
            output_path: Path to save audio file
            temperature: Sampling temperature (creativity)
            speed: Speech speed multiplier

        Returns:
            Path to generated audio file

        Example:
            ```python
            service = VoiceSynthesisService()
            profile = get_voice_profile("male_narrator_1")
            audio_path = service.synthesize_text(
                "Hello, world!",
                profile,
                Path("output.wav")
            )
            ```
        """
        logger.info(
            f"Synthesizing speech with {voice_profile.engine.value} engine: {len(text)} chars"
        )

        # Route to appropriate engine
        if voice_profile.engine == TTSEngine.BARK:
            return self._synthesize_with_bark(text, voice_profile, output_path, temperature)
        elif voice_profile.engine == TTSEngine.COQUI:
            return self._synthesize_with_coqui(text, voice_profile, output_path, speed)
        else:
            raise ValueError(f"Unsupported TTS engine: {voice_profile.engine}")

    def _synthesize_with_bark(
        self,
        text: str,
        voice_profile: VoiceProfile,
        output_path: Path,
        temperature: float,
    ) -> Path:
        """Synthesize speech using Bark TTS."""
        import numpy as np
        from scipy.io.wavfile import write as write_wav

        self._load_bark_model()

        try:
            # Generate audio
            audio_array = self._bark_model["generate"](
                text,
                history_prompt=voice_profile.engine_voice_id,
                text_temp=temperature,
                waveform_temp=temperature,
            )

            # Save to file
            sample_rate = self._bark_model["sample_rate"]
            write_wav(str(output_path), sample_rate, audio_array)

            logger.success(f"Bark synthesis complete: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Bark synthesis failed: {e}")
            raise

    def _synthesize_with_coqui(
        self,
        text: str,
        voice_profile: VoiceProfile,
        output_path: Path,
        speed: float,
    ) -> Path:
        """Synthesize speech using Coqui TTS."""
        self._load_coqui_model()

        try:
            # Generate audio
            self._coqui_model.tts_to_file(
                text=text,
                file_path=str(output_path),
                speaker=voice_profile.engine_voice_id,
                language=voice_profile.language,
                speed=speed,
            )

            logger.success(f"Coqui synthesis complete: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Coqui synthesis failed: {e}")
            raise

    def synthesize_lyrics(
        self,
        lyrics: str,
        voice_profile: VoiceProfile,
        output_path: Path,
        chunk_sentences: bool = True,
    ) -> Path:
        """
        Synthesize song lyrics with appropriate phrasing.

        This method handles long lyrics by chunking them intelligently
        and adding pauses between sections.

        Args:
            lyrics: Song lyrics (may contain [Verse], [Chorus] markers)
            voice_profile: Voice profile to use
            output_path: Output audio file path
            chunk_sentences: Whether to chunk by sentences

        Returns:
            Path to generated audio file
        """
        from pydub import AudioSegment

        logger.info("Synthesizing lyrics...")

        # Split lyrics into chunks (by line breaks or sentences)
        if chunk_sentences:
            chunks = [line.strip() for line in lyrics.split("\n") if line.strip()]
        else:
            chunks = self._chunk_text(lyrics, self.config.chunk_size)

        # Generate audio for each chunk
        audio_segments = []
        temp_dir = output_path.parent / "temp"
        temp_dir.mkdir(exist_ok=True)

        for i, chunk in enumerate(chunks):
            # Skip section markers
            if chunk.startswith("[") and chunk.endswith("]"):
                # Add longer pause for section markers
                silence = AudioSegment.silent(duration=1000)  # 1 second
                audio_segments.append(silence)
                continue

            # Generate audio for chunk
            chunk_path = temp_dir / f"chunk_{i}.wav"
            self.synthesize_text(chunk, voice_profile, chunk_path)

            # Load generated audio
            audio = AudioSegment.from_file(str(chunk_path))
            audio_segments.append(audio)

            # Add pause between lines
            silence = AudioSegment.silent(duration=self.config.silence_duration_ms)
            audio_segments.append(silence)

            # Cleanup temp file
            chunk_path.unlink()

        # Combine all segments
        combined = sum(audio_segments)
        combined.export(str(output_path), format=output_path.suffix[1:])

        # Cleanup temp directory
        temp_dir.rmdir()

        logger.success(f"Lyrics synthesis complete: {output_path}")
        return output_path

    def _chunk_text(self, text: str, chunk_size: int) -> list[str]:
        """
        Split text into chunks of approximately equal size.

        Args:
            text: Text to chunk
            chunk_size: Target chunk size in characters

        Returns:
            List of text chunks
        """
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0

        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = word_length
            else:
                current_chunk.append(word)
                current_length += word_length

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def estimate_duration(self, text: str, words_per_minute: int = 150) -> float:
        """
        Estimate speech duration for given text.

        Args:
            text: Text to estimate
            words_per_minute: Speaking rate (default: 150 wpm = average)

        Returns:
            Estimated duration in seconds
        """
        word_count = len(text.split())
        minutes = word_count / words_per_minute
        return minutes * 60


# Singleton instance
_synthesis_service: Optional[VoiceSynthesisService] = None


def get_voice_synthesis() -> VoiceSynthesisService:
    """Get or create voice synthesis service instance."""
    global _synthesis_service
    if _synthesis_service is None:
        _synthesis_service = VoiceSynthesisService()
    return _synthesis_service
