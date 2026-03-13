# Copilot Instructions

All code generation, file creation, and terminal commands MUST be scoped to the
project directory: `fully-ai-generated/`.

Never suggest commands that:
- Write to /tmp, ~, /usr, or any path outside the project
- Install packages globally (always use `.venv` via `uv`)
- Modify system-level audio or OS configurations

Use `uv` for all Python dependency management — never `pip` or `python -m venv`.
