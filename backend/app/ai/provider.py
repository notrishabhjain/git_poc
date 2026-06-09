"""Multi-provider LLM client with automatic failover: Groq → NVIDIA Build → Cerebras."""
import logging
from enum import Enum

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)


class Provider(str, Enum):
    GROQ = "groq"
    NVIDIA = "nvidia"
    CEREBRAS = "cerebras"


_PROVIDER_CONFIG = {
    Provider.GROQ: {
        "base_url": "https://api.groq.com/openai/v1",
        "api_key_attr": "groq_api_key",
        "default_model": "llama-3.1-8b-instant",
    },
    Provider.NVIDIA: {
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key_attr": "nvidia_api_key",
        "default_model": "meta/llama-3.3-70b-instruct",
    },
    Provider.CEREBRAS: {
        "base_url": "https://api.cerebras.ai/v1",
        "api_key_attr": "cerebras_api_key",
        "default_model": "llama3.1-8b",
    },
}


def get_client(provider: Provider) -> AsyncOpenAI:
    cfg = _PROVIDER_CONFIG[provider]
    api_key = getattr(settings, cfg["api_key_attr"])
    return AsyncOpenAI(base_url=cfg["base_url"], api_key=api_key)


async def chat_with_fallback(
    messages: list[dict],
    tools: list[dict] | None = None,
    tool_choice: str | None = None,
    model_override: str | None = None,
    prefer_provider: Provider = Provider.GROQ,
    temperature: float = 0.1,
) -> tuple[Provider, object]:
    """Try providers in order, returning (provider, response) on first success."""
    providers = [prefer_provider] + [p for p in Provider if p != prefer_provider]

    for provider in providers:
        cfg = _PROVIDER_CONFIG[provider]
        api_key = getattr(settings, cfg["api_key_attr"])
        if not api_key:
            continue

        model = model_override or cfg["default_model"]
        client = get_client(provider)
        try:
            kwargs: dict = dict(model=model, messages=messages, temperature=temperature)
            if tools:
                kwargs["tools"] = tools
            if tool_choice:
                kwargs["tool_choice"] = tool_choice
            response = await client.chat.completions.create(**kwargs)
            return provider, response
        except Exception as e:
            logger.warning(f"Provider {provider} failed: {e}")

    raise RuntimeError("All LLM providers failed. Check your API keys.")
