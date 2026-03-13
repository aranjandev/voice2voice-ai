#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

# Check uv is installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

echo "Creating virtual environment..."
uv venv

echo "Installing dependencies..."
uv sync --extra dev

echo ""
echo "✅ Setup complete!"
echo "Run 'uv run voice-app' or 'make run' to start the app."
echo "Run 'uv run pytest' or 'make test' to run tests."
