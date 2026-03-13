"""LLM processing of transcripts via local Ollama server."""

from openai import OpenAI

from voice_app.config import OLLAMA_BASE_URL, OLLAMA_MODEL

DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful voice assistant. The user's speech has been transcribed "
    "and sent to you. Respond concisely and conversationally. Your response "
    "will be spoken aloud via text-to-speech."
)


def process_transcript(
    transcript: str,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    model: str = OLLAMA_MODEL,
) -> str:
    """Process a transcript through the local Ollama LLM.

    Uses Ollama's OpenAI-compatible API endpoint.

    Args:
        transcript: The user's transcribed speech.
        system_prompt: System prompt for the LLM.
        model: Ollama model name (e.g. 'qwen2.5:latest').

    Returns:
        The LLM's response text.

    Raises:
        RuntimeError: If the Ollama server is unreachable or the call fails.
    """
    client = OpenAI(
        base_url=f"{OLLAMA_BASE_URL}/v1",
        api_key="ollama",  # Ollama doesn't require a real key
    )

    try:
        print(f"🤖 Processing transcript with Ollama ({model})...")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": transcript},
            ],
        )
        result = response.choices[0].message.content or ""
        print(f"🤖 LLM response: {result}")
        return result
    except Exception as e:
        raise RuntimeError(
            f"LLM processing failed. Is Ollama running at {OLLAMA_BASE_URL}? "
            f"Error: {e}"
        ) from e
