.PHONY: setup run test lint format clean

setup:
	uv venv
	uv sync --extra dev

run:
	uv run voice-app

test:
	uv run pytest

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

clean:
	rm -rf .venv dist build *.egg-info
