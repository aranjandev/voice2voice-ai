"""Tests for the Silero VAD wrapper module."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

# Silence chunk — all zeros
CHUNK_SILENT = np.zeros(512, dtype=np.float32)
# Speech-like chunk — non-zero values
CHUNK_SPEECH = np.ones(512, dtype=np.float32) * 0.5


def _make_mock_model(confidence: float) -> MagicMock:
    """Return a fake Silero VAD torch model that always returns ``confidence``."""
    mock_output = MagicMock()
    mock_output.item.return_value = confidence
    mock_model = MagicMock()
    mock_model.return_value = mock_output
    mock_model.reset_states = MagicMock()
    return mock_model


@pytest.fixture()
def patched_vad_model():
    """Fixture that patches _get_vad_model to avoid loading the real model."""
    with patch("voice_app.audio.vad._get_vad_model") as mock_get:
        yield mock_get


class TestSileroVADIsSpeech:
    """Tests for SileroVAD.is_speech()."""

    def test_returns_true_when_confidence_high(
        self, patched_vad_model: MagicMock
    ) -> None:
        """is_speech should return True when model confidence >= 0.5."""
        patched_vad_model.return_value = _make_mock_model(confidence=0.9)
        from voice_app.audio.vad import SileroVAD

        vad = SileroVAD()
        assert vad.is_speech(CHUNK_SPEECH) is True

    def test_returns_false_when_confidence_low(
        self, patched_vad_model: MagicMock
    ) -> None:
        """is_speech should return False when model confidence < 0.5."""
        patched_vad_model.return_value = _make_mock_model(confidence=0.1)
        from voice_app.audio.vad import SileroVAD

        vad = SileroVAD()
        assert vad.is_speech(CHUNK_SILENT) is False

    def test_boundary_confidence_is_speech(self, patched_vad_model: MagicMock) -> None:
        """Confidence of exactly 0.5 should be treated as speech."""
        patched_vad_model.return_value = _make_mock_model(confidence=0.5)
        from voice_app.audio.vad import SileroVAD

        vad = SileroVAD()
        assert vad.is_speech(CHUNK_SPEECH) is True


class TestSileroVADUpdate:
    """Tests for SileroVAD.update() state machine."""

    def test_speech_chunk_does_not_trigger_eou(
        self, patched_vad_model: MagicMock
    ) -> None:
        """A speech chunk alone should never trigger end-of-utterance."""
        patched_vad_model.return_value = _make_mock_model(confidence=0.9)
        from voice_app.audio.vad import SileroVAD

        vad = SileroVAD(silence_threshold_ms=100, min_speech_duration_ms=0)
        is_speech, end_of_utt = vad.update(CHUNK_SPEECH)
        assert is_speech is True
        assert end_of_utt is False

    def test_silence_before_speech_does_not_trigger_eou(
        self, patched_vad_model: MagicMock
    ) -> None:
        """Silence chunks before any speech should never trigger end-of-utterance."""
        patched_vad_model.return_value = _make_mock_model(confidence=0.0)
        from voice_app.audio.vad import SileroVAD

        vad = SileroVAD(silence_threshold_ms=10, min_speech_duration_ms=0)
        for _ in range(50):
            _, eou = vad.update(CHUNK_SILENT)
            assert eou is False

    def test_silence_after_speech_triggers_eou(
        self, patched_vad_model: MagicMock
    ) -> None:
        """Sufficient silence following speech should trigger end-of-utterance."""
        mock_model = _make_mock_model(confidence=0.9)
        patched_vad_model.return_value = mock_model
        from voice_app.audio.vad import SileroVAD

        # 16000 Hz, 512 samples = 32ms per chunk
        # silence_threshold_ms=64 → need 2 silence chunks (2 * 512 = 1024 samples)
        # min_speech_duration_ms=32 → need 1 speech chunk (512 samples)
        vad = SileroVAD(
            sample_rate=16000,
            silence_threshold_ms=64,
            min_speech_duration_ms=32,
        )

        # Feed enough speech to satisfy min_speech_duration
        vad.update(CHUNK_SPEECH)

        # Switch model to return silence
        mock_model.return_value.item.return_value = 0.0

        # First silence chunk — not yet enough
        _, eou1 = vad.update(CHUNK_SILENT)
        assert eou1 is False

        # Second silence chunk — now at 2 * 32ms = 64ms ≥ threshold
        _, eou2 = vad.update(CHUNK_SILENT)
        assert eou2 is True

    def test_short_speech_does_not_trigger_eou(
        self, patched_vad_model: MagicMock
    ) -> None:
        """Speech shorter than min_speech_duration_ms should not trigger eou."""
        mock_model = _make_mock_model(confidence=0.9)
        patched_vad_model.return_value = mock_model
        from voice_app.audio.vad import SileroVAD

        # min_speech_duration_ms=200 → need 200ms of speech at 16kHz = 3200 samples
        # One 512-sample chunk = 32ms < 200ms — not enough
        vad = SileroVAD(
            sample_rate=16000,
            silence_threshold_ms=64,
            min_speech_duration_ms=200,
        )
        vad.update(CHUNK_SPEECH)  # Only 32ms of speech

        # Now go silent
        mock_model.return_value.item.return_value = 0.0
        for _ in range(10):
            _, eou = vad.update(CHUNK_SILENT)
            assert eou is False

    def test_reset_clears_state(self, patched_vad_model: MagicMock) -> None:
        """After reset(), state is cleared and eou should not fire immediately."""
        mock_model = _make_mock_model(confidence=0.9)
        patched_vad_model.return_value = mock_model
        from voice_app.audio.vad import SileroVAD

        vad = SileroVAD(
            sample_rate=16000,
            silence_threshold_ms=32,
            min_speech_duration_ms=32,
        )
        vad.update(CHUNK_SPEECH)
        vad.reset()

        # After reset, silence should not trigger eou (no speech yet)
        mock_model.return_value.item.return_value = 0.0
        for _ in range(5):
            _, eou = vad.update(CHUNK_SILENT)
            assert eou is False

        mock_model.reset_states.assert_called()


class TestVADModelCaching:
    """Tests verifying the module-level model cache behaviour."""

    def test_model_loaded_only_once(self) -> None:
        """torch.hub.load is called once; subsequent SileroVAD reuses cache."""
        from voice_app.audio import vad as vad_module

        # Clear the module-level cache to force a fresh load in this test
        original = vad_module._vad_model
        vad_module._vad_model = None

        mock_model = _make_mock_model(confidence=0.5)
        mock_model.eval = MagicMock()

        try:
            with patch(
                "torch.hub.load", return_value=(mock_model, None)
            ) as mock_hub_load:
                from voice_app.audio.vad import SileroVAD

                SileroVAD()
                SileroVAD()
                # Second SileroVAD hits the module-level cache; hub.load called once
                mock_hub_load.assert_called_once()
        finally:
            vad_module._vad_model = original
