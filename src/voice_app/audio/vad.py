"""Voice Activity Detection using Silero VAD."""

import numpy as np
import torch
from silero_vad import load_silero_vad

from voice_app.config import (
    SAMPLE_RATE,
    VAD_MIN_SPEECH_DURATION_MS,
    VAD_SILENCE_THRESHOLD_MS,
    VAD_SPEECH_THRESHOLD,
)

# Silero VAD requires 512 samples per chunk at 16 kHz (32 ms per chunk)
VAD_CHUNK_SAMPLES: int = 512

# Silero VAD only supports these two sample rates
_SUPPORTED_SAMPLE_RATES: frozenset[int] = frozenset({8000, 16000})

# Module-level model cache — loaded once, reused across calls
_vad_model: torch.nn.Module | None = None


def _get_vad_model() -> torch.nn.Module:
    """Load and cache the Silero VAD model from the installed package.

    Uses the ``silero-vad`` PyPI package (no network call after install).

    Returns:
        Loaded Silero VAD torch model.
    """
    global _vad_model
    if _vad_model is None:
        print("📦 Loading Silero VAD model...")
        model = load_silero_vad()
        model.eval()
        _vad_model = model
    return _vad_model


class SileroVAD:
    """Silero VAD wrapper for speech activity detection.

    Wraps the Silero VAD model and exposes a simple per-chunk inference
    interface, along with helpers to decide end-of-utterance based on
    configurable silence duration and minimum speech duration thresholds.

    Args:
        sample_rate: Audio sample rate in Hz (must be 16000 or 8000).
        silence_threshold_ms: Duration of trailing silence in milliseconds
            required to declare end-of-utterance.
        min_speech_duration_ms: Minimum accumulated speech duration in
            milliseconds to consider an utterance valid (noise rejection).
        speech_threshold: Confidence score (0–1) above which a chunk is
            classified as speech. Default is ``VAD_SPEECH_THRESHOLD``.
    """

    def __init__(
        self,
        sample_rate: int = SAMPLE_RATE,
        silence_threshold_ms: int = VAD_SILENCE_THRESHOLD_MS,
        min_speech_duration_ms: int = VAD_MIN_SPEECH_DURATION_MS,
        speech_threshold: float = VAD_SPEECH_THRESHOLD,
    ) -> None:
        """Initialise SileroVAD with configuration thresholds."""
        if sample_rate not in _SUPPORTED_SAMPLE_RATES:
            raise ValueError(f"Silero VAD requires 8000 or 16000 Hz; got {sample_rate}")
        self._model = _get_vad_model()
        self._sample_rate = sample_rate
        self._speech_threshold = speech_threshold
        self._silence_samples = int(sample_rate * silence_threshold_ms / 1000)
        self._min_speech_samples = int(sample_rate * min_speech_duration_ms / 1000)
        self._reset_state()

    def _reset_state(self) -> None:
        """Reset per-utterance tracking state."""
        self._speech_samples_accumulated: int = 0
        self._silence_samples_accumulated: int = 0
        self._in_speech: bool = False

    def is_speech(self, chunk: np.ndarray) -> bool:
        """Run VAD on a single audio chunk.

        Args:
            chunk: 1-D float32 numpy array of exactly ``VAD_CHUNK_SAMPLES``
                samples in the range [-1, 1].

        Returns:
            True if the chunk contains speech, False otherwise.
        """
        tensor = torch.from_numpy(chunk.astype(np.float32))
        with torch.no_grad():
            confidence: float = self._model(tensor, self._sample_rate).item()
        return confidence >= self._speech_threshold

    def update(self, chunk: np.ndarray) -> tuple[bool, bool]:
        """Feed a chunk into the VAD state machine.

        Updates internal speech/silence counters and determines whether an
        utterance boundary has been reached.

        Args:
            chunk: 1-D float32 numpy array of ``VAD_CHUNK_SAMPLES`` samples.

        Returns:
            A tuple ``(is_speech, end_of_utterance)`` where:

            - ``is_speech`` — whether this chunk was classified as speech.
            - ``end_of_utterance`` — True when trailing silence exceeds
              ``silence_threshold_ms`` *and* accumulated speech exceeds
              ``min_speech_duration_ms``.
        """
        speech = self.is_speech(chunk)
        chunk_samples = len(chunk)

        if speech:
            self._in_speech = True
            self._speech_samples_accumulated += chunk_samples
            self._silence_samples_accumulated = 0
            return True, False

        # Non-speech chunk
        if self._in_speech:
            self._silence_samples_accumulated += chunk_samples
            has_enough_speech = (
                self._speech_samples_accumulated >= self._min_speech_samples
            )
            end_of_utterance = (
                has_enough_speech
                and self._silence_samples_accumulated >= self._silence_samples
            )
            return False, end_of_utterance

        return False, False

    def reset(self) -> None:
        """Reset state for the next utterance."""
        self._reset_state()
        # Also reset Silero's internal LSTM state to avoid bleed-over
        self._model.reset_states()
