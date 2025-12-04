# Lyrica Documentation

Welcome to the Lyrica documentation! This folder contains all guides and documentation for the project.

## 📂 Documentation Structure

```
docs/
├── getting-started/          Quick start guides
├── architecture/             System design & architecture
├── guides/                   Detailed how-to guides
├── planning/                 Project planning & roadmap
├── PROJECT_STATUS.md         📊 Current project status tracker
└── NAVIGATION.md             Navigation guide
```

## 🚀 Getting Started

**New to Lyrica? Start here:**

1. **[PROJECT_STATUS.md](./PROJECT_STATUS.md)** 📊
   - Current project completion status
   - What's been implemented
   - What's next

2. **[START_HERE.md](./getting-started/START_HERE.md)** ⭐
   - Quick overview and first steps
   - Installation instructions
   - How to run the project

2. **[QUICK_START.md](./getting-started/QUICK_START.md)**
   - 5-minute guide to get running
   - Common commands
   - Troubleshooting tips

3. **[SETUP_COMPLETE.md](./getting-started/SETUP_COMPLETE.md)**
   - What's been configured
   - Features implemented
   - Next steps

## 🏗️ Architecture

**Understanding the system:**

- **[SYSTEM_ARCHITECTURE.md](./architecture/SYSTEM_ARCHITECTURE.md)**
  - Detailed system design
  - Component interactions
  - Technology choices

- **[ARCHITECTURE_VISUAL.md](./architecture/ARCHITECTURE_VISUAL.md)**
  - Visual diagrams and flowcharts
  - Request flow diagrams
  - System architecture visuals

- **[DATABASE_DESIGN.md](./architecture/DATABASE_DESIGN.md)**
  - Database schema
  - Table relationships
  - ERD diagrams

## 🎨 Design

**UI/UX design specifications:**

- **[FIGMA_DESIGN_PROMPT.md](./design/FIGMA_DESIGN_PROMPT.md)** 🎨
  - Complete Figma design prompt
  - Component-based design system
  - Industry-standard color palette
  - 10+ screen designs specified
  - Responsive design guidelines
  - Accessibility requirements

## 📖 Guides

**Detailed how-to guides:**

- **[AI_ASSISTANT_SETUP.md](./guides/AI_ASSISTANT_SETUP.md)** 🤖
  - Cursor AI, GitHub Copilot, Codeium setup
  - Code generation best practices
  - Project-specific prompts and patterns
  - Maintaining consistency across AI tools

- **[DATABASE_VIEWERS.md](./guides/DATABASE_VIEWERS.md)** 🐘🔴
  - pgAdmin setup and usage (PostgreSQL UI)
  - Redis Commander guide (Redis UI)
  - Database management tips
  - Troubleshooting database issues

- **[EDITOR_SETUP.md](./guides/EDITOR_SETUP.md)**
  - VSCode configuration
  - EditorConfig and Prettier
  - Recommended extensions
  - Code formatting setup

- **[MONOREPO_GUIDE.md](./guides/MONOREPO_GUIDE.md)**
  - TurboRepo setup and usage
  - Workspace management
  - Monorepo best practices

- **[MOBILE_SETUP.md](./guides/MOBILE_SETUP.md)**
  - iOS and Android setup
  - React Native CLI guide
  - Platform-specific instructions

- **[DEPLOYMENT_GUIDE.md](./guides/DEPLOYMENT_GUIDE.md)**
  - AWS deployment
  - Kubernetes setup
  - Terraform configuration
  - CI/CD pipelines

## 🤖 Implementation Guides

**Technical implementation documentation:**

- **[API_REFERENCE.md](./implementation/API_REFERENCE.md)** 🌐
  - Complete REST API documentation
  - 110+ endpoints across 14 categories
  - Request/response examples
  - Authentication guide
  - Quick reference for all endpoints

- **[AGENT_SYSTEM_GUIDE.md](./implementation/AGENT_SYSTEM_GUIDE.md)** 🦜🔗
  - Multi-agent song generation system
  - LangGraph workflow orchestration
  - Planning, Generation, Refinement, Evaluation agents
  - API usage and Python examples
  - Testing and troubleshooting

- **[FLEXIBLE_LLM_GUIDE.md](./implementation/FLEXIBLE_LLM_GUIDE.md)** 🔌
  - Provider-agnostic LLM architecture
  - Ollama, OpenAI, Gemini, Grok support
  - Instant provider switching
  - Configuration and usage examples

- **[RAG_IMPLEMENTATION.md](./implementation/RAG_IMPLEMENTATION.md)** 🧠
  - Retrieval-Augmented Generation system
  - ChromaDB vector store setup
  - Document ingestion and search
  - Embedding and chunking strategies
  - API reference and examples

- **[DATA_INGESTION_GUIDE.md](./implementation/DATA_INGESTION_GUIDE.md)** 📥 ⭐ **NEW**
  - Complete data ingestion pipeline (WBS 6.1-6.2)
  - Lyrics, music tracks, songs, voice profiles
  - Hugging Face dataset integration
  - Synthetic data generation strategies
  - ChromaDB population and embedding indexing
  - 2,300+ lyrics, 150+ tracks, 130+ songs ingested
  - Architecture diagrams and data flow
  - Usage examples and troubleshooting
  - Performance metrics (288 samples/second)

- **[STREAMING_GUIDE.md](./implementation/STREAMING_GUIDE.md)** 📡
  - Real-time streaming responses
  - Server-Sent Events (SSE)
  - WebSocket implementation
  - Streaming best practices
  - Frontend integration

- **[VOICE_SYNTHESIS_GUIDE.md](./implementation/VOICE_SYNTHESIS_GUIDE.md)** 🎤
  - Text-to-speech (TTS) systems
  - Bark and Coqui TTS engines
  - Voice profiles and customization
  - Pitch and tempo control
  - Vocal effects (reverb, echo, compression)
  - Lyrics synthesis workflow

- **[MUSIC_GENERATION_GUIDE.md](./implementation/MUSIC_GENERATION_GUIDE.md)** 🎹
  - AI-powered music composition
  - MusicGen integration
  - 15 genre support
  - Chord progression generation
  - MIDI melody creation
  - Structured composition (intro/verse/chorus)
  - Musical parameters (key, BPM, mood)

- **[COMPLETE_SONG_API_GUIDE.md](./implementation/COMPLETE_SONG_API_GUIDE.md)** 🎵
  - Complete song generation REST API (WBS 2.14)
  - End-to-end pipeline (lyrics → vocals → music → production)
  - 15+ dedicated endpoints for song management
  - Download, streaming, and distribution
  - Regenerate vocals or music independently
  - Remix and variation creation
  - Voice profiles and genre metadata
  - Full CRUD operations with database persistence

- **[AUDIO_QUALITY_GUIDE.md](./implementation/AUDIO_QUALITY_GUIDE.md)** 🎚️ ⭐ **NEW**
  - Audio Quality & Optimization system (WBS 2.15)
  - 15 quality & enhancement endpoints
  - Quality validation with scoring (0-100)
  - Spectral gating noise reduction
  - Dynamic range compression (broadcast quality)
  - M/S stereo widening
  - Comprehensive audio analysis (loudness, clarity, spectral, performance)
  - Enhancement pipeline with multiple algorithms
  - Batch processing support
  - Integration examples (Frontend, Mobile)

## 📋 Planning & Status

**Project planning and tracking:**

- **[PROJECT_STATUS.md](./PROJECT_STATUS.md)** 📊
  - Current completion status
  - Sprint progress
  - Milestones tracker
  - What's next

- **[WBS.md](./planning/WBS.md)**
  - Work Breakdown Structure
  - Complete feature roadmap
  - Development phases
  - Task breakdown (full list)

## 🎯 Quick Navigation

### I want to...

- **Get started quickly** → [QUICK_START.md](./getting-started/QUICK_START.md)
- **See all API endpoints** 🌐 → [API_REFERENCE.md](./implementation/API_REFERENCE.md)
- **Generate songs with agents** 🦜🔗 → [AGENT_SYSTEM_GUIDE.md](./implementation/AGENT_SYSTEM_GUIDE.md)
- **Use RAG for lyrics** 🧠 → [RAG_IMPLEMENTATION.md](./implementation/RAG_IMPLEMENTATION.md)
- **Switch LLM providers** 🔌 → [FLEXIBLE_LLM_GUIDE.md](./implementation/FLEXIBLE_LLM_GUIDE.md)
- **Implement streaming** 📡 → [STREAMING_GUIDE.md](./implementation/STREAMING_GUIDE.md)
- **Synthesize voice** 🎤 → [VOICE_SYNTHESIS_GUIDE.md](./implementation/VOICE_SYNTHESIS_GUIDE.md)
- **Generate music** 🎹 → [MUSIC_GENERATION_GUIDE.md](./implementation/MUSIC_GENERATION_GUIDE.md)
- **Generate complete songs** 🎵 → [COMPLETE_SONG_API_GUIDE.md](./implementation/COMPLETE_SONG_API_GUIDE.md)
- **Enhance audio quality** 🎚️ → [AUDIO_QUALITY_GUIDE.md](./implementation/AUDIO_QUALITY_GUIDE.md) ⭐ **NEW**
- **Design the UI in Figma** → [FIGMA_DESIGN_PROMPT.md](./design/FIGMA_DESIGN_PROMPT.md) 🎨
- **Use AI assistants effectively** → [AI_ASSISTANT_SETUP.md](./guides/AI_ASSISTANT_SETUP.md) 🤖
- **Manage databases visually** → [DATABASE_VIEWERS.md](./guides/DATABASE_VIEWERS.md) 🐘🔴
- **Set up my editor** → [EDITOR_SETUP.md](./guides/EDITOR_SETUP.md)
- **Understand the architecture** → [SYSTEM_ARCHITECTURE.md](./architecture/SYSTEM_ARCHITECTURE.md)
- **Set up mobile development** → [MOBILE_SETUP.md](./guides/MOBILE_SETUP.md)
- **Deploy to production** → [DEPLOYMENT_GUIDE.md](./guides/DEPLOYMENT_GUIDE.md)
- **See the roadmap** → [WBS.md](./planning/WBS.md)
- **Understand the monorepo** → [MONOREPO_GUIDE.md](./guides/MONOREPO_GUIDE.md)

## 📱 Quick Links

| Topic | Document |
|-------|----------|
| **Quick Start** | [5-min guide](./getting-started/QUICK_START.md) |
| **First Steps** | [Start here](./getting-started/START_HERE.md) |
| **Figma Design** 🎨 | [Design prompt](./design/FIGMA_DESIGN_PROMPT.md) |
| **AI Assistants** 🤖 | [Cursor/Copilot setup](./guides/AI_ASSISTANT_SETUP.md) |
| **Database Viewers** 🐘🔴 | [pgAdmin & Redis UI](./guides/DATABASE_VIEWERS.md) |
| **Editor Setup** | [VSCode & formatting](./guides/EDITOR_SETUP.md) |
| **Monorepo** | [TurboRepo guide](./guides/MONOREPO_GUIDE.md) |
| **Mobile** | [iOS/Android setup](./guides/MOBILE_SETUP.md) |
| **Architecture** | [System design](./architecture/SYSTEM_ARCHITECTURE.md) |
| **Database** | [Schema & design](./architecture/DATABASE_DESIGN.md) |
| **Deployment** | [AWS & K8s guide](./guides/DEPLOYMENT_GUIDE.md) |
| **Roadmap** | [Work breakdown](./planning/WBS.md) |
| **API Reference** 🌐 | [Complete API docs](./implementation/API_REFERENCE.md) |
| **Agent System** 🦜🔗 | [Multi-agent workflow](./implementation/AGENT_SYSTEM_GUIDE.md) |
| **RAG System** 🧠 | [RAG implementation](./implementation/RAG_IMPLEMENTATION.md) |
| **LLM Providers** 🔌 | [Flexible LLM guide](./implementation/FLEXIBLE_LLM_GUIDE.md) |
| **Streaming** 📡 | [Real-time streaming](./implementation/STREAMING_GUIDE.md) |
| **Voice Synthesis** 🎤 | [TTS & voice control](./implementation/VOICE_SYNTHESIS_GUIDE.md) |
| **Music Generation** 🎹 | [AI music composition](./implementation/MUSIC_GENERATION_GUIDE.md) |
| **Complete Song API** 🎵 | [End-to-end generation](./implementation/COMPLETE_SONG_API_GUIDE.md) |
| **Audio Quality** 🎚️ ⭐ | [Enhancement & analysis](./implementation/AUDIO_QUALITY_GUIDE.md) |

## 💡 Documentation Tips

1. **Start with** [START_HERE.md](./getting-started/START_HERE.md) if you're new
2. **Use search** (Cmd/Ctrl + F) to find specific topics
3. **Check timestamps** - docs are kept up-to-date with changes
4. **Follow links** - documents cross-reference each other

## 🔄 Keeping Docs Updated

As you develop:
- Update relevant docs when adding features
- Keep architecture docs in sync with code
- Document breaking changes
- Add examples and code snippets

## 📞 Need More Help?

- Check the [troubleshooting section](./getting-started/QUICK_START.md#troubleshooting)
- Review [common issues](./getting-started/SETUP_COMPLETE.md#troubleshooting)
- See the main [README.md](../README.md) in the root

---

**Happy reading! 📚✨**
