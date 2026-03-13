"""Microphone audio capture using sounddevice."""

import io

import numpy as np
import sounddevice as sd

from voice_app.config import CHANNELS, RECORD_SECONDS, SAMPLE_RATE


def record_audio(
    duration: int = RECORD_SECONDS,
    sample_rate: int = SAMPLE_RATE,
    channels: int = CHANNELS,
) -> np.ndarray:
    """Record audio from the default microphone.

    Args:
        duration: Recording duration in seconds.
        sample_rate: Sample rate in Hz.
        channels: Number of audio channels (1=mono, 2=stereo).

    Returns:
        NumPy array of recorded audio samples (float32).

    Raises:
        sd.PortAudioError: If no audio input device is available.
    """
    print(f"🎙️  Recording for {duration} seconds...")
    try:
        audio = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=channels,
            dtype="float32",
        )
        sd.wait()
        print("✅ Recording complete.")
        return audio
    except sd.PortAudioError as e:
        raise sd.PortAudioError(
            f"No audio input device found. Check your microphone. Error: {e}"
        ) from e


def audio_to_wav_bytes(
    audio: np.ndarray,
    sample_rate: int = SAMPLE_RATE,
) -> bytes:
    """Convert a NumPy audio array to WAV-format bytes.

    Args:
        audio: NumPy array of audio samples.
        sample_rate: Sample rate in Hz.

    Returns:
        WAV file content as bytes.
    """
    import wave

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        # Convert float32 [-1, 1] to int16
        int_audio = (audio * 32767).astype(np.int16)
        wf.writeframes(int_audio.tobytes())
    return buffer.getvalue()
