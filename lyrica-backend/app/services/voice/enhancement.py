"""
Voice enhancement service using neural vocoders and audio processing.

This module provides voice quality enhancement capabilities including:
- Neural vocoder-based enhancement (HiFi-GAN)
- Audio quality improvement
- Naturalness enhancement
- Integration with existing TTS pipeline
"""

import warnings
from pathlib import Path
from typing import Optional

import librosa
import numpy as np
import soundfile as sf
from loguru import logger

from app.core.voice_config import VoiceConfig, get_voice_config

# Suppress warnings from audio packages
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


class VoiceEnhancementService:
    """
    Service for enhancing voice quality using neural vocoders and audio processing.

    This service can improve the quality of TTS-generated audio by:
    - Using HiFi-GAN neural vocoder for high-quality resynthesis
    - Applying audio enhancement techniques
    - Improving naturalness and clarity
    """

    def __init__(self):
        """Initialize voice enhancement service."""
        self.config: VoiceConfig = get_voice_config()
        self._vocoder_model: Optional[object] = None
        self._hifigan_available: bool = False
        self._vocoder_type: Optional[str] = None

        # Check neural vocoder availability
        self._check_hifigan_availability()

    def _check_hifigan_availability(self) -> None:
        """
        Check if neural vocoder is available and can be loaded.

        Tries Vocos first (Python 3.12 compatible), then parallel-wavegan.
        Falls back to enhanced audio processing if neither is available.
        """
        # Try Vocos first (Python 3.12 compatible alternative)
        try:
            from vocos import Vocos

            self._hifigan_available = True
            self._vocoder_type = "vocos"
            logger.info("Vocos neural vocoder is available for voice enhancement")
            return
        except ImportError:
            pass

        # Try parallel-wavegan (legacy, may not work on Python 3.12)
        try:
            from parallel_wavegan.utils import load_model  # noqa: F401

            self._hifigan_available = True
            self._vocoder_type = "parallel_wavegan"
            logger.info("HiFi-GAN (parallel-wavegan) is available")
            return
        except ImportError:
            pass

        # Neither available - use audio processing
        self._hifigan_available = False
        self._vocoder_type = None
        logger.info(
            "Neural vocoders not available. " "Using enhanced audio processing methods instead."
        )

    def _load_vocoder_model(self):
        """
        Load neural vocoder model (lazy loading).

        Supports Vocos (Python 3.12 compatible) and parallel-wavegan (legacy).
        """
        if self._vocoder_model is not None:
            return

        if not self._hifigan_available:
            raise RuntimeError("Neural vocoder is not available")

        try:
            if self._vocoder_type == "vocos":
                self._load_vocos_model()
            elif self._vocoder_type == "parallel_wavegan":
                self._load_parallel_wavegan_model()
            else:
                raise RuntimeError(f"Unknown vocoder type: {self._vocoder_type}")

        except Exception as e:
            logger.error(f"Failed to load vocoder model: {e}")
            self._hifigan_available = False
            raise

    def _load_vocos_model(self):
        """Load Vocos neural vocoder (Python 3.12 compatible)."""
        from vocos import Vocos

        logger.info("Loading Vocos neural vocoder...")

        # Vocos can use pretrained models from Hugging Face
        # Default: facebook/tts_hifigan (HiFi-GAN compatible)
        try:
            self._vocoder_model = Vocos.from_pretrained("charactr/vocos-mel-24khz")
            logger.success("Vocos model loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load pretrained Vocos model: {e}")
            # Try alternative model
            try:
                self._vocoder_model = Vocos.from_pretrained("facebook/tts_hifigan")
                logger.success("Vocos model (facebook/tts_hifigan) loaded")
            except Exception as e2:
                logger.error(f"Failed to load any Vocos model: {e2}")
                # Fallback: use default Vocos without pretrained weights
                self._vocoder_model = Vocos()
                logger.warning("Using Vocos without pretrained weights")

    def _load_parallel_wavegan_model(self):
        """Load parallel-wavegan HiFi-GAN model (legacy)."""
        import torch  # noqa: F401
        from parallel_wavegan.utils import load_model

        logger.info("Loading HiFi-GAN (parallel-wavegan) model...")

        model_path = self.config.voice_models_path / "hifigan" / "checkpoint.pkl"

        if model_path.exists():
            self._vocoder_model = load_model(str(model_path))
            logger.success("HiFi-GAN model loaded successfully")
        else:
            logger.warning(
                f"HiFi-GAN model not found at {model_path}. " "Using fallback enhancement methods."
            )
            self._hifigan_available = False
            raise RuntimeError("HiFi-GAN model not found")

    def enhance_audio(
        self,
        audio_path: Path,
        output_path: Optional[Path] = None,
        method: str = "auto",
        quality: str = "high",
    ) -> Path:
        """
        Enhance audio quality using neural vocoder or audio processing.

        Args:
            audio_path: Path to input audio file
            output_path: Path to save enhanced audio (default: overwrite input)
            method: Enhancement method ("hifigan", "audio_processing", "auto")
            quality: Quality preset ("low", "medium", "high")

        Returns:
            Path to enhanced audio file

        Example:
            ```python
            service = VoiceEnhancementService()
            enhanced = service.enhance_audio(
                Path("vocals.wav"),
                output_path=Path("vocals_enhanced.wav")
            )
            ```
        """
        if output_path is None:
            output_path = audio_path

        logger.info(f"Enhancing audio: {audio_path} -> {output_path}")

        # Choose enhancement method
        # Note: For Python 3.12, audio_processing is the primary method
        # as parallel-wavegan (HiFi-GAN) has compatibility issues
        if method == "auto":
            # Prefer audio processing for Python 3.12 compatibility
            method = "hifigan" if self._hifigan_available else "audio_processing"
        elif method == "hifigan" and not self._hifigan_available:
            logger.info(
                "HiFi-GAN not available (parallel-wavegan has Python 3.12 "
                "compatibility issues). Using enhanced audio processing."
            )
            method = "audio_processing"

        # Apply enhancement
        if method == "hifigan":
            return self._enhance_with_hifigan(audio_path, output_path, quality)
        else:
            return self._enhance_with_audio_processing(audio_path, output_path, quality)

    def _enhance_with_hifigan(self, audio_path: Path, output_path: Path, quality: str) -> Path:
        """
        Enhance audio using neural vocoder (Vocos or HiFi-GAN).

        This method:
        1. Converts audio to mel-spectrogram
        2. Processes through neural vocoder
        3. Generates high-quality audio output
        """
        try:
            self._load_vocoder_model()

            if self._vocoder_model is None:
                raise RuntimeError("Vocoder model not loaded")

            import torch

            # Load audio
            audio, sr = librosa.load(str(audio_path), sr=22050, mono=True)

            if self._vocoder_type == "vocos":
                # Use Vocos vocoder
                return self._enhance_with_vocos(audio, sr, output_path)
            elif self._vocoder_type == "parallel_wavegan":
                # Use parallel-wavegan HiFi-GAN
                return self._enhance_with_parallel_wavegan(audio, sr, output_path)
            else:
                raise RuntimeError(f"Unknown vocoder type: {self._vocoder_type}")

        except Exception as e:
            logger.error(f"Neural vocoder enhancement failed: {e}")
            logger.info("Falling back to audio processing enhancement")
            return self._enhance_with_audio_processing(audio_path, output_path, quality)

    def _enhance_with_vocos(self, audio: np.ndarray, sr: int, output_path: Path) -> Path:
        """Enhance audio using Vocos neural vocoder."""
        import torch

        # Vocos expects mel-spectrogram input with 100 mel bins
        mel_spec = self._audio_to_melspectrogram(audio, sr, vocoder_type="vocos")

        # Convert to tensor (Vocos expects [batch, n_mels, time])
        mel_tensor = torch.FloatTensor(mel_spec).unsqueeze(0)

        # Generate audio with Vocos
        with torch.no_grad():
            enhanced_audio = self._vocoder_model.decode(mel_tensor)

        # Convert to numpy
        if isinstance(enhanced_audio, torch.Tensor):
            enhanced_audio = enhanced_audio.squeeze().cpu().numpy()

        # Ensure mono
        if len(enhanced_audio.shape) > 1:
            enhanced_audio = np.mean(enhanced_audio, axis=0)

        # Normalize
        enhanced_audio = np.clip(enhanced_audio, -1.0, 1.0)

        # Save enhanced audio (Vocos outputs at 24kHz)
        sf.write(str(output_path), enhanced_audio, 24000)

        logger.success(f"Vocos enhancement complete: {output_path}")
        return output_path

    def _enhance_with_parallel_wavegan(self, audio: np.ndarray, sr: int, output_path: Path) -> Path:
        """Enhance audio using parallel-wavegan HiFi-GAN (legacy)."""
        import torch

        # Convert to mel-spectrogram (80 mel bins for HiFi-GAN)
        mel_spec = self._audio_to_melspectrogram(audio, sr, vocoder_type="parallel_wavegan")

        # Convert to tensor
        mel_tensor = torch.FloatTensor(mel_spec).unsqueeze(0)

        # Generate audio with HiFi-GAN
        with torch.no_grad():
            if hasattr(self._vocoder_model, "inference"):
                enhanced_audio = self._vocoder_model.inference(mel_tensor)
            else:
                enhanced_audio = self._vocoder_model(mel_tensor)

        # Convert to numpy
        if isinstance(enhanced_audio, torch.Tensor):
            enhanced_audio = enhanced_audio.squeeze().cpu().numpy()

        # Normalize
        enhanced_audio = np.clip(enhanced_audio, -1.0, 1.0)

        # Save enhanced audio
        sf.write(str(output_path), enhanced_audio, 22050)

        logger.success(f"HiFi-GAN enhancement complete: {output_path}")
        return output_path

    def _enhance_with_audio_processing(
        self, audio_path: Path, output_path: Path, quality: str
    ) -> Path:
        """
        Enhance audio using traditional audio processing techniques.

        This is a fallback method when neural vocoders are not available.
        It applies noise reduction, EQ enhancement, compression, normalization.
        """
        try:
            # Load audio
            audio, sr = librosa.load(str(audio_path), sr=None, mono=True)

            logger.info(f"Applying audio processing enhancement (quality: {quality})")

            # Apply noise reduction (spectral gating)
            audio = self._reduce_noise(audio, sr)

            # Apply EQ enhancement
            audio = self._enhance_eq(audio, sr, quality)

            # Apply compression
            audio = self._apply_compression(audio, sr, quality)

            # Normalize
            audio = self._normalize_audio(audio)

            # Save enhanced audio
            sf.write(str(output_path), audio, sr)

            logger.success(f"Audio processing enhancement complete: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Audio processing enhancement failed: {e}")
            raise

    def _audio_to_melspectrogram(
        self, audio: np.ndarray, sr: int, vocoder_type: Optional[str] = None
    ) -> np.ndarray:
        """
        Convert audio to mel-spectrogram compatible with neural vocoders.

        Args:
            audio: Audio waveform
            sr: Sample rate
            vocoder_type: Type of vocoder ("vocos" or "parallel_wavegan")

        Returns:
            Mel-spectrogram array
        """
        if vocoder_type == "vocos":
            # Vocos expects 100 mel bins (charactr/vocos-mel-24khz)
            n_mels = 100
            hop_length = 256
            n_fft = 1024
            fmax = 12000
        else:
            # HiFi-GAN/parallel-wavegan typically expects:
            # - 80 mel bins
            # - Sample rate: 22050 Hz
            # - Hop length: 256
            # - Window length: 1024
            n_mels = 80
            hop_length = 256
            n_fft = 1024
            fmax = 8000

        mel_spec = librosa.feature.melspectrogram(
            y=audio,
            sr=sr,
            n_mels=n_mels,
            hop_length=hop_length,
            n_fft=n_fft,
            fmin=0,
            fmax=fmax,
        )

        # Convert to log scale
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)

        # Normalize to [-1, 1]
        mel_spec_norm = (mel_spec_db + 80) / 80.0
        mel_spec_norm = np.clip(mel_spec_norm, -1.0, 1.0)

        return mel_spec_norm

    def _reduce_noise(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """
        Reduce noise using spectral gating.

        Args:
            audio: Audio waveform
            sr: Sample rate

        Returns:
            Denoised audio
        """
        # Simple spectral gating noise reduction
        # Compute STFT
        stft = librosa.stft(audio, hop_length=512, n_fft=2048)
        magnitude = np.abs(stft)
        phase = np.angle(stft)

        # Estimate noise floor (using first 0.1 seconds)
        noise_frames = int(0.1 * sr / 512)
        noise_floor = np.mean(magnitude[:, :noise_frames], axis=1, keepdims=True)

        # Apply spectral gating
        threshold = noise_floor * 1.5
        mask = magnitude > threshold
        magnitude_clean = magnitude * mask

        # Reconstruct audio
        stft_clean = magnitude_clean * np.exp(1j * phase)
        audio_clean = librosa.istft(stft_clean, hop_length=512)

        return audio_clean

    def _enhance_eq(self, audio: np.ndarray, sr: int, quality: str) -> np.ndarray:
        """
        Apply EQ enhancement to improve voice clarity.

        Args:
            audio: Audio waveform
            sr: Sample rate
            quality: Quality preset

        Returns:
            EQ-enhanced audio
        """
        from scipy import signal

        # Design EQ filters for voice enhancement
        # Boost frequencies important for speech clarity (1-4 kHz)
        # High-pass filter to remove low-frequency noise
        sos_hp = signal.butter(4, 80, "hp", fs=sr, output="sos")
        audio = signal.sosfilt(sos_hp, audio)

        # Boost mid frequencies (1-4 kHz) for clarity
        if quality in ["medium", "high"]:
            # Parametric EQ boost at 2 kHz
            b, a = signal.iirpeak(2000, Q=2, fs=sr)
            audio = signal.filtfilt(b, a, audio * 0.3) + audio

        return audio

    def _apply_compression(self, audio: np.ndarray, sr: int, quality: str) -> np.ndarray:
        """
        Apply dynamic range compression.

        Args:
            audio: Audio waveform
            sr: Sample rate
            quality: Quality preset

        Returns:
            Compressed audio
        """
        # Simple peak compression
        threshold = 0.7
        ratio = 4.0 if quality == "high" else 2.0

        # Apply compression
        compressed = np.copy(audio)
        mask = np.abs(audio) > threshold
        compressed[mask] = (threshold + (np.abs(audio[mask]) - threshold) / ratio) * np.sign(
            audio[mask]
        )

        return compressed

    def _normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """
        Normalize audio to prevent clipping.

        Args:
            audio: Audio waveform

        Returns:
            Normalized audio
        """
        # Peak normalization
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = audio / max_val * 0.95  # Leave 5% headroom

        return audio

    def enhance_tts_output(
        self,
        tts_audio_path: Path,
        output_path: Optional[Path] = None,
        enable_enhancement: bool = True,
    ) -> Path:
        """
        Enhance TTS-generated audio as part of the synthesis pipeline.

        This method is designed to be called after TTS synthesis
        to improve the quality of the generated voice.

        Args:
            tts_audio_path: Path to TTS-generated audio
            output_path: Path to save enhanced audio (default: overwrite input)
            enable_enhancement: Whether to apply enhancement

        Returns:
            Path to enhanced audio file
        """
        if not enable_enhancement:
            logger.info("Voice enhancement disabled, returning original audio")
            return tts_audio_path

        if output_path is None:
            output_path = tts_audio_path

        logger.info(f"Enhancing TTS output: {tts_audio_path}")

        try:
            # Use automatic method selection
            return self.enhance_audio(
                audio_path=tts_audio_path,
                output_path=output_path,
                method="auto",
                quality="high",
            )
        except Exception as e:
            logger.error(f"TTS enhancement failed: {e}")
            # Return original audio if enhancement fails
            logger.warning("Returning original audio without enhancement")
            if output_path != tts_audio_path:
                import shutil

                shutil.copy2(tts_audio_path, output_path)
            return output_path

    def is_enhancement_available(self) -> bool:
        """
        Check if neural vocoder enhancement is available.

        Returns:
            True if HiFi-GAN is available, False otherwise
        """
        return self._hifigan_available


# Singleton instance
_enhancement_service: Optional[VoiceEnhancementService] = None


def get_voice_enhancement() -> VoiceEnhancementService:
    """Get or create voice enhancement service instance."""
    global _enhancement_service
    if _enhancement_service is None:
        _enhancement_service = VoiceEnhancementService()
    return _enhancement_service
