"""Command-line interaction helpers for voice-app."""


def select_voice(voices: list[str], default: str) -> str:
    """Display a numbered menu of TTS voices and prompt the user to pick one.

    Args:
        voices: Available voice names (should already be sorted).
        default: The voice to use when the user presses Enter without input.

    Returns:
        The selected voice name.
    """
    print("\n🎙️  Available TTS voices:\n")
    for idx, name in enumerate(voices, start=1):
        marker = "  ← default" if name == default else ""
        print(f"  {idx:>3}. {name}{marker}")

    print()
    raw = input(f"Pick a voice number [default: {default}]: ").strip()

    if not raw:
        print(f"Using default voice: {default}")
        return default

    try:
        choice = int(raw)
    except ValueError:
        print(f"Invalid input '{raw}'. Using default voice: {default}")
        return default

    if 1 <= choice <= len(voices):
        selected = voices[choice - 1]
        print(f"Selected voice: {selected}")
        return selected

    print(f"Number out of range. Using default voice: {default}")
    return default
