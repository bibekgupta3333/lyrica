# Agent System API Quick Reference

**Quick reference for the Multi-Agent Song Generation API endpoints.**

## Base URL

```
http://localhost:8000/api/v1/songs
```

## Endpoints

### 1. Generate Song

**POST** `/generate`

Generate a complete song using the multi-agent workflow.

#### Request Body

```json
{
  "prompt": "A melancholic song about lost love",
  "genre": "ballad",
  "mood": "melancholic",
  "theme": "lost love",
  "length": "medium",
  "style_references": ["Adele", "Sam Smith"],
  "use_rag": true,
  "llm_provider": "ollama"
}
```

#### curl Example

```bash
curl -X POST http://localhost:8000/api/v1/songs/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A happy song about summer",
    "genre": "pop",
    "mood": "upbeat",
    "length": "short",
    "use_rag": false
  }'
```

#### Response (Success)

```json
{
  "workflow_status": "completed",
  "workflow_duration": 45.2,
  "title": "Summer Vibes",
  "final_lyrics": "[INTRO]\nSunshine on my face...",
  "song_structure": {
    "sections": [
      {
        "type": "intro",
        "order": 1,
        "content": "Sunshine on my face...",
        "length": 2,
        "mood": "bright",
        "refined": true
      }
    ],
    "total_sections": 6,
    "structure_type": "verse-chorus",
    "estimated_duration": 120
  },
  "evaluation_score": {
    "overall": 8.2,
    "creativity": 8.5,
    "coherence": 8.0,
    "rhyme_quality": 8.3,
    "emotional_impact": 8.7,
    "genre_fit": 7.5,
    "feedback": "Excellent emotional depth and creative imagery...",
    "suggestions": ["Consider varying rhyme scheme in verse 2"]
  },
  "needs_regeneration": false,
  "refinement_iterations": 2,
  "retry_count": 0,
  "messages": [
    {
      "agent": "Planning",
      "message": "Planning agent started",
      "timestamp": "2024-01-15T10:30:00Z",
      "level": "info"
    }
  ],
  "errors": []
}
```

#### Response (Failed)

```json
{
  "workflow_status": "failed",
  "workflow_duration": 15.3,
  "title": null,
  "final_lyrics": null,
  "evaluation_score": {
    "overall": 5.2,
    "feedback": "Quality below threshold...",
    "suggestions": ["Improve rhyme scheme", "Add more imagery"]
  },
  "needs_regeneration": true,
  "retry_count": 3,
  "errors": [
    "[2024-01-15T10:30:00] Evaluation failed: Score below threshold",
    "[2024-01-15T10:30:15] Max retries exceeded"
  ]
}
```

---

### 2. List LLM Providers

**GET** `/providers`

Get list of available LLM providers.

#### curl Example

```bash
curl http://localhost:8000/api/v1/songs/providers
```

#### Response

```json
{
  "providers": [
    {
      "name": "ollama",
      "display_name": "Ollama (Local)",
      "description": "Free local LLM (Llama 3, Mistral)",
      "cost": "free",
      "speed": "fast"
    },
    {
      "name": "openai",
      "display_name": "OpenAI GPT",
      "description": "GPT-4 and GPT-3.5 Turbo",
      "cost": "paid",
      "speed": "fast"
    },
    {
      "name": "gemini",
      "display_name": "Google Gemini",
      "description": "Gemini Pro",
      "cost": "paid",
      "speed": "fast"
    },
    {
      "name": "grok",
      "display_name": "xAI Grok",
      "description": "Grok 2",
      "cost": "paid",
      "speed": "fast"
    }
  ],
  "default": "ollama"
}
```

---

### 3. Get Workflow Info

**GET** `/workflow-info`

Get information about the agent workflow.

#### curl Example

```bash
curl http://localhost:8000/api/v1/songs/workflow-info
```

#### Response

```json
{
  "workflow": {
    "name": "Multi-Agent Song Generation",
    "description": "Orchestrated workflow using LangGraph",
    "agents": [
      {
        "name": "Planning Agent",
        "description": "Designs song structure based on prompt",
        "output": "Song structure with sections"
      },
      {
        "name": "Generation Agent",
        "description": "Creates lyrics for each section",
        "output": "Complete song lyrics",
        "features": ["RAG context retrieval", "Section-by-section generation"]
      },
      {
        "name": "Refinement Agent",
        "description": "Improves lyrics quality",
        "output": "Refined lyrics",
        "features": ["Iterative refinement", "Quality analysis"]
      },
      {
        "name": "Evaluation Agent",
        "description": "Scores and validates lyrics",
        "output": "Evaluation scores and feedback",
        "features": [
          "Multi-dimensional scoring",
          "Quality threshold checking",
          "Automatic retry if needed"
        ]
      }
    ],
    "flow": "Planning → Generation → Refinement → Evaluation → Complete",
    "features": [
      "Automatic retry on low quality",
      "RAG-augmented generation",
      "Iterative refinement",
      "Comprehensive evaluation"
    ]
  },
  "configuration": {
    "quality_threshold": 6.5,
    "max_refinement_iterations": 2,
    "max_retries": 3
  }
}
```

---

## Request Parameters

### Required

- `prompt` (string, 10-500 chars): User prompt for song generation

### Optional

- `genre` (string): Music genre (e.g., "pop", "rock", "ballad")
- `mood` (string): Desired mood (e.g., "happy", "sad", "energetic")
- `theme` (string): Song theme or topic
- `length` (string): Song length - `"short"`, `"medium"` (default), `"long"`
- `style_references` (array): Reference artists or songs for style
- `use_rag` (boolean): Whether to use RAG for context (default: `true`)
- `llm_provider` (string): LLM provider - `"ollama"` (default), `"openai"`, `"gemini"`, `"grok"`

---

## Response Fields

### Workflow Info

- `workflow_status`: Current status (`"completed"`, `"failed"`, etc.)
- `workflow_duration`: Duration in seconds

### Generated Content

- `title`: Generated song title
- `final_lyrics`: Approved final lyrics (if completed)
- `generated_lyrics`: Initial generated lyrics
- `refined_lyrics`: Lyrics after refinement

### Structure

- `song_structure`: Object with sections, structure type, duration
  - `sections`: Array of song sections
    - `type`: Section type (verse, chorus, bridge, etc.)
    - `order`: Position in song
    - `content`: Lyrics content
    - `length`: Number of lines
    - `mood`: Section mood
    - `refined`: Whether refined

### Evaluation

- `evaluation_score`: Quality scores and feedback
  - `overall`: Overall score (0-10)
  - `creativity`: Creativity score (0-10)
  - `coherence`: Coherence score (0-10)
  - `rhyme_quality`: Rhyme quality score (0-10)
  - `emotional_impact`: Emotional impact score (0-10)
  - `genre_fit`: Genre fit score (0-10)
  - `feedback`: Detailed feedback text
  - `suggestions`: Array of improvement suggestions

### Metadata

- `needs_regeneration`: Whether regeneration is needed
- `refinement_iterations`: Number of refinement passes
- `retry_count`: Number of retry attempts
- `messages`: Array of agent messages
- `errors`: Array of error messages

---

## Status Codes

- `201 Created`: Song generated successfully
- `400 Bad Request`: Invalid request parameters
- `500 Internal Server Error`: Server error during generation

---

## Example: Complete Workflow

```bash
# 1. Check available providers
curl http://localhost:8000/api/v1/songs/providers

# 2. Get workflow info
curl http://localhost:8000/api/v1/songs/workflow-info

# 3. Generate a song
curl -X POST http://localhost:8000/api/v1/songs/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A motivational anthem about overcoming obstacles",
    "genre": "rock",
    "mood": "empowering",
    "theme": "resilience",
    "length": "medium",
    "style_references": ["Imagine Dragons", "Coldplay"],
    "use_rag": true,
    "llm_provider": "ollama"
  }' | jq '.'
```

---

## Python Usage

```python
import httpx
import asyncio

async def generate_song():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/songs/generate",
            json={
                "prompt": "A love song about starry nights",
                "genre": "ballad",
                "mood": "romantic",
                "length": "short",
                "use_rag": False,
            },
            timeout=120.0,  # 2 minutes timeout
        )
        result = response.json()
        
        if result["workflow_status"] == "completed":
            print(f"✅ Title: {result['title']}")
            print(f"⭐ Score: {result['evaluation_score']['overall']}/10")
            print(f"\n🎵 Lyrics:\n{result['final_lyrics']}")
        else:
            print(f"❌ Failed: {result['errors']}")

asyncio.run(generate_song())
```

---

## Related Documentation

- [Complete Agent System Guide](AGENT_SYSTEM_GUIDE.md)
- [RAG System API](RAG_API_QUICK_REFERENCE.md)
- [Flexible LLM Guide](FLEXIBLE_LLM_GUIDE.md)

---

**For more details, see the [complete guide](AGENT_SYSTEM_GUIDE.md).**
