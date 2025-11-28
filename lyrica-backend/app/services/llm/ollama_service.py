"""
Ollama LLM Service
Implementation for local Ollama models.
"""

from typing import AsyncIterator, List, Optional

from langchain_community.llms import Ollama
from loguru import logger

from app.services.llm.base import BaseLLMService, LLMMessage, LLMProvider, LLMResponse


class OllamaService(BaseLLMService):
    """LLM service for Ollama (local models)."""

    def __init__(self, config):
        """Initialize Ollama service."""
        super().__init__(config)
        self.client = Ollama(
            base_url=config.base_url or "http://localhost:11434",
            model=config.model_name,
            temperature=config.temperature,
            timeout=config.timeout,
        )
        logger.info(f"Ollama service initialized: {config.model_name}")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate text from prompt using Ollama."""
        messages = self._build_messages(prompt, system_prompt)
        return await self.generate_chat(messages, temperature, max_tokens)

    async def generate_chat(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate chat response using Ollama."""
        try:
            # Build full prompt from messages
            prompt_parts = []
            for msg in messages:
                if msg.role == "system":
                    prompt_parts.append(f"System: {msg.content}")
                elif msg.role == "user":
                    prompt_parts.append(f"User: {msg.content}")
                elif msg.role == "assistant":
                    prompt_parts.append(f"Assistant: {msg.content}")

            full_prompt = "\n\n".join(prompt_parts)
            if not full_prompt.endswith("Assistant:"):
                full_prompt += "\n\nAssistant:"

            logger.info(f"Ollama generating response (model: {self.model_name})")

            # Generate response
            response_text = self.client.invoke(full_prompt)

            return LLMResponse(
                content=response_text,
                model=self.model_name,
                provider=LLMProvider.OLLAMA,
                finish_reason="stop",
            )

        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            raise

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """Generate streaming response from Ollama."""
        messages = self._build_messages(prompt, system_prompt)
        async for chunk in self.generate_chat_stream(messages, temperature, max_tokens):
            yield chunk

    async def generate_chat_stream(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """Generate streaming chat response from Ollama."""
        try:
            # Build full prompt
            prompt_parts = []
            for msg in messages:
                if msg.role == "system":
                    prompt_parts.append(f"System: {msg.content}")
                elif msg.role == "user":
                    prompt_parts.append(f"User: {msg.content}")

            full_prompt = "\n\n".join(prompt_parts)
            full_prompt += "\n\nAssistant:"

            logger.info(f"Ollama streaming (model: {self.model_name})")

            # Stream response
            for chunk in self.client.stream(full_prompt):
                yield chunk

        except Exception as e:
            logger.error(f"Ollama streaming error: {e}")
            raise
