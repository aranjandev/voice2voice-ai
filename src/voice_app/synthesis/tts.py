"""Text-to-speech using macOS built-in 'say' command."""

import subprocess

from voice_app.config import PROJECT_ROOT, TTS_RATE, TTS_VOICE


def synthesize(
    text: str,
    voice: str = TTS_VOICE,
    rate: int = TTS_RATE,
) -> None:
    """Speak text aloud using the macOS 'say' command.

    This plays audio directly through the speakers — no bytes returned.

    Args:
        text: The text to speak.
        voice: macOS voice name (e.g. 'Samantha', 'Alex', 'Daniel').
            Run 'say -v ?' in terminal to list available voices.
        rate: Speech rate in words per minute.

    Raises:
        RuntimeError: If the say command fails.
    """
    try:
        print(f"🗣️  Speaking (voice={voice}, rate={rate})...")
        subprocess.run(
            ["say", "-v", voice, "-r", str(rate), text],
            check=True,
        )
        print("✅ Speech complete.")
    except FileNotFoundError:
        raise RuntimeError(
            "'say' command not found. This TTS backend requires macOS."
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"TTS synthesis failed: {e}") from e


def synthesize_to_file(
    text: str,
    output_path: str = ".tmp/tts_output.aiff",
    voice: str = TTS_VOICE,
    rate: int = TTS_RATE,
) -> str:
    """Save synthesized speech to an audio file.

    Args:
        text: The text to speak.
        output_path: Relative path (within project) for the output file.
        voice: macOS voice name.
        rate: Speech rate in words per minute.

    Returns:
        Absolute path to the generated audio file.

    Raises:
        RuntimeError: If the say command fails.
    """
    from voice_app.config import safe_path

    out = safe_path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    try:
        subprocess.run(
            ["say", "-v", voice, "-r", str(rate), "-o", str(out), text],
            check=True,
        )
        return str(out)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"TTS file synthesis failed: {e}") from e
