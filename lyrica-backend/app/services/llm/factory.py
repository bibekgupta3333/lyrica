"""
LLM Service Factory
Creates appropriate LLM service based on provider.
"""

from typing import Optional

from loguru import logger

from app.services.llm.base import BaseLLMService, LLMConfig, LLMProvider


class LLMFactory:
    """Factory for creating LLM service instances."""

    @staticmethod
    def create(config: LLMConfig) -> BaseLLMService:
        """
        Create LLM service based on provider.

        Args:
            config: LLM configuration

        Returns:
            Appropriate LLM service instance

        Raises:
            ValueError: If provider is not supported
        """
        logger.info(f"Creating LLM service: {config.provider} ({config.model_name})")

        if config.provider == LLMProvider.OLLAMA:
            from app.services.llm.ollama_service import OllamaService

            return OllamaService(config)

        elif config.provider == LLMProvider.OPENAI:
            from app.services.llm.openai_service import OpenAIService

            return OpenAIService(config)

        elif config.provider == LLMProvider.GEMINI:
            from app.services.llm.gemini_service import GeminiService

            return GeminiService(config)

        elif config.provider == LLMProvider.GROK:
            # Grok uses OpenAI-compatible API
            from app.services.llm.openai_service import OpenAIService

            config.base_url = config.base_url or "https://api.x.ai/v1"
            return OpenAIService(config)

        elif config.provider == LLMProvider.ANTHROPIC:
            # Placeholder for Anthropic Claude
            logger.warning("Anthropic provider not yet implemented, falling back to Ollama")
            from app.services.llm.ollama_service import OllamaService

            return OllamaService(config)

        elif config.provider == LLMProvider.COHERE:
            # Placeholder for Cohere
            logger.warning("Cohere provider not yet implemented, falling back to Ollama")
            from app.services.llm.ollama_service import OllamaService

            return OllamaService(config)

        else:
            raise ValueError(f"Unsupported LLM provider: {config.provider}")

    @staticmethod
    def create_from_env(provider: Optional[str] = None) -> BaseLLMService:
        """
        Create LLM service from environment variables.

        Args:
            provider: Optional provider override

        Returns:
            LLM service instance
        """
        from app.core.config import settings

        # Determine provider
        if provider:
            llm_provider = LLMProvider(provider.lower())
        else:
            llm_provider = LLMProvider(getattr(settings, "llm_provider", "ollama").lower())

        # Build config from settings
        config = LLMConfig(
            provider=llm_provider,
            model_name=getattr(
                settings,
                f"{llm_provider.value}_model",
                settings.ollama_model,
            ),
            temperature=getattr(
                settings,
                f"{llm_provider.value}_temperature",
                settings.ollama_temperature,
            ),
            max_tokens=getattr(
                settings,
                f"{llm_provider.value}_max_tokens",
                settings.ollama_max_tokens,
            ),
            timeout=getattr(
                settings,
                f"{llm_provider.value}_timeout",
                settings.ollama_timeout,
            ),
            api_key=getattr(settings, f"{llm_provider.value}_api_key", None),
            base_url=(
                getattr(settings, f"{llm_provider.value}_base_url", None)
                if llm_provider != LLMProvider.OLLAMA
                else settings.ollama_base_url
            ),
        )

        return LLMFactory.create(config)
