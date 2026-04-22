"""Tests for audio capture module."""

from unittest.mock import MagicMock, patch

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


# ---------------------------------------------------------------------------
# Helpers for record_until_silence tests
# ---------------------------------------------------------------------------

CHUNK_SIZE = 512
SILENT_CHUNK = np.zeros(CHUNK_SIZE, dtype=np.float32)
SPEECH_CHUNK = np.ones(CHUNK_SIZE, dtype=np.float32) * 0.5


def _make_vad_stub(responses: list[tuple[bool, bool]]) -> MagicMock:
    """Build a mock SileroVAD whose update() returns preset (is_speech, eou) pairs."""
    vad = MagicMock()
    vad.update.side_effect = responses
    vad.reset = MagicMock()
    return vad


def _make_stream_side_effect(chunks: list[np.ndarray]) -> callable:
    """Return a context-manager factory that feeds ``chunks`` into the callback."""

    class _FakeStream:
        def __init__(self, **kwargs: object) -> None:
            self._callback = kwargs["callback"]

        def __enter__(self) -> "_FakeStream":
            for chunk in chunks:
                # sounddevice passes (frames, channels) shaped arrays
                indata = chunk.reshape(-1, 1)
                self._callback(indata, len(chunk), None, None)
            return self

        def __exit__(self, *args: object) -> None:
            pass

    return _FakeStream


class TestRecordUntilSilence:
    """Tests for record_until_silence() using mocked VAD and sounddevice."""

    def test_returns_audio_on_end_of_utterance(self) -> None:
        """Should return accumulated audio when VAD signals end-of-utterance."""
        vad = _make_vad_stub(
            [
                (True, False),  # chunk 1: speech
                (True, False),  # chunk 2: speech
                (False, True),  # chunk 3: silence → end-of-utterance
            ]
        )
        chunks = [SPEECH_CHUNK, SPEECH_CHUNK, SILENT_CHUNK]

        with patch(
            "voice_app.audio.capture.sd.InputStream",
            side_effect=_make_stream_side_effect(chunks),
        ):
            from voice_app.audio.capture import record_until_silence

            result = record_until_silence(vad=vad)

        assert result is not None
        assert isinstance(result, np.ndarray)
        assert result.dtype == np.float32
        # Speech chunks + silence chunk accumulated after speech started
        assert result.shape[0] == CHUNK_SIZE * 3

    def test_pure_silence_never_returns(self) -> None:
        """Pure silence (VAD never signals speech or EOU) should not return audio.

        We simulate an InputStream that delivers 5 silent chunks —
        none trigger EOU — then we verify the loop keeps running.
        This test uses a KeyboardInterrupt to break out since no EOU fires.
        """
        from voice_app.audio.capture import record_until_silence

        # VAD never fires EOU when no speech has occurred
        vad = _make_vad_stub([(False, False)] * 5)

        call_count = 0

        class _SilenceForeverStream:
            def __init__(self, **kwargs: object) -> None:
                self._callback = kwargs["callback"]

            def __enter__(self) -> "_SilenceForeverStream":
                nonlocal call_count
                # Feed 5 silent chunks then raise to break the infinite listen
                for _ in range(5):
                    self._callback(SILENT_CHUNK.reshape(-1, 1), CHUNK_SIZE, None, None)
                    call_count += 1
                raise KeyboardInterrupt

            def __exit__(self, *args: object) -> None:
                pass

        with patch("voice_app.audio.capture.sd.InputStream", _SilenceForeverStream):
            with pytest.raises(KeyboardInterrupt):
                record_until_silence(vad=vad)

        assert call_count == 5

    def test_returns_none_if_no_audio_accumulated(self) -> None:
        """Should return None when EOU fires before any audio is accumulated."""
        # EOU fires immediately (before speech_started becomes True)
        vad = MagicMock()
        vad.update.return_value = (False, True)  # end-of-utterance with no speech
        vad.reset = MagicMock()

        chunks = [SILENT_CHUNK]

        with patch(
            "voice_app.audio.capture.sd.InputStream",
            side_effect=_make_stream_side_effect(chunks),
        ):
            from voice_app.audio.capture import record_until_silence

            result = record_until_silence(vad=vad)

        assert result is None

    def test_vad_reset_called_after_utterance(self) -> None:
        """VAD reset() must be called after each utterance."""
        vad = _make_vad_stub(
            [
                (True, False),
                (False, True),
            ]
        )
        chunks = [SPEECH_CHUNK, SILENT_CHUNK]

        with patch(
            "voice_app.audio.capture.sd.InputStream",
            side_effect=_make_stream_side_effect(chunks),
        ):
            from voice_app.audio.capture import record_until_silence

            record_until_silence(vad=vad)

        vad.reset.assert_called_once()
