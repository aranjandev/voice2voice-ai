"""Tests for audio capture module."""

import numpy as np
import pytest

from voice_app.audio.capture import audio_to_wav_bytes


class TestAudioToWavBytes:
    """Tests for audio_to_wav_bytes conversion."""

    def test_returns_bytes(self) -> None:
        """WAV conversion should return bytes."""
        audio = np.zeros((16000,), dtype=np.float32)
        result = audio_to_wav_bytes(audio.reshape(-1, 1))
        assert isinstance(result, bytes)

    def test_wav_header(self) -> None:
        """Output should start with RIFF WAV header."""
        audio = np.zeros((16000,), dtype=np.float32).reshape(-1, 1)
        result = audio_to_wav_bytes(audio)
        assert result[:4] == b"RIFF"
        assert result[8:12] == b"WAVE"

    def test_empty_audio(self) -> None:
        """Empty audio should still produce valid WAV bytes."""
        audio = np.zeros((0,), dtype=np.float32).reshape(-1, 1)
        result = audio_to_wav_bytes(audio)
        assert result[:4] == b"RIFF"


@pytest.mark.skipif(
    True,  # Replace with actual device check if needed
    reason="Skipping mic test — requires audio input device",
)
class TestRecordAudio:
    """Tests for record_audio (requires hardware)."""

    def test_record_returns_array(self) -> None:
        from voice_app.audio.capture import record_audio

        audio = record_audio(duration=1)
        assert isinstance(audio, np.ndarray)
        assert audio.shape[0] > 0
