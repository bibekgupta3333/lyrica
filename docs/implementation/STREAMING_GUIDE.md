# LLM Streaming & Fallback System

Complete guide for real-time streaming lyrics generation and multi-provider LLM failover.

## Overview

The streaming system provides:
- **Server-Sent Events (SSE)** for real-time lyrics generation
- **Multi-provider fallback** for zero-downtime operation
- **Professional prompt templates** for consistent output
- **Automatic retry logic** with exponential backoff

---

## Table of Contents

- [Streaming Endpoints](#streaming-endpoints)
- [Fallback System](#fallback-system)
- [Prompt Templates](#prompt-templates)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)

---

## Streaming Endpoints

### POST `/api/v1/stream/lyrics`

Stream lyrics generation in real-time using Server-Sent Events.

**Request:**
```json
{
  "prompt": "A song about chasing dreams",
  "genre": "pop",
  "mood": "inspirational",
  "temperature": 0.7,
  "max_tokens": 500,
  "llm_provider": "ollama"
}
```

**Response (SSE Stream):**
```
data: {"type": "start", "message": "Starting generation..."}

data: {"type": "chunk", "content": "[Verse 1]\n"}

data: {"type": "chunk", "content": "Chasing stars across the sky\n"}

data: {"type": "chunk", "content": "Never asking why\n"}

data: {"type": "complete", "total_tokens": 150}
```

**Event Types:**
- `start` - Generation begins
- `chunk` - Content chunk (incremental)
- `complete` - Generation finished
- `error` - Error occurred

### POST `/api/v1/stream/chat`

Stream chat-based lyrics generation with conversational context.

**Request:**
```json
{
  "prompt": "Write a verse about overcoming obstacles",
  "genre": "rock",
  "mood": "determined",
  "temperature": 0.8,
  "max_tokens": 300
}
```

**Response:** Same SSE format as `/stream/lyrics`

---

## Fallback System

### Architecture

The fallback handler provides automatic failover across multiple LLM providers:

```
Primary Service (Ollama)
    ↓ (fails)
Fallback 1 (OpenAI)
    ↓ (fails)
Fallback 2 (Gemini)
    ↓ (fails)
Fallback 3 (Grok)
    ↓
Exception raised
```

### Features

- **Automatic Retry**: 3 attempts per service with exponential backoff
- **Zero-Downtime**: Seamless switching between providers
- **Detailed Logging**: Track which service handled each request
- **Configurable**: Set retry counts and delay timing

### Implementation

```python
from app.services.llm.fallback import create_fallback_handler

# Create handler with fallbacks
handler = create_fallback_handler(
    primary_provider="ollama",
    fallback_providers=["openai", "gemini"],
    max_retries=3
)

# Use like any LLM service
response = await handler.generate(
    prompt="Write a song about love",
    temperature=0.7,
    max_tokens=500
)
```

### Configuration

In `.env`:
```bash
# Primary provider
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434

# Fallback providers (optional)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

GEMINI_API_KEY=...
GEMINI_MODEL=gemini-pro
```

---

## Prompt Templates

### 1. Lyrics Generation Template

Complete song generation with structure.

```python
from app.services.prompts import LyricsGenerationPrompt

prompt = LyricsGenerationPrompt.format(
    prompt="A song about friendship",
    genre="pop",
    mood="happy",
    theme="connection",
    length="medium"
)
```

**Output:** Structured prompt with clear requirements for:
- Song structure (verses, chorus, bridge)
- Genre-appropriate style
- Mood alignment
- Rhyme scheme guidance

### 2. Verse Generation Template

Generate a single verse or section.

```python
from app.services.prompts import VerseGenerationPrompt

prompt = VerseGenerationPrompt.format(
    verse_type="Verse 2",
    title="Dreams Come True",
    genre="indie",
    mood="hopeful",
    context="[Previous verse and chorus content]",
    lines_count=4
)
```

### 3. Refinement Template

Improve existing lyrics.

```python
from app.services.prompts import RefinementPrompt

prompt = RefinementPrompt.format(
    original_lyrics="[Original lyrics here]",
    genre="rock",
    mood="energetic",
    focus="rhyme quality",
    improvement_instructions="Strengthen the metaphors"
)
```

### 4. Song Planning Template

Plan song structure before generation.

```python
from app.services.prompts import SongPlanningPrompt

prompt = SongPlanningPrompt.format(
    prompt="A song about resilience",
    genre="hip-hop",
    mood="determined",
    length="long"
)
```

**Output:** JSON structure with:
- Song sections and order
- Estimated duration
- Rhyme scheme
- Theme for each section

### 5. Evaluation Template

Evaluate lyrics quality.

```python
from app.services.prompts import EvaluationPrompt

prompt = EvaluationPrompt.format(
    lyrics="[Lyrics to evaluate]",
    genre="pop",
    mood="happy"
)
```

**Output:** JSON scores for:
- Creativity (0-10)
- Coherence (0-10)
- Rhyme quality (0-10)
- Emotional impact (0-10)
- Genre fit (0-10)
- Mood match (0-10)

---

## Usage Examples

### Example 1: Basic Streaming

```python
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

@router.post("/generate")
async def generate_lyrics(request: GenerateRequest):
    async def stream():
        llm = get_llm_service("ollama")
        
        async for chunk in llm.generate_stream(
            prompt=request.prompt,
            temperature=0.7,
            max_tokens=500
        ):
            content = chunk.get("content", "")
            yield f'data: {{"content": "{content}"}}\n\n'
    
    return StreamingResponse(stream(), media_type="text/event-stream")
```

### Example 2: Frontend Integration (JavaScript)

```javascript
const eventSource = new EventSource('/api/v1/stream/lyrics', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    prompt: 'A song about adventure',
    genre: 'pop'
  })
});

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'chunk') {
    // Append new content
    lyricsDiv.textContent += data.content;
  } else if (data.type === 'complete') {
    console.log(`Generated ${data.total_tokens} tokens`);
    eventSource.close();
  } else if (data.type === 'error') {
    console.error('Error:', data.message);
    eventSource.close();
  }
};
```

### Example 3: With Fallback

```python
from app.services.llm.fallback import create_fallback_handler

async def generate_with_fallback(prompt: str):
    # Create handler with fallback chain
    handler = create_fallback_handler(
        primary_provider="ollama",
        fallback_providers=["openai", "gemini"],
        max_retries=3
    )
    
    try:
        # Will automatically failover if primary fails
        response = await handler.generate(
            prompt=prompt,
            temperature=0.7,
            max_tokens=500
        )
        return response
    except Exception as e:
        # All providers failed
        logger.error(f"All LLM providers failed: {e}")
        raise
```

### Example 4: Using Prompt Templates

```python
from app.services.prompts import (
    get_generation_prompt,
    get_evaluation_prompt
)
from app.services.llm import get_llm_service

async def generate_and_evaluate(user_prompt: str, genre: str):
    llm = get_llm_service()
    
    # 1. Generate lyrics
    generation_prompt = get_generation_prompt(
        prompt=user_prompt,
        genre=genre,
        mood="uplifting",
        length="medium"
    )
    
    lyrics_response = await llm.generate(
        prompt=generation_prompt,
        temperature=0.7
    )
    
    lyrics = lyrics_response.content
    
    # 2. Evaluate quality
    eval_prompt = get_evaluation_prompt(
        lyrics=lyrics,
        genre=genre,
        mood="uplifting"
    )
    
    eval_response = await llm.generate(
        prompt=eval_prompt,
        temperature=0.3  # Lower temperature for evaluation
    )
    
    scores = json.loads(eval_response.content)
    
    return {
        "lyrics": lyrics,
        "scores": scores
    }
```

---

## Configuration

### Streaming Settings

```python
# app/core/config.py

class Settings(BaseSettings):
    # Streaming
    STREAM_CHUNK_SIZE: int = 10  # Characters per chunk
    STREAM_DELAY: float = 0.05   # Seconds between chunks
    
    # Fallback
    LLM_MAX_RETRIES: int = 3
    LLM_RETRY_DELAY: float = 1.0  # Initial delay (exponential)
    
    # Timeouts
    LLM_TIMEOUT: int = 300  # 5 minutes
    STREAM_TIMEOUT: int = 600  # 10 minutes
```

### Provider Priority

Configure fallback order in `.env`:

```bash
# Option 1: Fast local model with cloud backup
LLM_PROVIDER=ollama
OPENAI_API_KEY=sk-...

# Option 2: Cloud-first with local backup
LLM_PROVIDER=openai
OLLAMA_BASE_URL=http://localhost:11434

# Option 3: Multiple cloud providers
LLM_PROVIDER=gemini
OPENAI_API_KEY=sk-...
GROK_API_KEY=...
```

---

## Best Practices

### 1. Error Handling

Always handle stream errors:

```python
async def safe_stream():
    try:
        async for chunk in llm.generate_stream(prompt):
            yield chunk
    except Exception as e:
        yield {
            "type": "error",
            "message": str(e)
        }
```

### 2. Timeouts

Set appropriate timeouts:

```python
from asyncio import wait_for, TimeoutError

try:
    response = await wait_for(
        llm.generate(prompt),
        timeout=300  # 5 minutes
    )
except TimeoutError:
    # Use fallback or return error
    pass
```

### 3. Rate Limiting

Respect provider rate limits:

```python
from app.middleware.rate_limit import RateLimitMiddleware

app.add_middleware(
    RateLimitMiddleware,
    max_requests_per_minute=60,
    max_requests_per_day=1000
)
```

### 4. Cost Optimization

Use cheaper providers as primary:

```python
# Cheap local model first
handler = create_fallback_handler(
    primary_provider="ollama",  # Free
    fallback_providers=["openai"]  # Paid backup
)
```

---

## Testing

### Test Streaming Endpoint

```bash
curl -N http://localhost:8000/api/v1/stream/lyrics \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A song about AI",
    "genre": "electronic",
    "mood": "futuristic"
  }'
```

### Test Fallback System

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_fallback_on_primary_failure():
    # Mock primary to fail
    with patch('app.services.llm.ollama_service.OllamaService') as mock_ollama:
        mock_ollama.generate.side_effect = Exception("Ollama down")
        
        # Mock fallback to succeed
        with patch('app.services.llm.openai_service.OpenAIService') as mock_openai:
            mock_openai.generate.return_value = {"content": "Success!"}
            
            handler = create_fallback_handler(
                primary_provider="ollama",
                fallback_providers=["openai"]
            )
            
            result = await handler.generate("test prompt")
            
            assert result["content"] == "Success!"
            mock_ollama.generate.assert_called_once()
            mock_openai.generate.assert_called_once()
```

---

## Troubleshooting

### Issue: Stream Cuts Off Early

**Solution:** Increase timeout settings
```python
STREAM_TIMEOUT = 600  # 10 minutes
```

### Issue: Fallback Not Triggering

**Solution:** Check provider configuration
```bash
# Ensure fallback providers are configured
echo $OPENAI_API_KEY
echo $GEMINI_API_KEY
```

### Issue: High Latency

**Solution:** Optimize chunk size
```python
STREAM_CHUNK_SIZE = 20  # Larger chunks = less overhead
```

---

## API Reference

See [Streaming API Documentation](../api/STREAMING_API.md) for complete endpoint specifications.

---

**Last Updated:** November 2025  
**Version:** 1.0.0
