.PHONY: setup run test lint format clean

setup:
	uv venv
	uv sync --extra dev

VOICE ?=
run:
ifneq ($(VOICE),)
	TTS_VOICE=$(VOICE) uv run voice-app
else
	uv run voice-app
endif

test:
	uv run pytest

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

clean:
	rm -rf .venv dist build *.egg-info
