# Flexible LLM System Guide

## Overview

Lyrica now supports **multiple LLM providers** with seamless switching. You can use any of these providers without changing code:

- 🦙 **Ollama** (Local, Free)
- 🤖 **OpenAI** (GPT-3.5, GPT-4)
- 🌟 **Google Gemini** (Gemini Pro)
- 🚀 **Grok** (X.AI)
- 🔮 **Anthropic Claude** (Coming soon)
- 🎯 **Cohere** (Coming soon)

---

## Quick Start

### 1. Switch Providers via Environment Variable

Edit `.env`:

```bash
# Use Ollama (default, free, local)
LLM_PROVIDER=ollama

# Or use OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here

# Or use Gemini
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-key

# Or use Grok
LLM_PROVIDER=grok
GROK_API_KEY=your-grok-key
```

That's it! Restart the server and it uses the new provider.

---

## Provider Configuration

### Ollama (Default - Local & Free)

```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
OLLAMA_TEMPERATURE=0.7
OLLAMA_MAX_TOKENS=2048
OLLAMA_TIMEOUT=300
```

**Models**: llama3, mistral, codellama, etc.

---

### OpenAI (GPT-4, GPT-3.5)

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2048
OPENAI_TIMEOUT=300
```

**Models**: gpt-4, gpt-4-turbo, gpt-3.5-turbo

---

### Google Gemini

```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-api-key
GEMINI_MODEL=gemini-pro
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=2048
GEMINI_TIMEOUT=300
```

**Models**: gemini-pro, gemini-pro-vision

---

### Grok (X.AI)

```bash
LLM_PROVIDER=grok
GROK_API_KEY=your-api-key
GROK_MODEL=grok-beta
GROK_TEMPERATURE=0.7
GROK_MAX_TOKENS=2048
GROK_TIMEOUT=300
GROK_BASE_URL=https://api.x.ai/v1
```

---

## Code Usage

### Basic Usage

```python
from app.services.llm import get_llm_service

# Use default provider from settings
llm = get_llm_service()
response = await llm.generate("Write a song about love")
print(response.content)
```

### Switch Provider Programmatically

```python
# Use specific provider
llm = get_llm_service("openai")
response = await llm.generate("Write a song")

# Switch to Gemini
llm = get_llm_service("gemini")
response = await llm.generate("Write lyrics")

# Back to Ollama
llm = get_llm_service("ollama")
response = await llm.generate("Create music")
```

### Streaming Response

```python
llm = get_llm_service()

async for chunk in llm.generate_stream("Write a song about the ocean"):
    print(chunk, end="", flush=True)
```

### Chat Messages

```python
from app.services.llm import LLMMessage

messages = [
    LLMMessage(role="system", content="You are a creative songwriter"),
    LLMMessage(role="user", content="Write a pop song"),
    LLMMessage(role="assistant", content="Here's a pop song..."),
    LLMMessage(role="user", content="Make it more energetic"),
]

response = await llm.generate_chat(messages)
print(response.content)
```

### Custom Configuration

```python
from app.services.llm import LLMConfig, LLMProvider, LLMFactory

config = LLMConfig(
    provider=LLMProvider.OPENAI,
    model_name="gpt-4",
    temperature=0.9,
    max_tokens=4000,
    api_key="your-key",
)

llm = LLMFactory.create(config)
response = await llm.generate("Write creative lyrics")
```

---

## RAG Service Integration

The RAG service automatically uses the configured provider:

```python
from app.services.rag import rag_service

# Uses provider from LLM_PROVIDER in .env
result = await rag_service.generate_lyrics_with_context(
    theme="adventure",
    genre="rock",
    mood="energetic"
)

print(result["response"])  # Generated with configured LLM
```

### Override Provider for Specific Request

```python
from app.services.rag import RAGService

# Force OpenAI for this request
rag = RAGService(provider="openai")
result = await rag.generate_lyrics_with_context(
    theme="love",
    genre="ballad"
)
```

---

## API Usage

### Generate with Default Provider

```bash
curl -X POST http://localhost:8000/api/v1/rag/generate/lyrics \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "summer nights",
    "genre": "pop",
    "mood": "upbeat"
  }'
```

### Check Current Model

```bash
curl http://localhost:8000/api/v1/llm/info
```

Response:
```json
{
  "provider": "ollama",
  "model": "llama3",
  "temperature": 0.7,
  "max_tokens": 2048
}
```

---

## Adding New Providers

### 1. Create Service Class

Create `app/services/llm/your_provider_service.py`:

```python
from app.services.llm.base import BaseLLMService, LLMResponse, LLMProvider

class YourProviderService(BaseLLMService):
    def __init__(self, config):
        super().__init__(config)
        # Initialize your provider client

    async def generate(self, prompt, system_prompt=None, **kwargs):
        # Implement generation logic
        return LLMResponse(
            content="Generated text",
            model=self.model_name,
            provider=LLMProvider.YOUR_PROVIDER
        )

    # Implement other required methods...
```

### 2. Update Factory

Edit `app/services/llm/factory.py`:

```python
from app.services.llm.base import LLMProvider

class LLMProvider(str, Enum):
    # ...existing providers
    YOUR_PROVIDER = "your_provider"

# In LLMFactory.create():
elif config.provider == LLMProvider.YOUR_PROVIDER:
    from app.services.llm.your_provider_service import YourProviderService
    return YourProviderService(config)
```

### 3. Add Config

Edit `app/core/config.py`:

```python
# Your Provider Configuration
your_provider_api_key: Optional[str] = Field(default=None)
your_provider_model: str = Field(default="default-model")
your_provider_temperature: float = Field(default=0.7)
# ...more config
```

### 4. Use It

```bash
LLM_PROVIDER=your_provider
YOUR_PROVIDER_API_KEY=key
```

---

## Comparison

| Provider | Cost | Speed | Quality | Local | Best For |
|----------|------|-------|---------|-------|----------|
| Ollama | Free | Fast | Good | ✅ | Development, Privacy |
| OpenAI | $$$ | Fast | Excellent | ❌ | Production, Quality |
| Gemini | $$ | Fast | Excellent | ❌ | Cost-effective |
| Grok | $$ | Fast | Good | ❌ | X.AI ecosystem |

---

## Best Practices

### 1. Development vs Production

```bash
# Development (.env.development)
LLM_PROVIDER=ollama  # Free, local

# Production (.env.production)
LLM_PROVIDER=openai  # Better quality
OPENAI_API_KEY=...
```

### 2. Fallback Strategy

```python
# Try OpenAI, fallback to Ollama
try:
    llm = get_llm_service("openai")
    response = await llm.generate(prompt)
except Exception as e:
    logger.warning(f"OpenAI failed: {e}, falling back to Ollama")
    llm = get_llm_service("ollama")
    response = await llm.generate(prompt)
```

### 3. Cost Optimization

```python
# Use cheaper model for drafts
draft_llm = get_llm_service()  # Ollama or Gemini
draft = await draft_llm.generate("Quick draft lyrics")

# Use premium model for final version
premium_llm = get_llm_service("openai")
final = await premium_llm.generate(f"Improve: {draft}")
```

---

## Troubleshooting

### Provider Not Working

1. Check API key in `.env`
2. Verify model name is correct
3. Check network connectivity
4. Review logs: `tail -f logs/app.log`

### Import Errors

Install provider package:

```bash
# OpenAI
pip install openai

# Gemini
pip install google-generativeai

# All providers
pip install openai google-generativeai anthropic cohere
```

### Rate Limits

```python
# Add retry logic
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential())
async def generate_with_retry(llm, prompt):
    return await llm.generate(prompt)
```

---

## Future Providers

Coming soon:
- **Anthropic Claude 3** (Opus, Sonnet, Haiku)
- **Cohere Command**
- **Meta LLaMA via Replicate**
- **Azure OpenAI**
- **Custom API endpoints**

---

## Summary

✅ **Multiple Providers**: Ollama, OpenAI, Gemini, Grok  
✅ **Easy Switching**: Just change environment variable  
✅ **Consistent Interface**: Same code works with all providers  
✅ **Streaming Support**: Real-time text generation  
✅ **Extensible**: Add new providers easily  
✅ **Production Ready**: Error handling, timeouts, retries  

**Switch providers anytime without changing a single line of code!** 🚀

---

**Last Updated**: November 27, 2025  
**Version**: 1.0.0
