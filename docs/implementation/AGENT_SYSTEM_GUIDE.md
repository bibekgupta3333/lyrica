# Multi-Agent Song Generation System (LangGraph)

## Overview

The Lyrica Agent System is a sophisticated multi-agent workflow that orchestrates four specialized AI agents to create high-quality song lyrics. Built with [LangGraph](https://github.com/langchain-ai/langgraph), it provides:

- **🎯 Structured Workflow**: Deterministic agent orchestration
- **🔄 Iterative Refinement**: Quality improvement loops
- **📊 Quality Evaluation**: Multi-dimensional scoring
- **🧠 RAG Integration**: Context-augmented generation
- **🔌 Flexible LLM**: Multi-provider support (Ollama, OpenAI, Gemini, Grok)

## Architecture

### Agent Workflow

```
START
  ↓
┌─────────────────┐
│ Planning Agent  │  → Designs song structure
└────────┬────────┘
         ↓
┌─────────────────┐
│Generation Agent │  → Creates lyrics (with RAG)
└────────┬────────┘
         ↓
┌─────────────────┐
│Refinement Agent │  → Improves quality (iterative)
└────────┬────────┘
         ↓
┌─────────────────┐
│Evaluation Agent │  → Scores & validates
└────────┬────────┘
         ↓
    ┌────┴────┐
    │ Score?  │
    └─┬────┬──┘
      │    │
   OK │    │ Low → Retry (max 3x)
      ↓    ↓
     END  START
```

### Agents

#### 1. Planning Agent

**Responsibility**: Design song structure

**Input**:
- User prompt
- Genre, mood, theme
- Length preference

**Output**:
- Song structure (sections, order, length)
- Structure type (verse-chorus, AABA, etc.)
- Mood guidelines for each section

**Example Output**:
```
Structure: Verse-Chorus
Sections:
  1. Intro (2 lines, mysterious)
  2. Verse 1 (8 lines, reflective)
  3. Chorus (6 lines, uplifting)
  4. Verse 2 (8 lines, hopeful)
  5. Chorus (6 lines, uplifting)
  6. Bridge (6 lines, introspective)
  7. Chorus (6 lines, uplifting)
  8. Outro (2 lines, peaceful)
```

#### 2. Generation Agent

**Responsibility**: Create lyrics for each section

**Input**:
- Song structure from Planning Agent
- User preferences
- RAG context (optional)

**Output**:
- Complete song lyrics
- Song title
- Generation metadata

**Features**:
- Section-by-section generation
- RAG-augmented context (retrieves similar lyrics)
- Genre and mood-specific instructions
- Automatic title generation

**Example Output**:
```
Title: "Echoes of Tomorrow"

[INTRO]
In the silence, I hear your name
Whispered softly, like falling rain

[VERSE 1]
...
```

#### 3. Refinement Agent

**Responsibility**: Improve lyrics quality

**Input**:
- Generated lyrics
- User preferences

**Output**:
- Refined lyrics
- List of changes made
- Iteration count

**Process**:
1. **Analyze**: Identify issues (rhyme, flow, clichés, etc.)
2. **Refine**: Improve lyrics while maintaining essence
3. **Compare**: Track changes made
4. **Iterate**: Repeat if needed (max 2 iterations)

**Quality Checks**:
- ✅ Rhyme scheme consistency
- ✅ Syllable count and rhythm
- ✅ Emotional coherence
- ✅ Imagery and metaphors
- ✅ Avoid clichés
- ✅ Flow between sections

#### 4. Evaluation Agent

**Responsibility**: Assess lyrics quality

**Input**:
- Refined lyrics (or generated if refinement failed)
- User preferences

**Output**:
- Multi-dimensional scores (0-10)
- Detailed feedback
- Improvement suggestions
- Pass/fail decision

**Scoring Dimensions**:
1. **Creativity** (0-10): Originality, unique perspectives
2. **Coherence** (0-10): Logical flow, thematic unity
3. **Rhyme Quality** (0-10): Natural rhyme scheme
4. **Emotional Impact** (0-10): Ability to connect
5. **Genre Fit** (0-10): Matches intended genre
6. **Overall** (average): Final score

**Quality Threshold**: 6.5/10 (configurable)

---

## State Management

### AgentState

The complete state passed between agents:

```python
class AgentState:
    # Input
    user_id: int
    prompt: str
    genre: Optional[str]
    mood: Optional[str]
    theme: Optional[str]
    length: str  # short, medium, long
    style_references: List[str]

    # Workflow
    workflow_status: WorkflowStatus
    current_agent: Optional[str]
    workflow_start_time: datetime
    workflow_end_time: Optional[datetime]

    # Agent statuses
    planning_status: AgentStatus
    generation_status: AgentStatus
    refinement_status: AgentStatus
    evaluation_status: AgentStatus

    # Outputs
    song_structure: Optional[SongStructure]
    generated_lyrics: Optional[str]
    refined_lyrics: Optional[str]
    evaluation_score: Optional[EvaluationScore]
    final_lyrics: Optional[str]
    title: Optional[str]

    # Communication
    messages: List[AgentMessage]
    errors: List[str]
    retry_count: int
    max_retries: int
```

### Workflow Statuses

- `INITIALIZED`: Workflow created
- `PLANNING`: Planning agent running
- `GENERATING`: Generation agent running
- `REFINING`: Refinement agent running
- `EVALUATING`: Evaluation agent running
- `COMPLETED`: Successfully completed
- `FAILED`: Workflow failed

---

## API Usage

### Endpoint: POST `/api/v1/songs/generate`

Generate a complete song with the multi-agent workflow.

#### Request

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

#### Response

```json
{
  "workflow_status": "completed",
  "workflow_duration": 45.2,
  "title": "Memories of You",
  "final_lyrics": "[INTRO]\n...",
  "song_structure": {
    "sections": [...],
    "total_sections": 8,
    "structure_type": "verse-chorus",
    "estimated_duration": 180
  },
  "evaluation_score": {
    "overall": 8.2,
    "creativity": 8.5,
    "coherence": 8.0,
    "rhyme_quality": 8.3,
    "emotional_impact": 8.7,
    "genre_fit": 7.5,
    "feedback": "Excellent emotional depth...",
    "suggestions": [...]
  },
  "needs_regeneration": false,
  "refinement_iterations": 2,
  "retry_count": 0,
  "messages": [...],
  "errors": []
}
```

### Endpoint: GET `/api/v1/songs/providers`

List available LLM providers.

### Endpoint: GET `/api/v1/songs/workflow-info`

Get information about the agent workflow.

---

## Python Usage

### Basic Usage

```python
from app.agents import get_orchestrator

# Get orchestrator instance
orchestrator = get_orchestrator(
    llm_provider="ollama",  # or "openai", "gemini", "grok"
    quality_threshold=6.5,
    max_refinement_iterations=2,
)

# Generate song
result = await orchestrator.generate_song(
    user_id=1,
    prompt="A happy song about sunshine",
    genre="pop",
    mood="upbeat",
    length="short",
    use_rag=True,
)

# Check result
if result.workflow_status == WorkflowStatus.COMPLETED:
    print(f"Title: {result.title}")
    print(f"Lyrics:\n{result.final_lyrics}")
    print(f"Score: {result.evaluation_score.overall}/10")
else:
    print(f"Failed: {result.errors}")
```

### Using Individual Agents

```python
from app.agents import (
    PlanningAgent,
    GenerationAgent,
    RefinementAgent,
    EvaluationAgent,
    AgentState,
)

# Initialize state
state = AgentState(
    user_id=1,
    prompt="A song about hope",
    genre="pop",
)

# Run agents individually
planning_agent = PlanningAgent()
await planning_agent.run(state)

generation_agent = GenerationAgent()
await generation_agent.run(state)

refinement_agent = RefinementAgent()
await refinement_agent.run(state)

evaluation_agent = EvaluationAgent()
await evaluation_agent.run(state)
```

### Custom Configuration

```python
orchestrator = get_orchestrator(
    llm_provider="openai",           # Use OpenAI GPT
    quality_threshold=7.5,            # Higher quality threshold
    max_refinement_iterations=3,      # More refinement passes
)

result = await orchestrator.generate_song(
    user_id=1,
    prompt="An epic song about adventure",
    genre="rock",
    mood="energetic",
    length="long",
    style_references=["Queen", "Led Zeppelin"],
    use_rag=True,
    max_retries=5,                    # More retries allowed
)
```

---

## Testing

### Run Test Suite

```bash
cd lyrica-backend
source venv/bin/activate
python scripts/test_agent_workflow.py
```

### Test Cases

1. **Simple Song**: Short, fast generation without RAG
2. **Complex Song with RAG**: Full workflow with context retrieval
3. **Agent Messages**: Message tracking and debugging

### Manual Testing with curl

```bash
# Generate a song
curl -X POST http://localhost:8000/api/v1/songs/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A song about coding late at night",
    "genre": "indie",
    "mood": "focused",
    "length": "short",
    "use_rag": false
  }'

# Get workflow info
curl http://localhost:8000/api/v1/songs/workflow-info

# List providers
curl http://localhost:8000/api/v1/songs/providers
```

---

## Configuration

### Environment Variables

```bash
# LLM Provider (default: ollama)
LLM_PROVIDER=ollama  # or openai, gemini, grok

# Ollama (default)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7

# Gemini
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-pro

# Grok
GROK_API_KEY=...
GROK_MODEL=grok-2
```

### Quality Thresholds

Adjust quality threshold based on use case:

- **Development/Testing**: 5.0 (lenient)
- **Production**: 6.5 (balanced)
- **Premium**: 8.0 (strict)

---

## Error Handling

### Automatic Retry

The workflow automatically retries if:
- Evaluation score < quality threshold
- Retry count < max_retries (default: 3)

### Error Recovery

Each agent handles errors gracefully:
- Logs detailed error messages
- Updates state with error info
- Allows workflow to continue or fail safely

### Example Error Response

```json
{
  "workflow_status": "failed",
  "errors": [
    "[2024-01-15T10:30:00] Planning failed: Invalid structure",
    "[2024-01-15T10:30:01] Max retries exceeded"
  ],
  "messages": [
    {"agent": "Planning", "message": "Planning agent started", "level": "info"},
    {"agent": "Planning", "message": "Planning agent failed: Invalid structure", "level": "error"}
  ],
  "retry_count": 3
}
```

---

## Performance

### Typical Execution Times

| Song Length | RAG | Provider | Time     |
|-------------|-----|----------|----------|
| Short       | No  | Ollama   | ~20-30s  |
| Short       | Yes | Ollama   | ~25-40s  |
| Medium      | No  | Ollama   | ~40-60s  |
| Medium      | Yes | Ollama   | ~50-80s  |
| Long        | Yes | Ollama   | ~80-120s |
| Medium      | Yes | OpenAI   | ~20-30s  |

### Optimization Tips

1. **Disable RAG** for faster testing
2. **Use shorter length** during development
3. **Lower quality threshold** for rapid iteration
4. **Use OpenAI** for faster generation (but costs $$)
5. **Reduce refinement iterations** for speed

---

## Troubleshooting

### Issue: Workflow takes too long

**Solution**:
- Set `length="short"`
- Set `use_rag=False`
- Set `max_refinement_iterations=1`
- Use faster LLM provider

### Issue: Low quality scores

**Solution**:
- Lower `quality_threshold`
- Improve prompt quality
- Add more specific genre/mood
- Add style references
- Enable RAG for better context

### Issue: Workflow fails

**Solution**:
- Check Ollama is running: `ollama serve`
- Check ChromaDB is running: `docker ps`
- Check logs: `tail -f logs/app.log`
- Verify LLM provider credentials

### Issue: RAG returns no context

**Solution**:
- Ingest documents first: `POST /api/v1/rag/ingest/database`
- Check ChromaDB collection: `GET /api/v1/rag/stats`
- Verify query matches ingested content

---

## Future Enhancements

### Planned Features

- [ ] **Voice Selection Agent**: Choose voice profile for TTS
- [ ] **Music Planning Agent**: Plan instrumental composition
- [ ] **Audio Production Agent**: Mix and master final song
- [ ] **Collaboration Agent**: Multi-user song co-creation
- [ ] **Style Transfer Agent**: Apply artist style to lyrics
- [ ] **Translation Agent**: Multi-language lyrics

### Potential Improvements

- [ ] Parallel agent execution (where possible)
- [ ] Agent caching for similar prompts
- [ ] A/B testing multiple LLM providers
- [ ] Fine-tuned evaluation models
- [ ] User feedback loop integration
- [ ] Real-time streaming updates (WebSocket)

---

## Related Documentation

- [Flexible LLM System](FLEXIBLE_LLM_GUIDE.md)
- [RAG Implementation](RAG_IMPLEMENTATION.md)
- [System Architecture](../architecture/SYSTEM_ARCHITECTURE.md)
- [Database Design](../architecture/DATABASE_DESIGN.md)
- [WBS Planning](../planning/WBS.md)

---

## License

This agent system is part of the Lyrica project.

---

**Built with LangGraph** 🦜🔗

For questions or issues, please check the main project documentation or open an issue on GitHub.
