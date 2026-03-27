"""Tests for text-to-speech module (macOS 'say' command)."""

from unittest.mock import MagicMock, patch

import pytest

from voice_app.synthesis.tts import list_available_voices, synthesize

# Sample output from `say -v ?` on macOS
_SAY_V_OUTPUT = (
    "Alex                en_US    # Most people recognize me by my voice.\n"
    "Daniel              en_GB    # Hello, my name is Daniel.\n"
    "Samantha            en_US    # Hello, my name is Samantha.\n"
    "Fiona               en-scotland # Hello, my name is Fiona.\n"
)


class TestListAvailableVoices:
    """Tests for list_available_voices function."""

    @patch("voice_app.synthesis.tts.subprocess")
    def test_returns_sorted_voice_names(self, mock_subprocess: MagicMock) -> None:
        """Should parse and return sorted voice names from say output."""
        mock_subprocess.run.return_value = MagicMock(stdout=_SAY_V_OUTPUT)
        voices = list_available_voices()
        assert voices == ["Alex", "Daniel", "Fiona", "Samantha"]

    @patch("voice_app.synthesis.tts.subprocess")
    def test_calls_say_with_question_flag(self, mock_subprocess: MagicMock) -> None:
        """Should invoke 'say -v ?' to discover voices."""
        mock_subprocess.run.return_value = MagicMock(stdout="")
        list_available_voices()
        mock_subprocess.run.assert_called_once_with(
            ["say", "-v", "?"],
            capture_output=True,
            text=True,
            check=True,
        )

    @patch("voice_app.synthesis.tts.subprocess.run")
    def test_say_not_found_returns_builtin_voices(self, mock_run: MagicMock) -> None:
        """Should return BUILTIN_VOICES when 'say' is not available."""
        from voice_app.synthesis.tts import BUILTIN_VOICES

        mock_run.side_effect = FileNotFoundError()
        voices = list_available_voices()
        assert voices == BUILTIN_VOICES

    @patch("voice_app.synthesis.tts.subprocess.run")
    def test_say_failure_returns_builtin_voices(self, mock_run: MagicMock) -> None:
        """Should return BUILTIN_VOICES when 'say -v ?' fails."""
        import subprocess

        from voice_app.synthesis.tts import BUILTIN_VOICES

        mock_run.side_effect = subprocess.CalledProcessError(1, "say")
        voices = list_available_voices()
        assert voices == BUILTIN_VOICES

    @patch("voice_app.synthesis.tts.subprocess")
    def test_empty_output_returns_builtin_voices(
        self, mock_subprocess: MagicMock
    ) -> None:
        """Should return BUILTIN_VOICES when say produces no parseable output."""
        from voice_app.synthesis.tts import BUILTIN_VOICES

        mock_subprocess.run.return_value = MagicMock(stdout="")
        assert list_available_voices() == BUILTIN_VOICES


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
