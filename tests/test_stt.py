"""Tests for speech-to-text module (local faster-whisper)."""

from unittest.mock import MagicMock, patch

import pytest


class TestTranscribe:
    """Tests for transcribe function with mocked whisper model."""

    @patch("voice_app.transcription.stt._get_model")
    @patch("voice_app.transcription.stt.PROJECT_ROOT")
    def test_returns_transcript(
        self, mock_root: MagicMock, mock_get_model: MagicMock, tmp_path: object
    ) -> None:
        """Should return joined segment text."""
        from pathlib import Path

        mock_root.__truediv__ = lambda self, x: Path(str(tmp_path)) / x

        mock_model = MagicMock()
        mock_get_model.return_value = mock_model

        seg1 = MagicMock()
        seg1.text = "Hello"
        seg2 = MagicMock()
        seg2.text = "world"
        mock_model.transcribe.return_value = ([seg1, seg2], MagicMock())

        from voice_app.transcription.stt import transcribe

        result = transcribe(b"fake-wav-bytes")
        assert result == "Hello world"

    @patch("voice_app.transcription.stt._get_model")
    @patch("voice_app.transcription.stt.PROJECT_ROOT")
    def test_transcription_error_raises_runtime_error(
        self, mock_root: MagicMock, mock_get_model: MagicMock, tmp_path: object
    ) -> None:
        """Should wrap errors in RuntimeError."""
        from pathlib import Path

        mock_root.__truediv__ = lambda self, x: Path(str(tmp_path)) / x

        mock_model = MagicMock()
        mock_get_model.return_value = mock_model
        mock_model.transcribe.side_effect = Exception("decode failed")

        from voice_app.transcription.stt import transcribe

        with pytest.raises(RuntimeError, match="Transcription failed"):
            transcribe(b"fake-wav-bytes")
