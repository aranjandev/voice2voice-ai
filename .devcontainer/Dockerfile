FROM mcr.microsoft.com/devcontainers/python:3.11

# System deps needed by sounddevice / PortAudio (no host audio device is
# exposed inside the container — these allow the package to install cleanly).
RUN apt-get update && apt-get install -y --no-install-recommends \
        libportaudio2 \
        libportaudiocpp0 \
        portaudio19-dev \
        ffmpeg \
        git \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for the vscode user (project-scoped; never global pip)
USER vscode
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/home/vscode/.local/bin:${PATH}"
USER root

# Set the working directory to the project root
WORKDIR /workspaces/voice2voice-ai
