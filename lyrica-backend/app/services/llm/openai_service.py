"""
OpenAI LLM Service
Implementation for OpenAI models (GPT-3.5, GPT-4, etc.).
"""

from typing import AsyncIterator, List, Optional

from loguru import logger

from app.services.llm.base import BaseLLMService, LLMMessage, LLMProvider, LLMResponse


class OpenAIService(BaseLLMService):
    """LLM service for OpenAI models."""

    def __init__(self, config):
        """Initialize OpenAI service."""
        super().__init__(config)

        try:
            from openai import AsyncOpenAI

            self.client = AsyncOpenAI(
                api_key=config.api_key,
                base_url=config.base_url,
                timeout=config.timeout,
            )
            logger.info(f"OpenAI service initialized: {config.model_name}")
        except ImportError:
            logger.error("openai package not installed. Run: pip install openai")
            raise

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate text from prompt using OpenAI."""
        messages = self._build_messages(prompt, system_prompt)
        return await self.generate_chat(messages, temperature, max_tokens)

    async def generate_chat(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate chat response using OpenAI."""
        try:
            # Convert to OpenAI format
            openai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

            logger.info(f"OpenAI generating response (model: {self.model_name})")

            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=openai_messages,
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens,
                top_p=self.config.top_p,
                frequency_penalty=self.config.frequency_penalty,
                presence_penalty=self.config.presence_penalty,
            )

            return LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                provider=LLMProvider.OPENAI,
                tokens_used=response.usage.total_tokens,
                finish_reason=response.choices[0].finish_reason,
            )

        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            raise

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """Generate streaming response from OpenAI."""
        messages = self._build_messages(prompt, system_prompt)
        async for chunk in self.generate_chat_stream(messages, temperature, max_tokens):
            yield chunk

    async def generate_chat_stream(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """Generate streaming chat response from OpenAI."""
        try:
            # Convert to OpenAI format
            openai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

            logger.info(f"OpenAI streaming (model: {self.model_name})")

            # Stream response
            stream = await self.client.chat.completions.create(
                model=self.model_name,
                messages=openai_messages,
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise
