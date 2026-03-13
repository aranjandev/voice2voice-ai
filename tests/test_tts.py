"""Tests for text-to-speech module (macOS 'say' command)."""

from unittest.mock import MagicMock, patch

import pytest

from voice_app.synthesis.tts import synthesize


class TestSynthesize:
    """Tests for synthesize function with mocked subprocess."""

    @patch("voice_app.synthesis.tts.subprocess")
    def test_calls_say_command(self, mock_subprocess: MagicMock) -> None:
        """Should invoke macOS 'say' with correct args."""
        synthesize("Hello world", voice="Samantha", rate=175)
        mock_subprocess.run.assert_called_once_with(
            ["say", "-v", "Samantha", "-r", "175", "Hello world"],
            check=True,
        )

    @patch("voice_app.synthesis.tts.subprocess")
    def test_uses_specified_voice(self, mock_subprocess: MagicMock) -> None:
        """Should pass the voice parameter to say."""
        synthesize("test", voice="Daniel")
        args = mock_subprocess.run.call_args[0][0]
        assert args[2] == "Daniel"

    @patch("voice_app.synthesis.tts.subprocess")
    def test_say_not_found_raises(self, mock_subprocess: MagicMock) -> None:
        """Should raise RuntimeError when 'say' is not available."""
        mock_subprocess.run.side_effect = FileNotFoundError()
        with pytest.raises(RuntimeError, match="requires macOS"):
            synthesize("Hello")

    @patch("voice_app.synthesis.tts.subprocess")
    def test_say_failure_raises(self, mock_subprocess: MagicMock) -> None:
        """Should raise RuntimeError on say command failure."""
        import subprocess

        mock_subprocess.run.side_effect = subprocess.CalledProcessError(1, "say")
        mock_subprocess.CalledProcessError = subprocess.CalledProcessError
        with pytest.raises(RuntimeError, match="TTS synthesis failed"):
            synthesize("Hello")
