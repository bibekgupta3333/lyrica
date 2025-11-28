"""
Base LLM Service
Abstract interface for different LLM providers.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, AsyncIterator, Dict, List, Optional

from pydantic import BaseModel


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OLLAMA = "ollama"
    OPENAI = "openai"
    GEMINI = "gemini"
    GROK = "grok"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"


class LLMMessage(BaseModel):
    """Standard message format for all providers."""

    role: str  # system, user, assistant
    content: str


class LLMResponse(BaseModel):
    """Standard response format from LLM."""

    content: str
    model: str
    provider: LLMProvider
    tokens_used: Optional[int] = None
    finish_reason: Optional[str] = None
    metadata: Dict[str, Any] = {}


class LLMConfig(BaseModel):
    """Configuration for LLM instances."""

    provider: LLMProvider
    model_name: str
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 300
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    extra_params: Dict[str, Any] = {}


class BaseLLMService(ABC):
    """Abstract base class for LLM services."""

    def __init__(self, config: LLMConfig):
        """
        Initialize LLM service.

        Args:
            config: LLM configuration
        """
        self.config = config
        self.provider = config.provider
        self.model_name = config.model_name

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """
        Generate text from prompt.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Returns:
            LLMResponse with generated text
        """
        pass

    @abstractmethod
    async def generate_chat(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """
        Generate text from chat messages.

        Args:
            messages: List of chat messages
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Returns:
            LLMResponse with generated text
        """
        pass

    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """
        Generate text with streaming.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Yields:
            Text chunks as they are generated
        """
        pass

    @abstractmethod
    async def generate_chat_stream(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """
        Generate chat response with streaming.

        Args:
            messages: List of chat messages
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Yields:
            Text chunks as they are generated
        """
        pass

    def _build_messages(self, prompt: str, system_prompt: Optional[str] = None) -> List[LLMMessage]:
        """
        Build messages list from prompt and system prompt.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            List of LLMMessage objects
        """
        messages = []
        if system_prompt:
            messages.append(LLMMessage(role="system", content=system_prompt))
        messages.append(LLMMessage(role="user", content=prompt))
        return messages

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.

        Returns:
            Dictionary with model information
        """
        return {
            "provider": self.provider.value,
            "model": self.model_name,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
