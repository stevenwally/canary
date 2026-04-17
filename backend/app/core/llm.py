from langchain_openai import ChatOpenAI

from app.core.config import settings


def get_llm(
    model: str | None = None,
    temperature: float = 0.0,
) -> ChatOpenAI:
    """Return a ChatOpenAI instance configured for OpenRouter.

    OpenRouter exposes an OpenAI-compatible API, so we just set the
    base URL and API key on the standard ChatOpenAI class.

    Args:
        model: Override the default model from settings.
        temperature: LLM temperature (default 0.0 for deterministic output).
    """
    return ChatOpenAI(
        model=model or settings.OPENROUTER_MODEL,
        openai_api_key=settings.OPENROUTER_API_KEY,
        openai_api_base=settings.OPENROUTER_BASE_URL,
        temperature=temperature,
    )
