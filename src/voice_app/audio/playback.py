"""Audio playback through speakers using sounddevice."""

import io

import numpy as np
import sounddevice as sd


def play_audio_bytes(
    audio_bytes: bytes,
    sample_rate: int = 24000,
) -> None:
    """Play raw audio bytes through the default output device.

    Expects PCM audio. For MP3/OGG from TTS APIs, use play_file_bytes instead.

    Args:
        audio_bytes: Raw PCM audio bytes (int16).
        sample_rate: Sample rate in Hz (OpenAI TTS outputs 24kHz).
    """
    audio = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32767
    print("🔊 Playing audio...")
    sd.play(audio, samplerate=sample_rate)
    sd.wait()
    print("✅ Playback complete.")


def play_file_bytes(
    file_bytes: bytes,
    fmt: str = "mp3",
) -> None:
    """Play audio from file bytes (MP3, WAV, etc.) through speakers.

    Args:
        file_bytes: Audio file content as bytes.
        fmt: Audio format ('mp3', 'wav', 'opus', 'flac').
    """
    import wave

    if fmt == "wav":
        buffer = io.BytesIO(file_bytes)
        with wave.open(buffer, "rb") as wf:
            sample_rate = wf.getframerate()
            raw = wf.readframes(wf.getnframes())
            audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32767
        sd.play(audio, samplerate=sample_rate)
        sd.wait()
    else:
        # For MP3 and other compressed formats, write to temp file and use
        # a decoder. We avoid global deps by requiring this only when needed.
        try:
            import subprocess
            import tempfile
            from pathlib import Path

            from voice_app.config import PROJECT_ROOT

            tmp_dir = PROJECT_ROOT / ".tmp"
            tmp_dir.mkdir(exist_ok=True)
            tmp_path = tmp_dir / f"tts_output.{fmt}"
            tmp_path.write_bytes(file_bytes)

            # Use ffmpeg/afplay (macOS) to play
            subprocess.run(["afplay", str(tmp_path)], check=True)
            tmp_path.unlink(missing_ok=True)
        except FileNotFoundError:
            print("⚠️  Could not play audio. Install ffmpeg or use WAV format.")
