# Voice-to-Voice AI App — Agent Instructions

## Project Scope & Sandboxing

**CRITICAL: All file and folder creation, modification, and deletion MUST occur
within `<project-root>/voice2voice-ai/`.
Never read, write, or execute files outside this directory tree.**

- Working directory: `voice2voice-ai/`
- All paths must be relative to the project root or absolute within it.
- Never install global packages. Use a local virtual environment at `.venv/` managed by `uv`.
- Never modify system audio settings or system-level configs.

## Tech Stack

| Layer          | Technology                        |
|----------------|-----------------------------------|
| Language       | Python 3.11+                      |
| Audio capture  | `sounddevice` + `numpy`           |
| STT            | OpenAI Whisper API (`openai`)     |
| LLM (optional) | OpenAI GPT-4o (`openai`)         |
| TTS            | OpenAI TTS API or ElevenLabs      |
| Audio playback | `sounddevice`                     |
| Config         | `python-dotenv`                   |
| Testing        | `pytest`                          |
| Packaging      | `pyproject.toml` (PEP 621) + `uv`|

## Architecture Rules

1. **Modular pipeline**: Each stage (capture → STT → processing → TTS → playback)
   is a separate module under `src/voice_app/`.
2. **No God objects**: Each module exposes a simple functional interface.
3. **Async where beneficial**: Use `asyncio` for I/O-bound API calls (STT, TTS).
4. **Config via environment**: All API keys and settings come from `.env`,
   loaded by `config.py`. Never hardcode secrets.
5. **Error handling**: Wrap all external API calls in try/except with meaningful
   error messages. Audio device errors should suggest troubleshooting steps.
6. **Type hints**: All functions must have type annotations.
7. **Docstrings**: All public functions must have Google-style docstrings.

## Dependency & Environment Management

- Use `uv` for all dependency and virtualenv management. Never use `pip install` or `python -m venv`.
- `uv.lock` is auto-generated — do not edit manually, but commit it to git.
- Add dependencies: `uv add <package>`
- Remove dependencies: `uv remove <package>`
- Run commands in venv: `uv run <command>`
- Sync environment: `uv sync --extra dev`

## File Operation Rules

- **Create files** only inside `src/`, `tests/`, `scripts/`, or project root.
- **Never delete** `.git/`, `.env`, or `pyproject.toml` without explicit confirmation.
- **Test before commit**: Run `uv run pytest` after any code change.
- Use `pathlib.Path` for all file operations in code; always resolve relative to
  `PROJECT_ROOT = Path(__file__).resolve().parents[2]`.

## MCP Server Integration

When MCP servers are available, use them for:
- **Filesystem MCP**: Scope to project root only. Reject any path outside it.
- **Fetch MCP**: For downloading API docs or checking endpoints.
- **GitHub MCP**: For creating issues, PRs, and branch management.

## Code Style

- Formatter: `ruff format`
- Linter: `ruff check`
- Line length: 88 characters
- Imports: sorted with `isort` (ruff handles this)

## Naming Conventions

- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`

## Testing

- Every module in `src/voice_app/` must have a corresponding test in `tests/`.
- Mock external API calls in tests (use `unittest.mock`).
- Audio device tests should be skippable when no device is available.
