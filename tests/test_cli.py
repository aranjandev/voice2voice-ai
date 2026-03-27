"""Tests for CLI voice-selection helper."""

from unittest.mock import patch

from voice_app.cli import select_voice

_VOICES = ["Alex", "Daniel", "Fiona", "Samantha"]


class TestSelectVoice:
    """Tests for select_voice interactive menu."""

    @patch("builtins.input", return_value="2")
    def test_valid_selection(self, _mock_input) -> None:  # noqa: ANN001
        """Should return the voice at the chosen index."""
        assert select_voice(_VOICES, default="Samantha") == "Daniel"

    @patch("builtins.input", return_value="")
    def test_empty_input_returns_default(self, _mock_input) -> None:  # noqa: ANN001
        """Should return the default voice when user presses Enter."""
        assert select_voice(_VOICES, default="Samantha") == "Samantha"

    @patch("builtins.input", return_value="abc")
    def test_non_numeric_input_returns_default(self, _mock_input) -> None:  # noqa: ANN001
        """Should return default for non-numeric input."""
        assert select_voice(_VOICES, default="Samantha") == "Samantha"

    @patch("builtins.input", return_value="99")
    def test_out_of_range_returns_default(self, _mock_input) -> None:  # noqa: ANN001
        """Should return default when number is out of range."""
        assert select_voice(_VOICES, default="Samantha") == "Samantha"

    @patch("builtins.input", return_value="0")
    def test_zero_returns_default(self, _mock_input) -> None:  # noqa: ANN001
        """Should return default for zero (1-indexed menu)."""
        assert select_voice(_VOICES, default="Samantha") == "Samantha"

    @patch("builtins.input", return_value="1")
    def test_first_voice_selection(self, _mock_input) -> None:  # noqa: ANN001
        """Should return the first voice when '1' is entered."""
        assert select_voice(_VOICES, default="Samantha") == "Alex"

    @patch("builtins.input", return_value="4")
    def test_last_voice_selection(self, _mock_input) -> None:  # noqa: ANN001
        """Should return the last voice when max index is entered."""
        assert select_voice(_VOICES, default="Samantha") == "Samantha"
