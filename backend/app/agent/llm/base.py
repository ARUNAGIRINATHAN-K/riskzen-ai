"""LLM Service Interface and Base Provider Abstraction."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseLLMService(ABC):
    """Abstract base class for LLM completion and embedding services."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        response_format: Optional[str] = None,
    ) -> str:
        """Generate text completion from LLM."""
        pass

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Generate vector embedding for the given text."""
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate vector embeddings for a batch of texts."""
        pass
