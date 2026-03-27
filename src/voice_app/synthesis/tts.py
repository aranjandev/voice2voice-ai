"""Text-to-speech using macOS built-in 'say' command."""

import re
import subprocess

from voice_app.config import TTS_RATE, TTS_VOICE

# Well-known macOS voices used as a fallback when `say -v ?` is unavailable
# (e.g. during development on Linux).
BUILTIN_VOICES: list[str] = [
    "Alex",
    "Daniel",
    "Fiona",
    "Karen",
    "Moira",
    "Samantha",
    "Tessa",
    "Veena",
    "Victoria",
]


def list_available_voices() -> list[str]:
    """Discover available macOS TTS voices via ``say -v ?``.

    Falls back to :data:`BUILTIN_VOICES` when:

    * ``say`` is not installed (Linux / other OS).
    * ``say -v ?`` fails (e.g. macOS 15+ changed the interface).
    * The command produces no parseable voice names.

    Returns:
        Sorted list of voice names.
    """
    try:
        result = subprocess.run(
            ["say", "-v", "?"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return list(BUILTIN_VOICES)

    voices: list[str] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        # Each line looks like: "Samantha  en_US  # Most people ..."
        # Voice name is everything before the first two-or-more spaces.
        match = re.match(r"^(\S+(?:\s\S+)*?)\s{2,}", line)
        if match:
            voices.append(match.group(1))
    return sorted(voices) if voices else list(BUILTIN_VOICES)


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
        raise RuntimeError("'say' command not found. This TTS backend requires macOS.")
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
