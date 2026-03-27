"""Main entry point — voice-to-voice pipeline orchestrator."""

import sys

from voice_app.audio.capture import audio_to_wav_bytes, record_audio
from voice_app.config import TTS_VOICE, is_voice_configured
from voice_app.processing.llm import process_transcript
from voice_app.synthesis.tts import list_available_voices, synthesize
from voice_app.transcription.stt import transcribe


def run_pipeline(use_llm: bool = True, voice: str | None = None) -> None:
    """Run one cycle of the voice-to-voice pipeline.

    Args:
        use_llm: If True, pass transcript through LLM before TTS.
                 If False, directly synthesize the transcript back as speech.
        voice: TTS voice name. Uses config default when *None*.
    """
    # 1. Capture audio from microphone
    audio = record_audio()

    # 2. Convert to WAV bytes for the STT model
    wav_bytes = audio_to_wav_bytes(audio)

    # 3. Transcribe speech to text (local faster-whisper)
    transcript = transcribe(wav_bytes)

    if not transcript.strip():
        print("⚠️  No speech detected. Try again.")
        return

    # 4. Optionally process through Ollama LLM
    if use_llm:
        text_to_speak = process_transcript(transcript)
    else:
        text_to_speak = transcript

    # 5. Speak through macOS 'say' (plays directly through speakers)
    if voice:
        synthesize(text_to_speak, voice=voice)
    else:
        synthesize(text_to_speak)


def _pick_voice() -> str:
    """Determine TTS voice — skip prompt when already configured."""
    if is_voice_configured():
        print(f"Using configured voice: {TTS_VOICE}")
        return TTS_VOICE

    try:
        from voice_app.cli import select_voice

        voices = list_available_voices()
        return select_voice(voices, default=TTS_VOICE)
    except RuntimeError as exc:
        print(f"⚠️  Could not list voices ({exc}). Using default: {TTS_VOICE}")
        return TTS_VOICE


def main() -> None:
    """Main loop — continuously listens, processes, and speaks."""
    print("=" * 50)
    print("🎤 Voice-to-Voice AI App")
    print("Press Ctrl+C to quit.")
    print("=" * 50)

    voice = _pick_voice()

    try:
        while True:
            run_pipeline(use_llm=True, voice=voice)
            print("\n--- Ready for next input ---\n")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
