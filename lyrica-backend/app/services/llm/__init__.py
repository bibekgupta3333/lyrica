"""
LLM Services Module
Provides flexible, provider-agnostic LLM integration.
"""

from app.services.llm.base import BaseLLMService, LLMConfig, LLMMessage, LLMProvider, LLMResponse
from app.services.llm.factory import LLMFactory

__all__ = [
    "BaseLLMService",
    "LLMConfig",
    "LLMMessage",
    "LLMProvider",
    "LLMResponse",
    "LLMFactory",
    "get_llm_service",
]


def get_llm_service(provider: str = None) -> BaseLLMService:
    """
    Get LLM service instance (convenience function).

    Args:
        provider: Optional provider name (ollama, openai, gemini, grok)

    Returns:
        LLM service instance

    Examples:
        >>> llm = get_llm_service()  # Uses default from settings
        >>> llm = get_llm_service("openai")  # Uses OpenAI
        >>> llm = get_llm_service("gemini")  # Uses Gemini
    """
    return LLMFactory.create_from_env(provider)
