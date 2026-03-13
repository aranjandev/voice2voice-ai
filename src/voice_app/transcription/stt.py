"""Speech-to-text using local faster-whisper."""

import io
import tempfile
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel

from voice_app.config import PROJECT_ROOT, STT_MODEL_PATH, STT_MODEL_SIZE

# Cache the model instance to avoid reloading on each call
_model: WhisperModel | None = None


def _get_model(
    model_size: str = STT_MODEL_SIZE,
    model_path: str = STT_MODEL_PATH,
) -> WhisperModel:
    """Get or create the cached WhisperModel instance.

    If model_path is set, loads from that local directory.
    Otherwise falls back to downloading by model_size name.

    Args:
        model_size: Whisper model size ('tiny', 'base', 'small', 'medium', 'large-v3').
        model_path: Absolute or project-relative path to a local CTranslate2 model dir.

    Returns:
        A WhisperModel instance.
    """
    global _model
    if _model is None:
        model_id = model_path if model_path else model_size
        print(f"\U0001f4e6 Loading Whisper model from '{model_id}'...")
        _model = WhisperModel(model_id, device="cpu", compute_type="int8")
    return _model


def transcribe(
    audio_wav_bytes: bytes, model_size: str = STT_MODEL_SIZE
) -> str:
    """Transcribe audio bytes to text using local faster-whisper.

    Args:
        audio_wav_bytes: WAV-format audio content as bytes.
        model_size: Whisper model size.

    Returns:
        Transcribed text string.

    Raises:
        RuntimeError: If transcription fails.
    """
    model = _get_model(model_size)

    # Write WAV bytes to a temp file (faster-whisper reads files)
    tmp_dir = PROJECT_ROOT / ".tmp"
    tmp_dir.mkdir(exist_ok=True)
    tmp_path = tmp_dir / "stt_input.wav"
    tmp_path.write_bytes(audio_wav_bytes)

    try:
        print("📝 Transcribing audio locally...")
        segments, info = model.transcribe(str(tmp_path), beam_size=5)
        transcript = " ".join(segment.text.strip() for segment in segments)
        print(f"📝 Transcript: {transcript}")
        return transcript
    except Exception as e:
        raise RuntimeError(f"Transcription failed: {e}") from e
    finally:
        tmp_path.unlink(missing_ok=True)
