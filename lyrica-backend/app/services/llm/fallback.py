"""
LLM fallback handler for graceful degradation.

This module provides fallback mechanisms when primary LLM fails.
"""

import asyncio
from typing import AsyncIterator, Optional

from loguru import logger

from app.services.llm.base import BaseLLMService, LLMMessage, LLMResponse


class LLMFallbackHandler:
    """
    Fallback handler for LLM services.

    Tries primary service first, falls back to secondary on failure.
    """

    def __init__(
        self,
        primary: BaseLLMService,
        fallbacks: list[BaseLLMService],
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Initialize fallback handler.

        Args:
            primary: Primary LLM service
            fallbacks: List of fallback services (tried in order)
            max_retries: Maximum retry attempts per service
            retry_delay: Delay between retries (seconds)
        """
        self.primary = primary
        self.fallbacks = fallbacks
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    async def generate(
        self, prompt: str, temperature: float = 0.7, max_tokens: int = 500, **kwargs
    ) -> LLMResponse:
        """
        Generate text with fallback support.

        Tries primary service first, then fallbacks if it fails.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Returns:
            LLM response

        Raises:
            Exception: If all services fail
        """
        services = [self.primary] + self.fallbacks
        last_error = None

        for service_idx, service in enumerate(services):
            is_primary = service_idx == 0

            for attempt in range(self.max_retries):
                try:
                    logger.info(
                        f"Attempting generation with {service.provider.value} "
                        f"(attempt {attempt + 1}/{self.max_retries})"
                    )

                    response = await service.generate(
                        prompt=prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        **kwargs,
                    )

                    if is_primary:
                        logger.info(f"✅ Primary service succeeded: {service.provider.value}")
                    else:
                        logger.warning(f"⚠️  Fallback service succeeded: {service.provider.value}")

                    return response

                except Exception as e:
                    last_error = e
                    logger.warning(
                        f"❌ {service.provider.value} failed (attempt {attempt + 1}): {str(e)}"
                    )

                    # Wait before retry
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay * (attempt + 1))

            # Service exhausted all retries, try next service
            logger.error(
                f"Service {service.provider.value} failed after {self.max_retries} attempts"
            )

        # All services failed
        logger.error("❌ All LLM services failed (primary + fallbacks)")
        raise Exception(f"All LLM services failed. Last error: {str(last_error)}")

    async def generate_stream(
        self, prompt: str, temperature: float = 0.7, max_tokens: int = 500, **kwargs
    ) -> AsyncIterator[dict]:
        """
        Generate streaming response with fallback.

        Note: Fallback during streaming is tricky - if primary starts streaming
        but fails mid-way, we cannot easily switch to fallback. This implementation
        will try fallback only if primary fails to start.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            **kwargs: Additional parameters

        Yields:
            Dictionary chunks with 'content' key
        """
        services = [self.primary] + self.fallbacks
        last_error = None

        for service_idx, service in enumerate(services):
            try:
                logger.info(f"Attempting streaming with {service.provider.value}")

                async for chunk in service.generate_stream(
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs,
                ):
                    yield chunk

                # If we got here, streaming succeeded
                return

            except Exception as e:
                last_error = e
                logger.warning(f"Streaming failed with {service.provider.value}: {str(e)}")

                # Try next service
                continue

        # All services failed
        logger.error("❌ All LLM streaming services failed")
        raise Exception(f"All LLM streaming services failed. Last error: {str(last_error)}")

    async def chat(
        self, messages: list[LLMMessage], temperature: float = 0.7, max_tokens: int = 500, **kwargs
    ) -> LLMResponse:
        """
        Chat with fallback support.

        Args:
            messages: Chat messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            **kwargs: Additional parameters

        Returns:
            LLM response
        """
        services = [self.primary] + self.fallbacks
        last_error = None

        for service in services:
            for attempt in range(self.max_retries):
                try:
                    response = await service.chat(
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        **kwargs,
                    )
                    return response

                except Exception as e:
                    last_error = e
                    logger.warning(f"Chat failed with {service.provider.value}: {str(e)}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay)

        raise Exception(f"All LLM chat services failed. Last error: {str(last_error)}")


# ============================================================================
# Factory Function
# ============================================================================


def create_fallback_handler(
    primary_provider: str = "ollama",
    fallback_providers: Optional[list[str]] = None,
    max_retries: int = 3,
) -> LLMFallbackHandler:
    """
    Create a fallback handler with configured services.

    Args:
        primary_provider: Primary LLM provider
        fallback_providers: List of fallback providers
        max_retries: Maximum retries per service

    Returns:
        Configured fallback handler

    Example:
        ```python
        handler = create_fallback_handler(
            primary_provider="ollama",
            fallback_providers=["openai"],
            max_retries=3
        )

        response = await handler.generate("Write a song about...")
        ```
    """
    from app.services.llm.factory import LLMFactory

    # Create primary service
    primary = LLMFactory.create(primary_provider)

    # Create fallback services
    fallbacks = []
    if fallback_providers:
        for provider in fallback_providers:
            try:
                fallback_service = LLMFactory.create(provider)
                fallbacks.append(fallback_service)
                logger.info(f"Registered fallback service: {provider}")
            except Exception as e:
                logger.warning(f"Failed to create fallback service {provider}: {str(e)}")

    return LLMFallbackHandler(primary=primary, fallbacks=fallbacks, max_retries=max_retries)
