# Project Instructions

<!-- CUSTOMIZE: Replace with a brief description of your project — what it does, who uses it, and its primary purpose. -->
## Overview

A fully local voice-to-voice AI assistant. The pipeline is: **Mic → STT (faster-whisper) → LLM (Ollama) → TTS (macOS `say`) → Speaker**. No cloud APIs are required — everything runs on the local machine. The app is written in Python 3.11+ and targets macOS 13+.

## Code Style

- Language: Python 3.11+
- Formatter: `ruff format` (line length 88)
- Linter: `ruff check` with rules E, F, I, N, W, UP
- Key conventions:
  - All functions must have type annotations
  - All public functions must have Google-style docstrings
  - File names: `snake_case.py` — Classes: `PascalCase` — Functions/variables: `snake_case` — Constants: `UPPER_SNAKE_CASE`
  - Use `pathlib.Path` for all file operations; resolve paths relative to `PROJECT_ROOT = Path(__file__).resolve().parents[2]`
  - All paths must be validated against `PROJECT_ROOT` using `config.safe_path()`

## Architecture

- Project type: Python CLI application (`voice-app` entry point → `voice_app.main:main`)
- Pipeline stages are separate modules; each exposes a simple functional interface
- Use `asyncio` for I/O-bound API calls (STT, LLM, TTS) where beneficial
- All API keys and tuneable settings come from `.env` via `config.py` — never hardcode secrets
- Key directories:
  - `src/voice_app/` — application source
    - `main.py` — pipeline orchestrator and main loop
    - `config.py` — environment config + path safety (`safe_path`)
    - `audio/capture.py` — mic recording via `sounddevice`
    - `audio/playback.py` — speaker output via `sounddevice`
    - `transcription/stt.py` — STT with local `faster-whisper` (cached model)
    - `processing/llm.py` — LLM via Ollama's OpenAI-compatible API
    - `synthesis/tts.py` — TTS via macOS `say` command
    - `cli.py` — interactive voice picker
  - `tests/` — unit tests with mocked external calls (one file per module)
  - `models/` — local CTranslate2 model files (gitignored, not bundled)
  - `scripts/` — `setup_env.sh` bootstrap, `git_ops.sh` git helpers

## Build and Test

```bash
# Install dependencies (including dev extras)
uv sync --extra dev

# Run tests
uv run pytest

# Run tests (verbose)
uv run pytest -v --tb=short

# Lint
uv run ruff check src/ tests/

# Format
uv run ruff format src/ tests/

# Run the app
uv run voice-app
```

## Conventions

- **Dependency management**: Use `uv` exclusively — never `pip install` or `python -m venv`
  - Add: `uv add <package>` | Remove: `uv remove <package>` | Sync: `uv sync --extra dev`
- **Testing**: Every module in `src/voice_app/` must have a corresponding test in `tests/`. Mock all external API calls (`openai`, `sounddevice`, subprocess). Audio device tests must be skippable when no device is available.
- **Error handling**: Wrap all external API calls in `try/except` with meaningful error messages. Audio device errors should suggest troubleshooting steps.
- **File creation**: Only inside `src/`, `tests/`, `scripts/`, or project root. Never delete `.git/`, `.env`, or `pyproject.toml` without explicit confirmation.
- **Path safety**: Always use `config.safe_path()` or validate that resolved paths start with `PROJECT_ROOT`.
- **Shell commands**: Never use heredocs or `python3 -c "..."` with double outer quotes. Always use `python3 -c '...'` with single outer quotes.

## Dependencies

Runtime:
- `openai>=1.0` — Ollama OpenAI-compatible client
- `sounddevice>=0.4` — mic capture and audio playback
- `numpy>=1.24` — audio array processing
- `python-dotenv>=1.0` — `.env` config loading
- `faster-whisper>=1.0` — local CTranslate2-based Whisper STT
- `huggingface-hub>=1.7.1` — model download fallback

Dev:
- `pytest>=7.0` — test runner
- `ruff>=0.4` — linter and formatter

External services / tools:
- **Ollama** — local LLM server (default model: `qwen2.5:latest`); must be running at `OLLAMA_BASE_URL`
- **macOS `say`** — TTS backend; required for synthesis
- **GitHub CLI (`gh`)** — must be authenticated via `gh auth login` for PR workflows

## Environment

- `OLLAMA_BASE_URL` — Ollama server URL (default: `http://localhost:11434`)
- `OLLAMA_MODEL` — Ollama model name (default: `qwen2.5:latest`)
- `STT_MODEL_PATH` — Path to a local CTranslate2-converted Whisper model directory; leave empty to auto-download
- `STT_MODEL_SIZE` — Fallback model size when `STT_MODEL_PATH` is empty (default: `base`)
- `TTS_VOICE` — macOS `say` voice name (default: `Samantha`; run `say -v ?` to list available voices)
- `TTS_RATE` — Speech rate in words per minute (default: `175`)
- `SAMPLE_RATE` — Audio sample rate in Hz (default: `16000`)
- `CHANNELS` — Number of audio channels (default: `1`)
- `RECORD_SECONDS` — Recording duration per pipeline cycle in seconds (default: `5`)
- GitHub CLI (`gh`) must be authenticated via `gh auth login`

---

## Shell Command Rules

> This section is managed by the jira2pr agent setup. Do not modify.

Applies whenever an agent runs shell commands in a terminal. Violations produce silent, hard-to-debug corruption:

- **Never write file content using heredocs** (`<< 'EOF' ... EOF`) — they get mangled in agent terminal sessions.
- **Never use `python3 -c "..."` with double outer quotes** — the shell expands `$variables` and backticks inside.
- **Always use `python3 -c '...'` with single outer quotes** and `\n` for newlines — this is the only reliable pattern:
  ```bash
  python3 -c 'open("/tmp/file.md","w").write("line1\nline2\n")'
  # With dynamic values, concatenate inside the expression
  python3 -c 'import datetime; ts=datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"); open("/tmp/file.md","w").write("# Title\nTimestamp: "+ts+"\n")'
  ```

---

## How Agents Contribute to Code

> This section is managed by the jira2pr agent setup. Do not remove or modify it — agents rely on it to understand available tools and workflows.

Agents in this project follow a structured, phase-driven workflow: they read a JIRA ticket, plan and implement the change, self-review, and submit a Pull Request. All agent behaviour is coordinated through the files under `.github/`.

### Agent Roster

Five agents are available. Each has a defined scope and model tier:

| Agent | Role | Model |
|-------|------|-------|
| **Orchestrator** | End-to-end workflow driver — reads the ticket, plans, implements, delegates, and submits the PR | Claude Sonnet 4 |
| **JIRA Reader** | Fetches a JIRA ticket and produces a structured requirements document | GPT-4o mini |
| **Researcher** | Lightweight research — evaluates packages, APIs, and algorithms | GPT-4o mini |
| **Reviewer** | Thorough code review — identifies risks, missing tests, and security issues | Claude Opus 4 |
| **PR Author** | Commits changes, pushes the branch, and finalises the draft PR | Claude Haiku 3.5 |

Agent definitions live in `.github/agents/`. Each file is a `.agent.md` with YAML frontmatter declaring its `description`, `tools`, `model`, and which subagents it may invoke.

### Skills

Skills are reusable, domain-specific instruction sets that agents load on demand. They live in `.github/skills/<skill-name>/SKILL.md`.

| Skill | Purpose |
|-------|---------|
| `read-jira-ticket` | Fetch and parse a JIRA ticket into structured requirements |
| `git-operations` | Create branches, stage commits with conventional messages, and push |
| `create-pull-request` | Open a draft PR with the canonical PR body template |
| `update-pull-request` | Update mutable blocks and append to append-only blocks in an existing PR |
| `summarize-changes` | Produce a human-readable summary of a git diff, grouped by component |
| `identify-risks` | Analyse changes for breaking changes, security issues, and missing tests |

### Agent Prompts

User-facing entry points are defined as `.prompt.md` files in `.github/prompts/`. Invoke them with a `/` slash command in the Copilot chat:

| Prompt | Slash command | What it does |
|--------|---------------|--------------|
| `feature.prompt.md` | `/feature` | Full feature workflow from JIRA ticket to PR, or resume from a PR link |
| `bugfix.prompt.md` | `/bugfix` | Bugfix workflow from JIRA ticket to PR, or resume |
| `review.prompt.md` | `/review` | Standalone code review of current changes |

### Workflows

Multi-phase workflow definitions live in `.github/agent-workflows/`. The Orchestrator reads the matching workflow file and executes it phase-by-phase:

| Workflow | Trigger | Phases |
|----------|---------|--------|
| `feature.md` | `/feature` | Bootstrap → Understand → Plan → Implement → Review → Submit |
| `bugfix.md` | `/bugfix` | Bootstrap → Understand → Diagnose → Fix → Review → Submit |
| `_resume.md` | Any PR link | Parses PR state and routes to the correct phase to continue |

All workflows include a **Phase 0: Bootstrap** that handles both fresh (JIRA input) and resume (PR link) modes automatically.

### Instructions

Persistent rules that apply across all agents are defined as `.instructions.md` files in `.github/instructions/`:

| File | Scope | What it governs |
|------|-------|-----------------|
| `commit-conventions.instructions.md` | All commits | [Conventional Commits](https://www.conventionalcommits.org/) format — type, scope, body, footers |
| `pr-schema.instructions.md` | PR bodies | Block definitions, mutability rules, idempotency, and ownership model |
| `pr-template.instructions.md` | PR bodies | Canonical PR body template that agents populate and update |

### Model Tiers

`.github/model-tiers.json` maps model tiers (0–3) to concrete Copilot model names. The `scripts/apply_model_tiers.py` script stamps the correct model into each agent file at setup time. Tier assignment reflects cost/capability trade-offs:

- **Tier 0** — Cheapest (GPT-4o mini): simple, deterministic tasks like reading tickets
- **Tier 1** — Lightweight (GPT-4o mini / Haiku): formulaic tasks like committing and pushing
- **Tier 2** — Capable (Claude Sonnet): complex reasoning and implementation
- **Tier 3** — Most powerful (Claude Opus): thorough review and risk analysis
