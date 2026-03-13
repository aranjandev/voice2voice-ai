"""Tests for audio playback module."""

from unittest.mock import patch

import numpy as np
import pytest


class TestPlayAudioBytes:
    """Tests for play_audio_bytes with mocked sounddevice."""

    @patch("voice_app.audio.playback.sd")
    def test_play_calls_sounddevice(self, mock_sd: object) -> None:
        """Should call sd.play with correct data."""
        from voice_app.audio.playback import play_audio_bytes

        # 1 second of silence as int16 bytes
        silence = np.zeros(24000, dtype=np.int16).tobytes()
        play_audio_bytes(silence, sample_rate=24000)

        mock_sd.play.assert_called_once()  # type: ignore[attr-defined]
        mock_sd.wait.assert_called_once()  # type: ignore[attr-defined]
