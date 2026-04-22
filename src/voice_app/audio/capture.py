"""Microphone audio capture using sounddevice."""

import io
import queue

import numpy as np
import sounddevice as sd

from voice_app.audio.vad import VAD_CHUNK_SAMPLES, SileroVAD
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


def record_until_silence(
    sample_rate: int = SAMPLE_RATE,
    channels: int = CHANNELS,
    vad: SileroVAD | None = None,
) -> np.ndarray | None:
    """Record audio from the microphone until end-of-utterance is detected.

    Streams audio in 512-sample chunks using sounddevice InputStream. Each
    chunk is fed into a Silero VAD instance that tracks speech and trailing
    silence. Recording stops once the VAD signals end-of-utterance.

    When nobody is speaking (pure silence or noise below VAD threshold) this
    function keeps listening indefinitely until speech is detected and then
    ends. Returns ``None`` only if an error prevents any audio from being
    collected.

    Args:
        sample_rate: Audio sample rate in Hz (must match the VAD model: 16000).
        channels: Number of input channels. Audio is summed to mono before
            VAD processing.
        vad: Optional pre-constructed :class:`SileroVAD` instance. A new one
            is created if not provided.

    Returns:
        NumPy float32 array of accumulated speech audio, or ``None`` if
        a hardware error occurred before any audio was collected.

    Raises:
        sd.PortAudioError: If no audio input device is available.
    """
    if vad is None:
        vad = SileroVAD(sample_rate=sample_rate)

    chunk_queue: queue.Queue[np.ndarray | Exception] = queue.Queue()

    def _callback(
        indata: np.ndarray,
        frames: int,
        time: object,  # CData — not typed strictly
        status: sd.CallbackFlags,
    ) -> None:
        if status:
            # Propagate non-fatal status flags as a warning via the queue
            # so the main thread sees them without crashing the callback.
            pass
        chunk_queue.put(indata.copy())

    print("🎙️  Listening... (speak now, recording stops after silence)")

    accumulated: list[np.ndarray] = []
    speech_started = False

    try:
        with sd.InputStream(
            samplerate=sample_rate,
            channels=channels,
            dtype="float32",
            blocksize=VAD_CHUNK_SAMPLES,
            callback=_callback,
        ):
            while True:
                chunk = chunk_queue.get()
                if isinstance(chunk, Exception):
                    raise chunk

                # Flatten to 1-D mono for VAD
                mono = chunk[:, 0] if chunk.ndim > 1 else chunk.ravel()

                is_speech, end_of_utt = vad.update(mono)

                if is_speech and not speech_started:
                    speech_started = True

                if speech_started:
                    accumulated.append(mono)

                if end_of_utt:
                    print("✅ End of utterance detected.")
                    break

    except sd.PortAudioError as e:
        raise sd.PortAudioError(
            f"No audio input device found. Check your microphone. Error: {e}"
        ) from e

    vad.reset()

    if not accumulated:
        return None

    return np.concatenate(accumulated, axis=0)
