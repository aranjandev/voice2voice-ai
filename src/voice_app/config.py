"""Centralized configuration loaded from environment variables."""

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")


def safe_path(relative: str) -> Path:
    """Resolve a path and ensure it's within PROJECT_ROOT.

    Args:
        relative: A path relative to the project root.

    Returns:
        The resolved absolute path.

    Raises:
        ValueError: If the resolved path escapes the project root.
    """
    resolved = (PROJECT_ROOT / relative).resolve()
    if not str(resolved).startswith(str(PROJECT_ROOT)):
        raise ValueError(f"Path escapes project root: {resolved}")
    return resolved


# --- Ollama Settings ---
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:latest")

# --- Audio Settings ---
SAMPLE_RATE: int = int(os.getenv("SAMPLE_RATE", "16000"))
CHANNELS: int = int(os.getenv("CHANNELS", "1"))
RECORD_SECONDS: int = int(os.getenv("RECORD_SECONDS", "5"))

# --- STT Settings (local faster-whisper) ---
STT_MODEL_SIZE: str = os.getenv("STT_MODEL_SIZE", "base")
# Set STT_MODEL_PATH to a local directory containing the CTranslate2 model files
# to skip downloading from HuggingFace. Leave empty to auto-download.
STT_MODEL_PATH: str = os.getenv("STT_MODEL_PATH", "")

# --- TTS Settings (macOS 'say' command) ---
TTS_VOICE: str = os.getenv("TTS_VOICE", "Samantha")
TTS_RATE: int = int(os.getenv("TTS_RATE", "175"))
