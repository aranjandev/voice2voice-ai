# Voice-to-Voice AI App

A fully local voice-to-voice AI assistant that listens through your microphone, transcribes speech, processes it through an LLM, and speaks the response back through your speakers. **No cloud APIs required** — everything runs on your machine.

**Pipeline:**  Mic → STT (faster-whisper) → LLM (Ollama) → TTS (macOS `say`) → Speaker

## Prerequisites

| Requirement | Version | Install |
|-------------|---------|---------|
| **Python** | 3.11+ | `brew install python@3.13` |
| **uv** | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **Ollama** | latest | https://ollama.com/download |
| **macOS** | 13+ | Required for `say` TTS and `sounddevice` mic access |

## Quick Start

```bash
# 1. Clone the repo
git clone <repo-url>
cd voice2voice-ai

# 2. Install dependencies
make setup
# or manually: uv venv && uv sync --extra dev

# 3. Download the Whisper model (see below)

# 4. Start Ollama and pull a model
ollama pull qwen2.5:latest

# 5. Configure environment
cp .env.example .env
# Edit .env — set STT_MODEL_PATH to your downloaded model directory

# 6. Run the app
make run
# or: uv run voice-app
```

## Downloading the Whisper Model

`faster-whisper` requires a **CTranslate2-converted** Whisper model. Do **not** download the original OpenAI models (they have `pytorch_model.bin` / `model.safetensors` — those won't work).

### Recommended: English-only medium model

1. Go to **https://huggingface.co/Systran/faster-whisper-medium.en/tree/main**
2. Download **all files** (especially `model.bin` ~1.5 GB)
3. Place them in `models/faster-whisper-medium.en/`

```
models/faster-whisper-medium.en/
├── config.json
├── model.bin              ← CTranslate2 model (~1.5 GB)
├── preprocessor_config.json
├── tokenizer.json
├── vocabulary.json
└── README.md              (optional)
```

4. Set in your `.env`:
   ```
   STT_MODEL_PATH=models/faster-whisper-medium.en/
   ```

### Other model options

| Model | Repo | Size | Speed | Quality |
|-------|------|------|-------|---------|
| tiny.en | [Systran/faster-whisper-tiny.en](https://huggingface.co/Systran/faster-whisper-tiny.en) | ~75 MB | Fastest | Lower |
| base.en | [Systran/faster-whisper-base.en](https://huggingface.co/Systran/faster-whisper-base.en) | ~150 MB | Fast | Good |
| small.en | [Systran/faster-whisper-small.en](https://huggingface.co/Systran/faster-whisper-small.en) | ~500 MB | Medium | Better |
| **medium.en** | [Systran/faster-whisper-medium.en](https://huggingface.co/Systran/faster-whisper-medium.en) | ~1.5 GB | Slower | **Recommended** |
| large-v3 | [Systran/faster-whisper-large-v3](https://huggingface.co/Systran/faster-whisper-large-v3) | ~3 GB | Slowest | Best (multilingual) |

> **Note:** Models ending in `.en` are English-only and perform better for English speech. The `large-v3` model supports multiple languages.

## Configuration

All settings are in `.env` (copy from `.env.example`):

```dotenv
# Ollama server (local LLM)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:latest

# STT — point to your downloaded model directory
STT_MODEL_PATH=models/faster-whisper-medium.en/
STT_MODEL_SIZE=medium          # fallback if STT_MODEL_PATH is empty

# TTS — macOS 'say' voice (run 'say -v ?' to list available voices)
TTS_VOICE=Alex
TTS_RATE=175

# Audio recording
SAMPLE_RATE=16000
CHANNELS=1
RECORD_SECONDS=5               # seconds per recording cycle
```

### Changing the LLM

You can use any model available in Ollama:

```bash
ollama pull llama3.2:latest     # then set OLLAMA_MODEL=llama3.2:latest
ollama pull mistral:latest      # or OLLAMA_MODEL=mistral:latest
```

### Changing the TTS voice

List available macOS voices:
```bash
say -v ?
```
Then set `TTS_VOICE` in `.env` (e.g., `Samantha`, `Daniel`, `Alex`).

## Project Structure

```
voice2voice-ai/
├── src/voice_app/
│   ├── main.py                 # Pipeline orchestrator (entry point)
│   ├── config.py               # Environment config + path safety
│   ├── audio/
│   │   ├── capture.py          # Mic recording via sounddevice
│   │   └── playback.py         # Speaker output via sounddevice
│   ├── transcription/
│   │   └── stt.py              # Speech-to-text (faster-whisper)
│   ├── processing/
│   │   └── llm.py              # LLM processing (Ollama via OpenAI API)
│   └── synthesis/
│       └── tts.py              # Text-to-speech (macOS 'say')
├── tests/                      # Unit tests (mocked externals)
├── models/                     # Local model files (gitignored)
├── scripts/setup_env.sh        # Bootstrap script
├── agents.md                   # AI agent instructions
├── .env.example                # Config template
├── pyproject.toml              # Dependencies & project metadata
└── Makefile                    # Common commands
```

## Development

```bash
# Run tests
make test

# Lint
make lint

# Format code
make format
```

All dependencies are managed via `uv` — never use `pip install` directly.

```bash
uv add <package>          # Add a dependency
uv remove <package>       # Remove a dependency
uv sync --extra dev       # Sync environment
uv run <command>          # Run in venv without activating
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `No audio input device found` | Check System Settings → Privacy → Microphone. Grant terminal access. |
| `Ollama connection refused` | Make sure Ollama is running: `ollama serve` |
| `model.bin not found` | You downloaded the wrong model. Use repos from `Systran/faster-whisper-*`, not `openai/whisper-*`. |
| `SSL certificate error` downloading models | Download model files manually from HuggingFace and set `STT_MODEL_PATH`. |
| `'say' command not found` | This TTS backend requires macOS. |

## License

MIT
