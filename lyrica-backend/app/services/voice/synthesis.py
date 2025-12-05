"""
Voice synthesis service using multiple TTS engines.

This module provides text-to-speech capabilities using various TTS engines
including Bark, Coqui TTS, and others.
"""

import warnings
from pathlib import Path
from typing import Optional

from loguru import logger

from app.core.voice_config import TTSEngine, VoiceProfile, get_voice_config

# Suppress warnings from audio packages
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


class VoiceSynthesisService:
    """Service for voice synthesis (Text-to-Speech)."""

    def __init__(self):
        """Initialize voice synthesis service."""
        self.config = get_voice_config()
        self._bark_model: Optional[dict] = None
        self._coqui_model: Optional[object] = None
        self._tortoise_model: Optional[object] = None
        self._vad_model: Optional[object] = None
        self._pyttsx3_engine: Optional[object] = None

        # Create voice directories
        self.config.voice_models_path.mkdir(parents=True, exist_ok=True)
        self.config.generated_voices_path.mkdir(parents=True, exist_ok=True)

    def _load_bark_model(self):
        """Load Bark TTS model (lazy loading)."""
        if self._bark_model is None:
            try:
                from bark import SAMPLE_RATE, generate_audio, preload_models
                from bark.generation import ALLOWED_PROMPTS

                logger.info("Loading Bark TTS model (v0.1.5+)...")
                # Preload models with optimizations
                preload_models(
                    text_use_gpu=self.config.use_gpu,
                    coarse_use_gpu=self.config.use_gpu,
                    fine_use_gpu=self.config.use_gpu,
                )
                self._bark_model = {
                    "generate": generate_audio,
                    "sample_rate": SAMPLE_RATE,
                    "allowed_prompts": ALLOWED_PROMPTS,
                }
                logger.success(f"Bark model loaded successfully (GPU: {self.config.use_gpu})")
            except ImportError as e:
                logger.error(
                    f"Bark not installed. Install with: pip install bark>=0.1.5. Error: {e}"
                )
                raise
            except Exception as e:
                logger.error(f"Failed to load Bark model: {e}")
                raise

    def _load_coqui_model(self):
        """Load Coqui TTS model (lazy loading)."""
        if self._coqui_model is None:
            try:
                from TTS.api import TTS

                logger.info("Loading Coqui TTS model (v0.22.0+)...")
                # Use a fast, high-quality multilingual model
                gpu = self.config.use_gpu
                tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", gpu=gpu)
                self._coqui_model = tts
                logger.success(f"Coqui TTS model loaded successfully (GPU: {gpu})")
            except ImportError as e:
                logger.error(
                    f"Coqui TTS not installed. Install with: pip install TTS>=0.22.0. Error: {e}"
                )
                raise
            except Exception as e:
                logger.error(f"Failed to load Coqui model: {e}")
                raise

    def _load_tortoise_model(self):
        """Load Tortoise TTS model (lazy loading)."""
        if self._tortoise_model is None:
            try:
                from tortoise.api import TextToSpeech

                logger.info("Loading Tortoise TTS model (v3.0.0+)...")
                # Initialize with optimizations
                tts = TextToSpeech(
                    use_deepspeed=False,
                    kv_cache=True,
                    half=self.config.use_gpu,  # Use FP16 if GPU enabled
                )
                self._tortoise_model = tts
                logger.success(
                    f"Tortoise TTS model loaded successfully (GPU: {self.config.use_gpu})"
                )
            except ImportError as e:
                logger.error(
                    f"Tortoise TTS not installed. Install with: pip install tortoise-tts>=3.0.0. Error: {e}"
                )
                raise
            except Exception as e:
                logger.error(f"Failed to load Tortoise model: {e}")
                raise

    def _load_vad_model(self):
        """Load Silero VAD model for voice activity detection."""
        if self._vad_model is None:
            try:
                import torch
                from silero_vad import load_silero_vad

                logger.info("Loading Silero VAD model (v5.1.0+)...")
                model = load_silero_vad()
                self._vad_model = model
                logger.success("Silero VAD model loaded successfully")
            except ImportError as e:
                logger.error(
                    f"Silero VAD not installed. Install with: pip install silero-vad>=5.1.0. Error: {e}"
                )
                raise
            except Exception as e:
                logger.error(f"Failed to load Silero VAD model: {e}")
                raise

    def synthesize_text(
        self,
        text: str,
        voice_profile: VoiceProfile,
        output_path: Path,
        temperature: float = 0.7,
        speed: float = 1.0,
        enable_enhancement: bool = True,
    ) -> Path:
        """
        Synthesize speech from text using specified voice profile.

        Args:
            text: Text to synthesize
            voice_profile: Voice profile to use
            output_path: Path to save audio file
            temperature: Sampling temperature (creativity)
            speed: Speech speed multiplier
            enable_enhancement: Whether to apply voice enhancement (default: True)

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

        # Create temporary path for initial synthesis
        temp_path = output_path.parent / f"{output_path.stem}_temp{output_path.suffix}"

        # Route to appropriate engine
        if voice_profile.engine == TTSEngine.BARK:
            audio_path = self._synthesize_with_bark(text, voice_profile, temp_path, temperature)
        elif voice_profile.engine == TTSEngine.COQUI:
            audio_path = self._synthesize_with_coqui(text, voice_profile, temp_path, speed)
        elif voice_profile.engine == TTSEngine.TORTOISE:
            audio_path = self._synthesize_with_tortoise(text, voice_profile, temp_path, temperature)
        elif voice_profile.engine == TTSEngine.EDGE:
            audio_path = self._synthesize_with_edge(text, voice_profile, temp_path, speed)
        elif voice_profile.engine == TTSEngine.GTTS:
            audio_path = self._synthesize_with_gtts(text, voice_profile, temp_path, speed)
        elif voice_profile.engine == TTSEngine.PYTTSX3:
            audio_path = self._synthesize_with_pyttsx3(text, voice_profile, temp_path, speed)
        else:
            raise ValueError(f"Unsupported TTS engine: {voice_profile.engine}")

        # Apply voice enhancement if enabled
        if enable_enhancement:
            try:
                from app.services.voice import get_voice_enhancement

                enhancement_service = get_voice_enhancement()
                audio_path = enhancement_service.enhance_tts_output(
                    tts_audio_path=audio_path,
                    output_path=output_path,
                    enable_enhancement=True,
                )

                # Cleanup temp file if different from output
                if temp_path != output_path and temp_path.exists():
                    temp_path.unlink()

                return audio_path
            except Exception as e:
                logger.warning(f"Voice enhancement failed, using original audio: {e}")
                # Move temp file to output if enhancement failed
                if temp_path != output_path and temp_path.exists():
                    import shutil

                    shutil.move(str(temp_path), str(output_path))
                    return output_path
                return audio_path
        else:
            # Move temp file to output if enhancement disabled
            if temp_path != output_path and temp_path.exists():
                import shutil

                shutil.move(str(temp_path), str(output_path))
            return output_path

    def _synthesize_with_bark(
        self,
        text: str,
        voice_profile: VoiceProfile,
        output_path: Path,
        temperature: float,
    ) -> Path:
        """Synthesize speech using Bark TTS (v0.1.5+)."""
        import numpy as np
        from scipy.io.wavfile import write as write_wav

        self._load_bark_model()

        try:
            if self._bark_model is None:
                raise RuntimeError("Bark model not loaded")

            # Generate audio with latest Bark API
            audio_array = self._bark_model["generate"](  # type: ignore
                text,
                history_prompt=voice_profile.engine_voice_id,
                text_temp=temperature,
                waveform_temp=temperature,
                silent=False,  # Show progress
                output_full=False,  # Only return audio array
            )

            # Normalize audio to prevent clipping
            audio_array = np.clip(audio_array, -1.0, 1.0)

            # Convert to 16-bit PCM
            audio_int16 = (audio_array * 32767).astype(np.int16)

            # Save to file
            sample_rate = self._bark_model["sample_rate"]  # type: ignore
            write_wav(str(output_path), sample_rate, audio_int16)

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
        """Synthesize speech using Coqui TTS (v0.22.0+)."""
        self._load_coqui_model()

        try:
            if self._coqui_model is None:
                raise RuntimeError("Coqui model not loaded")

            # Generate audio with XTTS v2
            self._coqui_model.tts_to_file(  # type: ignore
                text=text,
                file_path=str(output_path),
                speaker=voice_profile.engine_voice_id,
                language=voice_profile.language,
                speed=speed,
                split_sentences=True,  # Better handling of long text
            )

            logger.success(f"Coqui synthesis complete: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Coqui synthesis failed: {e}")
            raise

    def _synthesize_with_tortoise(
        self,
        text: str,
        voice_profile: VoiceProfile,
        output_path: Path,
        temperature: float,
    ) -> Path:
        """Synthesize speech using Tortoise TTS (v3.0.0+)."""
        import torchaudio

        self._load_tortoise_model()

        try:
            if self._tortoise_model is None:
                raise RuntimeError("Tortoise model not loaded")

            # Generate audio with Tortoise
            # Note: Tortoise requires voice samples for cloning
            # Using preset voices for now
            voice_samples = None  # Can be provided for voice cloning

            gen = self._tortoise_model.tts_with_preset(  # type: ignore
                text,
                voice_samples=voice_samples,
                preset="fast",  # Options: ultra_fast, fast, standard, high_quality
                temperature=temperature,
            )

            # Save to file
            torchaudio.save(str(output_path), gen.squeeze(0).cpu(), 24000)  # Tortoise uses 24kHz

            logger.success(f"Tortoise synthesis complete: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Tortoise synthesis failed: {e}")
            raise

    def _synthesize_with_edge(
        self,
        text: str,
        voice_profile: VoiceProfile,
        output_path: Path,
        speed: float,
    ) -> Path:
        """Synthesize speech using Microsoft Edge TTS (Python 3.12 compatible)."""
        import edge_tts

        from app.utils.async_utils import run_async_in_thread

        try:

            async def generate():
                # Calculate rate adjustment
                rate_percent = int((speed - 1.0) * 100)
                rate_str = f"{rate_percent:+d}%"

                communicate = edge_tts.Communicate(
                    text, voice_profile.engine_voice_id, rate=rate_str
                )
                await communicate.save(str(output_path))

            # Run async function safely (handles both sync and async contexts)
            run_async_in_thread(generate())

            logger.success(f"Edge TTS synthesis complete: {output_path}")
            return output_path

        except ImportError as e:
            logger.error(
                f"Edge TTS not installed. Install with: pip install edge-tts>=6.1.0. Error: {e}"
            )
            raise
        except Exception as e:
            logger.error(f"Edge TTS synthesis failed: {e}")
            raise

    def _synthesize_with_gtts(
        self,
        text: str,
        voice_profile: VoiceProfile,
        output_path: Path,
        speed: float,
    ) -> Path:
        """Synthesize speech using Google TTS (Python 3.12 compatible)."""
        try:
            from gtts import gTTS

            # Extract language code
            lang = (
                voice_profile.language[:2]
                if len(voice_profile.language) > 2
                else voice_profile.language
            )

            # Generate audio
            tts = gTTS(text=text, lang=lang, slow=(speed < 0.9))
            tts.save(str(output_path))

            logger.success(f"Google TTS synthesis complete: {output_path}")
            return output_path

        except ImportError as e:
            logger.error(f"gTTS not installed. Install with: pip install gTTS>=2.5.0. Error: {e}")
            raise
        except Exception as e:
            logger.error(f"Google TTS synthesis failed: {e}")
            raise

    def _load_pyttsx3_engine(self):
        """Load pyttsx3 TTS engine (lazy loading)."""
        if self._pyttsx3_engine is None:
            try:
                import pyttsx3

                logger.info("Initializing pyttsx3 engine...")
                engine = pyttsx3.init()
                self._pyttsx3_engine = engine
                logger.success("pyttsx3 engine initialized")
            except ImportError as e:
                logger.error(
                    f"pyttsx3 not installed. Install with: pip install pyttsx3>=2.90. Error: {e}"
                )
                raise
            except Exception as e:
                logger.error(f"Failed to initialize pyttsx3: {e}")
                raise

    def _synthesize_with_pyttsx3(
        self,
        text: str,
        voice_profile: VoiceProfile,
        output_path: Path,
        speed: float,
    ) -> Path:
        """Synthesize speech using pyttsx3 (Python 3.12 compatible, offline)."""
        self._load_pyttsx3_engine()

        try:
            if self._pyttsx3_engine is None:
                raise RuntimeError("pyttsx3 engine not initialized")

            # Configure engine
            self._pyttsx3_engine.setProperty("rate", int(150 * speed))  # type: ignore # Words per minute

            # Set voice if specified
            voices = self._pyttsx3_engine.getProperty("voices")  # type: ignore
            if voice_profile.engine_voice_id and voice_profile.engine_voice_id.isdigit():
                voice_idx = int(voice_profile.engine_voice_id)
                if voices and 0 <= voice_idx < len(voices):  # type: ignore
                    self._pyttsx3_engine.setProperty("voice", voices[voice_idx].id)  # type: ignore

            # Save to file
            self._pyttsx3_engine.save_to_file(text, str(output_path))  # type: ignore
            self._pyttsx3_engine.runAndWait()  # type: ignore

            logger.success(f"pyttsx3 synthesis complete: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"pyttsx3 synthesis failed: {e}")
            raise

    def synthesize_lyrics(
        self,
        lyrics: str,
        voice_profile: VoiceProfile,
        output_path: Path,
        chunk_sentences: bool = True,
        enable_enhancement: bool = True,
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
            enable_enhancement: Whether to apply voice enhancement (default: True)

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
            self.synthesize_text(
                chunk, voice_profile, chunk_path, enable_enhancement=enable_enhancement
            )

            # Load generated audio
            audio = AudioSegment.from_file(str(chunk_path))
            audio_segments.append(audio)

            # Add pause between lines
            silence = AudioSegment.silent(duration=self.config.silence_duration_ms)
            audio_segments.append(silence)

            # Cleanup temp file
            chunk_path.unlink()

        # Combine all segments
        if not audio_segments:
            raise ValueError("No audio segments to combine")

        combined = audio_segments[0]
        for segment in audio_segments[1:]:
            combined = combined + segment  # type: ignore

        # Save combined audio
        temp_combined_path = temp_dir / "combined.wav"
        combined.export(str(temp_combined_path), format="wav")  # type: ignore

        # Apply final enhancement to combined audio if enabled
        if enable_enhancement:
            try:
                from app.services.voice import get_voice_enhancement

                enhancement_service = get_voice_enhancement()
                output_path = enhancement_service.enhance_tts_output(
                    tts_audio_path=temp_combined_path,
                    output_path=output_path,
                    enable_enhancement=True,
                )
            except Exception as e:
                logger.warning(f"Final enhancement failed, using combined audio: {e}")
                import shutil

                shutil.move(str(temp_combined_path), str(output_path))
        else:
            import shutil

            shutil.move(str(temp_combined_path), str(output_path))

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

    def detect_voice_activity(
        self, audio_path: Path, threshold: float = 0.5
    ) -> list[tuple[float, float]]:
        """Detect voice activity in audio file using Silero VAD.

        Args:
            audio_path: Path to audio file
            threshold: Voice activity threshold (0-1)

        Returns:
            List of (start_time, end_time) tuples in seconds
        """
        import torch
        import torchaudio

        self._load_vad_model()

        try:
            if self._vad_model is None:
                raise RuntimeError("VAD model not loaded")

            # Load audio
            wav, sr = torchaudio.load(str(audio_path))

            # Resample to 16kHz if needed (VAD requirement)
            if sr != 16000:
                resampler = torchaudio.transforms.Resample(sr, 16000)
                wav = resampler(wav)
                sr = 16000

            # Get speech timestamps
            speech_timestamps = self._vad_model(  # type: ignore
                wav,
                sr,
                threshold=threshold,
                min_speech_duration_ms=250,
                min_silence_duration_ms=100,
            )

            # Convert to seconds
            segments = [(ts["start"] / sr, ts["end"] / sr) for ts in speech_timestamps]

            logger.info(f"Detected {len(segments)} voice activity segments")
            return segments

        except Exception as e:
            logger.error(f"Voice activity detection failed: {e}")
            raise

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
