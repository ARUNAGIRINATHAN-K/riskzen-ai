"""Unit tests for LLM Providers and Factory."""
import pytest

from app.agent.llm import (
    BaseLLMService,
    MockLLMProvider,
    OllamaProvider,
    OpenAIProvider,
    get_llm_service,
)


@pytest.mark.asyncio
async def test_mock_llm_provider_generation_and_embeddings():
    """Test MockLLMProvider produces expected structured outputs and embeddings."""
    provider = MockLLMProvider()

    # Test investigation generation
    inv_resp = await provider.generate("Investigate risk preliminary reasoning")
    assert "initial_hypothesis" in inv_resp

    # Test analyze generation
    ana_resp = await provider.generate("Root-cause analysis contributing factors")
    assert "explanation" in ana_resp
    assert "contributing_factors" in ana_resp

    # Test recommend generation
    rec_resp = await provider.generate("Recommend mitigation actions")
    assert "recommendations" in rec_resp

    # Test review generation
    rev_resp = await provider.generate("Review quality check")
    assert "quality_check_passed" in rev_resp

    # Test embeddings
    emb = await provider.embed("Sample project text")
    assert len(emb) == 1536
    batch = await provider.embed_batch(["Text 1", "Text 2"])
    assert len(batch) == 2


def test_llm_factory():
    """Test get_llm_service factory creates correct providers."""
    mock_svc = get_llm_service(provider_override="mock")
    assert isinstance(mock_svc, MockLLMProvider)

    ollama_svc = get_llm_service(provider_override="ollama")
    assert isinstance(ollama_svc, OllamaProvider)

    openai_svc = get_llm_service(provider_override="openai")
    assert isinstance(openai_svc, OpenAIProvider)
