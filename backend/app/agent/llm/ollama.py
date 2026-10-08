"""Ollama LLM Provider implementation for local inference."""
from typing import List, Optional
import httpx

from app.agent.llm.base import BaseLLMService
from app.config import settings
from app.utils.logging import get_logger

logger = get_logger("riskzen.agent.llm.ollama")


class OllamaProvider(BaseLLMService):
    """LLM Provider communicating with a local or containerized Ollama instance."""

    def __init__(
        self,
        host: Optional[str] = None,
        model: Optional[str] = None,
        embed_model: Optional[str] = None,
        timeout: float = 60.0,
    ):
        self.host = (host or settings.OLLAMA_HOST or "http://ollama:11434").rstrip("/")
        self.model = model or settings.LLM_MODEL or "llama3.1"
        self.embed_model = embed_model or "nomic-embed-text"
        self.timeout = timeout

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        response_format: Optional[str] = None,
    ) -> str:
        url = f"{self.host}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if system_prompt:
            payload["system"] = system_prompt
        if response_format == "json":
            payload["format"] = "json"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data.get("response", "").strip()
        except Exception as exc:
            logger.error("Ollama generate failed", host=self.host, model=self.model, error=str(exc))
            raise RuntimeError(f"Ollama generation failed: {str(exc)}") from exc

    async def embed(self, text: str) -> List[float]:
        url = f"{self.host}/api/embeddings"
        payload = {
            "model": self.embed_model,
            "prompt": text,
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data.get("embedding", [])
        except Exception as exc:
            logger.error("Ollama embedding failed", host=self.host, model=self.embed_model, error=str(exc))
            # Fallback dummy 1536-dim embedding if Ollama embed is not ready
            return [0.0] * 1536

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        results = []
        for text in texts:
            emb = await self.embed(text)
            results.append(emb)
        return results
