# System Architecture & Design
## Lyrica - Agentic Song Lyrics Generator

---

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Design](#component-design)
4. [Agent Architecture](#agent-architecture)
5. [Data Flow](#data-flow)
6. [Technology Stack](#technology-stack)
7. [Scalability & Performance](#scalability--performance)
8. [Security Architecture](#security-architecture)

---

## System Overview

Lyrica is an AI-powered agentic **complete song generator** that uses RAG (Retrieval-Augmented Generation) and LangGraph to create high-quality, contextually relevant song lyrics, vocals with customizable pitch, and instrumental music, producing full songs ready for playback and download.

### Key Features
- **Complete Song Generation**: Lyrics + Vocals + Music = Full Song 🎵
- **Agentic Architecture**: Multi-agent system using LangGraph for orchestration
- **RAG-based Generation**: Retrieves relevant lyrics examples to enhance generation
- **Voice Synthesis**: Text-to-speech with pitch control and vocal effects
- **Music Composition**: AI-generated instrumental music matching genre and mood
- **Audio Production**: Professional mixing and mastering pipeline
- **Real-time Streaming**: Stream lyrics, vocals, and music generation to users
- **Multi-platform**: Web (Next.js) and Mobile (React Native) clients with audio players
- **Scalable Infrastructure**: Kubernetes-based deployment on AWS

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────────────┐              ┌──────────────────────┐            │
│  │   Next.js Web App    │              │  React Native App    │            │
│  │   (TypeScript)       │              │   (TypeScript)       │            │
│  │                      │              │                      │            │
│  │  • React Components  │              │  • Native Components │            │
│  │  • TanStack Query    │              │  • React Query       │            │
│  │  • Zustand State     │              │  • Zustand State     │            │
│  │  • WebSocket Client  │              │  • WebSocket Client  │            │
│  └──────────┬───────────┘              └──────────┬───────────┘            │
│             │                                     │                         │
└─────────────┼─────────────────────────────────────┼─────────────────────────┘
              │                                     │
              └─────────────┬───────────────────────┘
                            │
                            │ HTTPS/WSS
                            │
┌─────────────────────────────────────────────────────────────────────────────┐
│                            LOAD BALANCER LAYER                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│           ┌─────────────────────────────────────────────┐                   │
│           │   AWS Application Load Balancer (ALB)       │                   │
│           │   + CloudFront CDN                           │                   │
│           │   + WAF (Web Application Firewall)           │                   │
│           └───────────────────┬─────────────────────────┘                   │
│                               │                                              │
└───────────────────────────────┼──────────────────────────────────────────────┘
                                │
                                │
┌─────────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│              ┌────────────────────────────────────────┐                      │
│              │    Kubernetes Ingress Controller       │                      │
│              │    (NGINX Ingress)                     │                      │
│              │                                        │                      │
│              │  • SSL/TLS Termination                 │                      │
│              │  • Rate Limiting                       │                      │
│              │  • Authentication                      │                      │
│              └──────────────────┬─────────────────────┘                      │
│                                 │                                            │
└─────────────────────────────────┼────────────────────────────────────────────┘
                                  │
                                  │
┌─────────────────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER (EKS)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    FastAPI Backend Services                            │  │
│  │                        (Python 3.12+)                                  │  │
│  ├───────────────────────────────────────────────────────────────────────┤  │
│  │                                                                         │  │
│  │  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────────┐  │  │
│  │  │  API Service    │  │  Agent Service   │  │  Embedding Service │  │  │
│  │  │                 │  │                  │  │                    │  │  │
│  │  │ • REST APIs     │  │ • LangGraph      │  │ • Vector Creation  │  │  │
│  │  │ • WebSocket     │  │ • Agent          │  │ • Chunking         │  │  │
│  │  │ • Auth          │  │   Orchestration  │  │ • Indexing         │  │  │
│  │  │ • Validation    │  │ • State Mgmt     │  │                    │  │  │
│  │  └────────┬────────┘  └────────┬─────────┘  └──────────┬─────────┘  │  │
│  │           │                    │                        │             │  │
│  │           └────────────────────┼────────────────────────┘             │  │
│  │                                │                                      │  │
│  │  ┌──────────────────────────────────────────────────────────────────┐│  │
│  │  │              🎵 AUDIO GENERATION SERVICES 🎵                      ││  │
│  │  ├──────────────────────────────────────────────────────────────────┤│  │
│  │  │                                                                    ││  │
│  │  │  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐││  │
│  │  │  │Voice Synthesis   │  │Music Generation  │  │Audio Mixing    │││  │
│  │  │  │Service           │  │Service           │  │Service         │││  │
│  │  │  │                  │  │                  │  │                │││  │
│  │  │  │• TTS (Bark/      │  │• MusicGen/       │  │• Multi-track   │││  │
│  │  │  │  Coqui TTS)      │  │  AudioCraft      │  │  mixing        │││  │
│  │  │  │• Pitch control   │  │• Genre matching  │  │• Mastering     │││  │
│  │  │  │• Vocal effects   │  │• Chord/melody    │  │• Normalization │││  │
│  │  │  │• Timing sync     │  │• BPM control     │  │• Export        │││  │
│  │  │  └──────────────────┘  └──────────────────┘  └────────────────┘││  │
│  │  │                                                                    ││  │
│  │  │  ┌──────────────────┐  ┌──────────────────┐                      ││  │
│  │  │  │Audio Processing  │  │Storage Service   │                      ││  │
│  │  │  │Service           │  │                  │                      ││  │
│  │  │  │                  │  │• S3/File storage │                      ││  │
│  │  │  │• Librosa/Pydub   │  │• CDN delivery    │                      ││  │
│  │  │  │• Format convert  │  │• Streaming       │                      ││  │
│  │  │  │• Waveform gen    │  │• Caching         │                      ││  │
│  │  │  └──────────────────┘  └──────────────────┘                      ││  │
│  │  │                                                                    ││  │
│  │  └────────────────────────────────────────────────────────────────────┘│  │
│  │                                                                         │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                   │                                          │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │          AGENT LAYER (LangGraph Multi-Agent System)                  │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │                     📝 LYRICS GENERATION AGENTS                       │  │
│  │                                                                        │  │
│  │   ┌────────────────┐      ┌─────────────────┐      ┌───────────────┐│  │
│  │   │ Planning Agent │─────▶│Generation Agent │─────▶│Refinement     ││  │
│  │   │                │      │                 │      │Agent          ││  │
│  │   │• Analyze input │      │• Create verses  │      │• Improve      ││  │
│  │   │• Plan structure│      │• Write chorus   │      │  quality      ││  │
│  │   │• Define style  │      │• Build bridge   │      │• Check rhyme  ││  │
│  │   └────────────────┘      └─────────────────┘      │• Enhance flow ││  │
│  │                                                      └───────┬───────┘│  │
│  │                                                              │        │  │
│  │                           ┌──────────────────────────────────┘        │  │
│  │                           │                                           │  │
│  │                           ▼                                           │  │
│  │                   ┌───────────────┐                                   │  │
│  │                   │Evaluation     │                                   │  │
│  │                   │Agent          │                                   │  │
│  │                   │• Score lyrics │                                   │  │
│  │                   │• Validate     │                                   │  │
│  │                   └───────┬───────┘                                   │  │
│  │                           │                                           │  │
│  │                           ▼                                           │  │
│  │  ─────────────────────────────────────────────────────────────────   │  │
│  │                     🎵 SONG PRODUCTION AGENTS 🎵                      │  │
│  │  ─────────────────────────────────────────────────────────────────   │  │
│  │                           │                                           │  │
│  │         ┌─────────────────┼─────────────────┐                        │  │
│  │         │                 │                 │                        │  │
│  │         ▼                 ▼                 ▼                        │  │
│  │  ┌─────────────┐   ┌─────────────┐  ┌──────────────┐               │  │
│  │  │Voice Agent  │   │Music Agent  │  │Assembly Agent│               │  │
│  │  │             │   │             │  │              │               │  │
│  │  │• TTS model  │   │• Genre match│  │• Sync lyrics │               │  │
│  │  │• Pitch adj. │   │• Generate   │  │  to audio    │               │  │
│  │  │• Timing     │   │  music      │  │• Mix tracks  │               │  │
│  │  │• Effects    │   │• BPM control│  │• Master audio│               │  │
│  │  └─────────────┘   └─────────────┘  └──────┬───────┘               │  │
│  │                                              │                        │  │
│  │                                              ▼                        │  │
│  │                                      ┌───────────────┐                │  │
│  │                                      │Quality Check  │                │  │
│  │                                      │Agent          │                │  │
│  │                                      │• Audio quality│                │  │
│  │                                      │• Mixing check │                │  │
│  │                                      │• Final polish │                │  │
│  │                                      └───────────────┘                │  │
│  │                                                                        │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  │
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AI & ML LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────────────────┐            ┌───────────────────────────────┐  │
│  │   Ollama Service         │            │   RAG Pipeline                 │  │
│  │   (Kubernetes Pod)       │            │                               │  │
│  │                          │            │  ┌─────────────────────────┐  │  │
│  │  • Llama 3 / Mistral     │            │  │  Embedding Model        │  │  │
│  │  • Model Management      │◀───────────┼──│  (sentence-transformers)│  │  │
│  │  • GPU Acceleration      │            │  │                         │  │  │
│  │  • Streaming Support     │            │  │  • all-MiniLM-L6-v2     │  │  │
│  │                          │            │  │  • Free & Open Source   │  │  │
│  └──────────────────────────┘            │  └─────────────────────────┘  │  │
│                                          │                               │  │
│                                          │  ┌─────────────────────────┐  │  │
│                                          │  │  Retrieval System       │  │  │
│                                          │  │                         │  │  │
│                                          │  │  • Semantic Search      │  │  │
│                                          │  │  • Context Ranking      │  │  │
│                                          │  │  • Similarity Scoring   │  │  │
│                                          │  └─────────────────────────┘  │  │
│                                          └───────────────────────────────┘  │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  │
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA LAYER                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────┐  ┌──────────────────────┐  ┌──────────────────┐   │
│  │  PostgreSQL (RDS)   │  │  ChromaDB            │  │  Redis Cache     │   │
│  │                     │  │  (Vector Store)      │  │  (ElastiCache)   │   │
│  │  • User data        │  │                      │  │                  │   │
│  │  • Lyrics metadata  │  │  • Lyrics embeddings │  │  • Session data  │   │
│  │  • Generation       │  │  • Semantic search   │  │  • API cache     │   │
│  │    history          │  │  • Context storage   │  │  • Rate limits   │   │
│  │  • User feedback    │  │                      │  │                  │   │
│  │                     │  │  Volume: EBS         │  │                  │   │
│  │  Multi-AZ           │  │  Persistent storage  │  │  In-memory       │   │
│  └─────────────────────┘  └──────────────────────┘  └──────────────────┘   │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      AWS S3                                          │    │
│  │                                                                       │    │
│  │  • Model artifacts                                                   │    │
│  │  • Static assets                                                     │    │
│  │  • Backups                                                           │    │
│  │  • Training data                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  │
┌─────────────────────────────────────────────────────────────────────────────┐
│                    OBSERVABILITY & MONITORING LAYER                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Prometheus  │  │   Grafana    │  │     EFK      │  │  CloudWatch  │   │
│  │              │  │              │  │              │  │              │   │
│  │  • Metrics   │  │  • Dashboards│  │  • Logs      │  │  • AWS logs  │   │
│  │  • Alerts    │  │  • Alerts    │  │  • Analytics │  │  • Metrics   │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      Jaeger (Distributed Tracing)                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Design

### 1. Client Layer

#### Next.js Web Application
```
web/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   └── register/
│   ├── (dashboard)/
│   │   ├── generate/
│   │   ├── history/
│   │   └── profile/
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   ├── ui/
│   ├── lyrics/
│   ├── forms/
│   └── layout/
├── lib/
│   ├── api/
│   ├── store/
│   └── utils/
└── hooks/
```

**Key Features:**
- Server-side rendering (SSR) for SEO
- Real-time streaming with WebSocket
- Responsive design with Tailwind CSS
- State management with Zustand
- API integration with TanStack Query

#### React Native Mobile Application
```
mobile/
├── src/
│   ├── screens/
│   │   ├── Auth/
│   │   ├── Generate/
│   │   ├── History/
│   │   └── Profile/
│   ├── components/
│   ├── navigation/
│   ├── services/
│   ├── store/
│   └── utils/
├── ios/
└── android/
```

**Key Features:**
- Native performance
- Offline support with AsyncStorage
- Push notifications
- Biometric authentication
- Share functionality

---

### 2. API Layer (FastAPI Backend)

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── lyrics.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── embeddings.py
│   │   │   │   └── search.py
│   │   │   └── api.py
│   │   └── deps.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   ├── models/
│   │   ├── user.py
│   │   ├── lyrics.py
│   │   └── generation.py
│   ├── schemas/
│   │   ├── request.py
│   │   └── response.py
│   ├── services/
│   │   ├── agent_service.py
│   │   ├── embedding_service.py
│   │   ├── ollama_service.py
│   │   └── vector_store_service.py
│   ├── agents/
│   │   ├── graph.py
│   │   ├── nodes.py
│   │   └── state.py
│   ├── db/
│   │   ├── session.py
│   │   ├── base.py
│   │   └── migrations/
│   └── main.py
├── tests/
├── Dockerfile
└── requirements.txt
```

**API Endpoints:**

```python
# Authentication
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout

# Lyrics Generation
POST   /api/v1/lyrics/generate
GET    /api/v1/lyrics/{id}
PUT    /api/v1/lyrics/{id}
DELETE /api/v1/lyrics/{id}
POST   /api/v1/lyrics/{id}/regenerate
GET    /api/v1/lyrics/history

# Embeddings & Search
POST   /api/v1/embeddings/ingest
POST   /api/v1/search/semantic
GET    /api/v1/search/similar/{id}

# User Management
GET    /api/v1/users/me
PUT    /api/v1/users/me
GET    /api/v1/users/me/preferences

# System
GET    /api/v1/health
GET    /api/v1/metrics
GET    /api/v1/styles
```

---

## Agent Architecture (LangGraph)

### Agent Graph Structure

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated

class AgentState(TypedDict):
    """State shared across agents"""
    user_input: str
    genre: str
    mood: str
    theme: str
    structure: dict
    retrieved_context: list
    generated_lyrics: dict
    refined_lyrics: dict
    evaluation_score: float
    feedback: list
    iteration: int
    max_iterations: int
    status: str

# Agent Graph
graph = StateGraph(AgentState)

# Add nodes (agents)
graph.add_node("planning", planning_agent)
graph.add_node("retrieval", retrieval_agent)
graph.add_node("generation", generation_agent)
graph.add_node("refinement", refinement_agent)
graph.add_node("evaluation", evaluation_agent)

# Define edges (workflow)
graph.set_entry_point("planning")
graph.add_edge("planning", "retrieval")
graph.add_edge("retrieval", "generation")
graph.add_edge("generation", "refinement")
graph.add_edge("refinement", "evaluation")

# Conditional edge for iteration
graph.add_conditional_edges(
    "evaluation",
    should_continue,
    {
        "continue": "generation",
        "end": END
    }
)

chain = graph.compile()
```

### Agent Descriptions

#### 1. Planning Agent
**Role:** Analyzes user input and creates a song structure plan

```python
def planning_agent(state: AgentState) -> AgentState:
    """
    - Analyzes user input (genre, mood, theme)
    - Determines song structure (verse-chorus-bridge)
    - Defines number of verses, choruses, etc.
    - Sets generation parameters
    """
    prompt = f"""
    Create a song structure plan:
    Genre: {state['genre']}
    Mood: {state['mood']}
    Theme: {state['theme']}
    
    Output a JSON structure with sections and requirements.
    """
    # Call LLM and parse response
    return state
```

**Output:**
```json
{
  "structure": {
    "intro": {"lines": 2, "style": "soft"},
    "verse1": {"lines": 8, "rhyme_scheme": "ABAB"},
    "chorus": {"lines": 4, "rhyme_scheme": "AABB", "repeat": 3},
    "verse2": {"lines": 8, "rhyme_scheme": "ABAB"},
    "bridge": {"lines": 4, "style": "contrasting"},
    "outro": {"lines": 2, "style": "fade"}
  }
}
```

#### 2. Retrieval Agent
**Role:** Retrieves relevant lyrics examples from vector store

```python
def retrieval_agent(state: AgentState) -> AgentState:
    """
    - Creates search query from state
    - Queries ChromaDB vector store
    - Retrieves top-k similar lyrics
    - Ranks and filters results
    """
    query = f"{state['genre']} {state['mood']} {state['theme']}"
    results = vector_store.similarity_search(
        query,
        k=10,
        filter={"genre": state['genre']}
    )
    state['retrieved_context'] = results
    return state
```

#### 3. Generation Agent
**Role:** Generates lyrics using LLM with retrieved context

```python
def generation_agent(state: AgentState) -> AgentState:
    """
    - Uses retrieved context as examples
    - Follows structure from planning agent
    - Generates lyrics section by section
    - Maintains consistency across sections
    """
    context = "\n".join([r['text'] for r in state['retrieved_context']])
    
    prompt = f"""
    Context examples:
    {context}
    
    Generate lyrics for:
    Structure: {state['structure']}
    Genre: {state['genre']}
    Mood: {state['mood']}
    Theme: {state['theme']}
    
    Follow the structure exactly and create original lyrics.
    """
    
    lyrics = ollama_client.generate(prompt, stream=True)
    state['generated_lyrics'] = parse_lyrics(lyrics)
    return state
```

#### 4. Refinement Agent
**Role:** Improves and polishes generated lyrics

```python
def refinement_agent(state: AgentState) -> AgentState:
    """
    - Checks rhyme scheme adherence
    - Improves word choice and imagery
    - Ensures thematic consistency
    - Enhances flow and rhythm
    - Fixes grammatical issues
    """
    prompt = f"""
    Refine these lyrics:
    {state['generated_lyrics']}
    
    Improvements needed:
    - Strengthen rhymes
    - Enhance imagery
    - Improve flow
    - Maintain {state['mood']} mood
    """
    
    refined = ollama_client.generate(prompt)
    state['refined_lyrics'] = parse_lyrics(refined)
    return state
```

#### 5. Evaluation Agent
**Role:** Evaluates quality and decides if another iteration is needed

```python
def evaluation_agent(state: AgentState) -> AgentState:
    """
    - Scores lyrics on multiple criteria
    - Provides specific feedback
    - Determines if refinement needed
    - Updates iteration counter
    """
    criteria = {
        "rhyme_quality": 0.0,
        "thematic_consistency": 0.0,
        "creativity": 0.0,
        "flow": 0.0,
        "mood_alignment": 0.0
    }
    
    # Evaluate each criterion
    for criterion in criteria:
        score = evaluate_criterion(
            state['refined_lyrics'],
            criterion,
            state
        )
        criteria[criterion] = score
    
    state['evaluation_score'] = sum(criteria.values()) / len(criteria)
    state['iteration'] += 1
    
    return state

def should_continue(state: AgentState) -> str:
    """Decide whether to continue refining"""
    if state['evaluation_score'] >= 0.8:
        return "end"
    if state['iteration'] >= state['max_iterations']:
        return "end"
    return "continue"
```

---

## Data Flow

### 1. Lyrics Generation Flow

```
User Input
    │
    ├──▶ [Frontend] Validate & format input
    │
    ├──▶ [API Gateway] Authentication & rate limiting
    │
    ├──▶ [FastAPI] POST /api/v1/lyrics/generate
    │
    ├──▶ [Agent Service] Initialize LangGraph
    │
    ├──▶ [Planning Agent] Create structure
    │
    ├──▶ [Retrieval Agent] Query ChromaDB
    │         │
    │         ├──▶ [Embedding Service] Create query embedding
    │         │
    │         └──▶ [ChromaDB] Similarity search
    │
    ├──▶ [Generation Agent] Generate lyrics
    │         │
    │         └──▶ [Ollama] LLM inference
    │
    ├──▶ [Refinement Agent] Improve lyrics
    │         │
    │         └──▶ [Ollama] LLM refinement
    │
    ├──▶ [Evaluation Agent] Score & decide
    │
    ├──▶ [PostgreSQL] Save lyrics & metadata
    │
    └──▶ [Frontend] Stream/display results
```

### 2. Document Ingestion Flow

```
Lyrics Dataset
    │
    ├──▶ [Ingestion Script] Read & clean data
    │
    ├──▶ [API] POST /api/v1/embeddings/ingest
    │
    ├──▶ [Embedding Service] Process documents
    │         │
    │         ├──▶ Chunk text (512 tokens)
    │         │
    │         ├──▶ Create embeddings
    │         │     (sentence-transformers)
    │         │
    │         └──▶ Add metadata
    │
    ├──▶ [ChromaDB] Store vectors
    │
    └──▶ [PostgreSQL] Store document metadata
```

---

## Technology Stack

### Backend
| Component | Technology | Purpose |
|-----------|-----------|---------|
| API Framework | FastAPI 0.104+ | REST API & WebSocket |
| Agent Framework | LangGraph 0.0.40+ | Multi-agent orchestration |
| LLM | Ollama (Llama 3 / Mistral) | Text generation |
| Embeddings | sentence-transformers | Text embeddings |
| Vector Store | ChromaDB 0.4+ | Semantic search |
| Database | PostgreSQL 15+ | Structured data |
| Cache | Redis 7+ | Session & API cache |
| ORM | SQLAlchemy 2.0+ | Database abstraction |
| Migrations | Alembic | Schema migrations |
| Validation | Pydantic 2.0+ | Data validation |
| Testing | pytest, pytest-asyncio | Unit & integration tests |

### Frontend Web
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | Next.js 14+ | React framework |
| Language | TypeScript 5+ | Type safety |
| UI Library | React 18+ | Component library |
| Styling | Tailwind CSS 3+ | Utility-first CSS |
| State Management | Zustand | Global state |
| Data Fetching | TanStack Query | Server state |
| Forms | React Hook Form | Form management |
| Validation | Zod | Schema validation |
| WebSocket | Socket.io-client | Real-time communication |
| Testing | Jest, React Testing Library, Playwright | Testing |

### Frontend Mobile
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | React Native 0.73+ | Mobile framework |
| Language | TypeScript 5+ | Type safety |
| Navigation | React Navigation 6+ | Routing |
| State Management | Zustand | Global state |
| Data Fetching | TanStack Query | Server state |
| Storage | AsyncStorage | Local storage |
| Testing | Jest, Detox | Testing |

### Infrastructure
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Container | Docker | Containerization |
| Orchestration | Kubernetes (EKS) | Container orchestration |
| IaC | Terraform 1.6+ | Infrastructure as code |
| Package Manager | Helm 3+ | Kubernetes packages |
| CI/CD | GitHub Actions | Automation |
| Cloud Provider | AWS | Cloud infrastructure |
| Registry | AWS ECR | Container registry |
| Monitoring | Prometheus + Grafana | Metrics & dashboards |
| Logging | EFK Stack | Log aggregation |
| Tracing | Jaeger | Distributed tracing |

---

## Scalability & Performance

### Horizontal Scaling
- **API Pods**: 3-10 replicas (auto-scaling based on CPU/memory)
- **Agent Service**: 2-5 replicas (GPU-enabled for faster inference)
- **Ollama Service**: 2-3 replicas (GPU nodes)
- **ChromaDB**: Sharded across multiple nodes

### Performance Optimizations
1. **Caching Strategy**
   - Redis for API responses (TTL: 5 minutes)
   - CDN caching for static assets
   - In-memory caching for embeddings

2. **Database Optimization**
   - Connection pooling (max 100 connections)
   - Read replicas for queries
   - Indexes on frequently queried fields

3. **Vector Store Optimization**
   - HNSW indexing for fast similarity search
   - Batch embedding generation
   - Async processing for ingestion

4. **LLM Optimization**
   - Model quantization (4-bit or 8-bit)
   - Batch inference when possible
   - Streaming responses to reduce perceived latency

### Load Testing Results (Target)
- **Concurrent Users**: 1000+
- **API Response Time**: < 2 seconds
- **Vector Search Latency**: < 500ms
- **Lyrics Generation**: < 30 seconds
- **System Uptime**: > 99.5%

---

## Security Architecture

### Authentication & Authorization
```
┌─────────────────────────────────────────────────┐
│          Authentication Flow                     │
├─────────────────────────────────────────────────┤
│                                                  │
│  User Login                                      │
│     │                                           │
│     ├──▶ POST /api/v1/auth/login               │
│     │                                           │
│     ├──▶ Verify credentials (bcrypt)            │
│     │                                           │
│     ├──▶ Generate JWT tokens                    │
│     │     • Access token (15 min)              │
│     │     • Refresh token (7 days)             │
│     │                                           │
│     └──▶ Return tokens                          │
│                                                  │
│  Authenticated Request                           │
│     │                                           │
│     ├──▶ Include Authorization header           │
│     │     Bearer <access_token>                │
│     │                                           │
│     ├──▶ API Gateway validates token            │
│     │                                           │
│     ├──▶ Check token expiration                 │
│     │                                           │
│     ├──▶ Verify signature                       │
│     │                                           │
│     └──▶ Extract user context                   │
│                                                  │
└─────────────────────────────────────────────────┘
```

### Security Measures
1. **Data Encryption**
   - TLS 1.3 for data in transit
   - AES-256 for data at rest
   - Encrypted database connections

2. **Secret Management**
   - AWS Secrets Manager for API keys
   - Environment-specific secrets
   - Rotation policies

3. **Network Security**
   - VPC isolation
   - Security groups
   - Network policies in Kubernetes
   - WAF rules

4. **API Security**
   - Rate limiting (100 req/min per user)
   - Input validation
   - CORS configuration
   - API key rotation

5. **Monitoring & Audit**
   - CloudTrail for AWS audit logs
   - Application audit logs
   - Security scanning (Trivy)
   - Vulnerability assessments

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                          AWS Cloud                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              VPC (10.0.0.0/16)                       │  │
│  │                                                       │  │
│  │  ┌─────────────────────┐  ┌─────────────────────┐   │  │
│  │  │  Public Subnets     │  │  Private Subnets    │   │  │
│  │  │  (10.0.1.0/24)      │  │  (10.0.10.0/24)     │   │  │
│  │  │                     │  │                     │   │  │
│  │  │  • ALB              │  │  • EKS Nodes        │   │  │
│  │  │  • NAT Gateway      │  │  • RDS              │   │  │
│  │  │                     │  │  • ElastiCache      │   │  │
│  │  └─────────────────────┘  └─────────────────────┘   │  │
│  │                                                       │  │
│  │  ┌─────────────────────────────────────────────┐    │  │
│  │  │         EKS Cluster (Kubernetes)             │    │  │
│  │  │                                              │    │  │
│  │  │  Namespaces:                                 │    │  │
│  │  │  • production                                │    │  │
│  │  │  • staging                                   │    │  │
│  │  │  • monitoring                                │    │  │
│  │  └─────────────────────────────────────────────┘    │  │
│  │                                                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Supporting Services:                                        │
│  • S3 (Static assets, backups)                             │
│  • ECR (Container registry)                                 │
│  • CloudWatch (Monitoring)                                  │
│  • Route53 (DNS)                                           │
│  • CloudFront (CDN)                                         │
│  • Secrets Manager (Secrets)                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Future Enhancements

1. **Multi-language Support**: Generate lyrics in multiple languages
2. **Music Generation**: Integrate with music generation models
3. **Collaborative Editing**: Real-time collaboration features
4. **Voice Input**: Accept voice descriptions for lyrics
5. **Fine-tuning**: Allow users to fine-tune on their style
6. **Marketplace**: Share and discover generated lyrics
7. **Analytics Dashboard**: Track generation patterns and trends
8. **API for Developers**: Public API for third-party integrations

---

## Conclusion

This architecture provides a scalable, maintainable, and secure foundation for the Lyrica lyrics generator. The multi-agent approach using LangGraph enables sophisticated lyrics generation, while the cloud-native deployment on AWS ensures reliability and scalability.
