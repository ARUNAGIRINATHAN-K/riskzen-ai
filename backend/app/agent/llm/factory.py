"""LLM Provider Factory."""
from typing import Optional

from app.agent.llm.base import BaseLLMService
from app.agent.llm.mock import MockLLMProvider
from app.agent.llm.ollama import OllamaProvider
from app.agent.llm.openai import OpenAIProvider
from app.config import settings
from app.utils.logging import get_logger

logger = get_logger("riskzen.agent.llm.factory")


def get_llm_service(provider_override: Optional[str] = None) -> BaseLLMService:
    """Instantiate and return the configured LLM provider service."""
    provider = (provider_override or settings.LLM_PROVIDER or "ollama").lower()

    if provider == "openai":
        return OpenAIProvider(
            api_key=settings.OPENAI_API_KEY,
            model=settings.LLM_MODEL or "gpt-4o-mini",
        )
    elif provider == "ollama":
        return OllamaProvider(
            host=settings.OLLAMA_HOST,
            model=settings.LLM_MODEL or "llama3.1",
        )
    elif provider == "mock":
        return MockLLMProvider()
    else:
        logger.warn(f"Unknown LLM_PROVIDER '{provider}', falling back to MockLLMProvider")
        return MockLLMProvider()
