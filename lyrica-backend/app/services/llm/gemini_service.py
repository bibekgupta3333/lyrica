"""
Google Gemini LLM Service
Implementation for Google Gemini models.
"""

from typing import AsyncIterator, List, Optional

from loguru import logger

from app.services.llm.base import BaseLLMService, LLMMessage, LLMProvider, LLMResponse


class GeminiService(BaseLLMService):
    """LLM service for Google Gemini models."""

    def __init__(self, config):
        """Initialize Gemini service."""
        super().__init__(config)

        try:
            import google.generativeai as genai

            genai.configure(api_key=config.api_key)
            self.client = genai.GenerativeModel(config.model_name)
            logger.info(f"Gemini service initialized: {config.model_name}")
        except ImportError:
            logger.error(
                "google-generativeai package not installed. " "Run: pip install google-generativeai"
            )
            raise

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate text from prompt using Gemini."""
        try:
            # Build full prompt with system prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            logger.info(f"Gemini generating response (model: {self.model_name})")

            # Generate response
            response = self.client.generate_content(
                full_prompt,
                generation_config={
                    "temperature": temperature or self.config.temperature,
                    "max_output_tokens": max_tokens or self.config.max_tokens,
                    "top_p": self.config.top_p,
                },
            )

            return LLMResponse(
                content=response.text,
                model=self.model_name,
                provider=LLMProvider.GEMINI,
                finish_reason=(
                    response.candidates[0].finish_reason.name if response.candidates else None
                ),
            )

        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            raise

    async def generate_chat(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate chat response using Gemini."""
        try:
            # Convert messages to Gemini format
            history = []
            last_message = None

            for msg in messages:
                if msg.role == "system":
                    # System messages are prepended to first user message
                    continue
                elif msg.role == "user":
                    last_message = {"role": "user", "parts": [msg.content]}
                elif msg.role == "assistant":
                    history.append({"role": "user", "parts": [messages[0].content]})
                    history.append({"role": "model", "parts": [msg.content]})

            logger.info(f"Gemini chat generating (model: {self.model_name})")

            # Start chat and generate
            chat = self.client.start_chat(history=history)
            response = chat.send_message(
                last_message["parts"][0] if last_message else messages[-1].content,
                generation_config={
                    "temperature": temperature or self.config.temperature,
                    "max_output_tokens": max_tokens or self.config.max_tokens,
                },
            )

            return LLMResponse(
                content=response.text,
                model=self.model_name,
                provider=LLMProvider.GEMINI,
                finish_reason=(
                    response.candidates[0].finish_reason.name if response.candidates else None
                ),
            )

        except Exception as e:
            logger.error(f"Gemini chat error: {e}")
            raise

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """Generate streaming response from Gemini."""
        try:
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            logger.info(f"Gemini streaming (model: {self.model_name})")

            # Stream response
            response = self.client.generate_content(
                full_prompt,
                generation_config={
                    "temperature": temperature or self.config.temperature,
                    "max_output_tokens": max_tokens or self.config.max_tokens,
                },
                stream=True,
            )

            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.error(f"Gemini streaming error: {e}")
            raise

    async def generate_chat_stream(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """Generate streaming chat response from Gemini."""
        try:
            # Build prompt from messages
            prompt_parts = []
            for msg in messages:
                if msg.role == "system":
                    prompt_parts.append(msg.content)
                elif msg.role == "user":
                    prompt_parts.append(f"User: {msg.content}")
                elif msg.role == "assistant":
                    prompt_parts.append(f"Assistant: {msg.content}")

            full_prompt = "\n\n".join(prompt_parts)

            async for chunk in self.generate_stream(full_prompt, None, temperature, max_tokens):
                yield chunk

        except Exception as e:
            logger.error(f"Gemini chat streaming error: {e}")
            raise
