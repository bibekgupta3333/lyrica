# Lyrica - AI-Powered Complete Song Generator 🎵

A full-stack monorepo for generating **complete songs** - lyrics, vocals with customizable pitch, and instrumental music using AI agents, RAG, and local LLMs. Transform your ideas into full songs ready for playback and download!

## ✨ Key Features

### 🎤 Complete Song Generation
- **Lyrics Creation**: AI-powered lyrics with multi-agent system
- **Voice Synthesis**: Text-to-speech with customizable pitch and effects
- **Music Composition**: Genre-matched instrumental music generation
- **Professional Mixing**: Automated multi-track mixing and mastering

### 🎵 Audio Capabilities
- **Voice Profiles**: Multiple voice options with different styles
- **Pitch Control**: Adjust vocal pitch up/down 12 semitones
- **BPM Control**: Set tempo from 40-220 BPM
- **Audio Effects**: Reverb, echo, compression, and more
- **Multi-track Production**: Separate vocal and instrumental tracks
- **Format Support**: MP3, WAV, OGG, FLAC, M4A

### 🤖 AI-Powered Features
- **Multi-Agent System**: Planning, Generation, Refinement, Voice, Music agents
- **RAG Integration**: Context-aware lyrics from vector database
- **Real-time Streaming**: Watch lyrics and audio generation live
- **Quality Scoring**: Automatic quality assessment

### 📱 Multi-Platform
- **Web App**: Full-featured web interface with audio player
- **Mobile App**: Native iOS and Android with offline playback
- **Background Play**: Continue listening while app is in background
- **Download**: Save songs for offline access

## 🏗️ Monorepo Structure

```
lyrica/
├── lyrica-backend/          # FastAPI backend with LangGraph agents
├── lyrica-web/              # Next.js web application
├── lyrica-mobile/           # React Native mobile app
├── package.json             # Root package.json with workspace scripts
├── turbo.json               # TurboRepo configuration
├── pnpm-workspace.yaml      # pnpm workspace configuration
└── docker-compose.yml       # Docker services (PostgreSQL, Redis, ChromaDB)
```

## 🚀 Quick Start

### Prerequisites

- Node.js 22+
- pnpm 8+
- Python 3.12+
- Docker & Docker Compose
- Ollama (optional, for local LLM)

### Installation

```bash
# Install pnpm globally if you haven't
npm install -g pnpm

# Install all dependencies (backend + frontend)
pnpm install

# Set up backend (creates venv, installs Python deps)
cd lyrica-backend && bash scripts/setup.sh && cd ..
```

### Running Everything

```bash
# Start all services (PostgreSQL, Redis, ChromaDB)
pnpm docker:up

# Run backend + web + mobile in parallel
pnpm dev

# Or run individually:
pnpm dev:backend   # Backend only (port 8000)
pnpm dev:web       # Web only (port 3000)
pnpm dev:mobile    # Mobile only (Expo)
```

### Access Points

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Web App**: http://localhost:3000
- **Mobile App**: Metro Bundler on port 8081 (use Android/iOS simulator)

## 📦 Available Scripts

### Root Level Commands

```bash
pnpm dev              # Run all apps in parallel
pnpm build            # Build all apps
pnpm test             # Run all tests
pnpm lint             # Lint all apps
pnpm format           # Format all code
pnpm clean            # Clean all build artifacts

# Docker commands
pnpm docker:up        # Start services
pnpm docker:down      # Stop services
pnpm docker:logs      # View logs

# Database commands
pnpm db:migrate       # Create migration
pnpm db:upgrade       # Apply migrations
pnpm db:seed          # Seed database
```

### Backend Commands

```bash
cd lyrica-backend
make dev              # Run backend server
make test             # Run tests
make lint             # Lint code
make format           # Format code
make db-upgrade       # Apply migrations
make db-seed          # Seed database
```

### Web Commands

```bash
cd lyrica-web
pnpm dev              # Run dev server
pnpm build            # Build for production
pnpm start            # Start production server
pnpm lint             # Lint code
```

### Mobile Commands

```bash
cd lyrica-mobile
pnpm install          # Install dependencies
pnpm start            # Start Metro bundler
pnpm android          # Run on Android
pnpm ios              # Run on iOS (macOS only)
```

## 🏛️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with async support
- **Database**: PostgreSQL (via SQLAlchemy)
- **Cache**: Redis
- **Vector Store**: ChromaDB for RAG
- **LLM**: Ollama (Llama 3 / Mistral)
- **Agents**: LangGraph multi-agent system
- **Embeddings**: sentence-transformers
- **Voice Synthesis**: Bark / Coqui TTS
- **Music Generation**: MusicGen / AudioCraft
- **Audio Processing**: librosa, pydub, soundfile

### Frontend Web (Next.js)
- **Framework**: Next.js 14+ with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State**: Zustand / TanStack Query
- **API Client**: Axios / Fetch

### Mobile (React Native)
- **Framework**: React Native CLI (0.76+)
- **Navigation**: React Navigation 6
- **Language**: TypeScript
- **State**: Zustand / TanStack Query
- **Platforms**: iOS, Android

## 📚 Documentation

**All documentation is organized in the [`docs/`](./docs/) folder:**

### Getting Started
- [Start Here](./docs/getting-started/START_HERE.md) ⭐ - Read this first!
- [Quick Start Guide](./docs/getting-started/QUICK_START.md) - 5-minute setup
- [Setup Complete](./docs/getting-started/SETUP_COMPLETE.md) - What's configured

### Architecture
- [System Architecture](./docs/architecture/SYSTEM_ARCHITECTURE.md) - Detailed design
- [Architecture Visual](./docs/architecture/ARCHITECTURE_VISUAL.md) - Diagrams
- [Database Design](./docs/architecture/DATABASE_DESIGN.md) - Schema & ERD

### Guides
- [Monorepo Guide](./docs/guides/MONOREPO_GUIDE.md) - TurboRepo & workspaces
- [Mobile Setup](./docs/guides/MOBILE_SETUP.md) - iOS & Android
- [Deployment Guide](./docs/guides/DEPLOYMENT_GUIDE.md) - AWS, K8s, Terraform

### Planning
- [Work Breakdown Structure](./docs/planning/WBS.md) - Feature roadmap

### Component Docs
- [Backend Documentation](./lyrica-backend/README.md)
- [Backend Database Guide](./lyrica-backend/DATABASE.md)

### Development
- [Editor Setup](./docs/guides/EDITOR_SETUP.md) - Code style & formatting

## 🐳 Docker Services

```bash
# PostgreSQL - Port 5432
# Redis - Port 6379
# ChromaDB - Port 8001

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## 🔧 Development Workflow

### 1. Start Services

```bash
pnpm docker:up
```

### 2. Initialize Database

```bash
pnpm db:upgrade
pnpm db:seed
```

### 3. Run Development Servers

```bash
pnpm dev
```

### 4. Make Changes

- Backend code: `lyrica-backend/app/`
- Web code: `lyrica-web/src/`
- Mobile code: `lyrica-mobile/`

### 5. Test & Lint

```bash
pnpm test
pnpm lint
pnpm format
```

## 🌳 Project Structure

### Backend
```
lyrica-backend/
├── app/
│   ├── api/              # API endpoints
│   ├── core/             # Core config
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas
│   ├── crud/             # CRUD operations
│   ├── services/         # Business logic
│   ├── agents/           # LangGraph agents
│   └── db/               # Database utilities
├── tests/                # Tests
├── scripts/              # Utility scripts
├── alembic/              # Database migrations
└── requirements.txt      # Python dependencies
```

### Web
```
lyrica-web/
├── src/
│   ├── app/              # Next.js App Router
│   ├── components/       # React components
│   ├── lib/              # Utilities
│   └── styles/           # Global styles
└── public/               # Static assets
```

### Mobile
```
lyrica-mobile/
├── app/                  # Expo Router pages
├── components/           # React Native components
├── services/             # API services
└── assets/               # Images, fonts, etc.
```

## 🚢 Deployment

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for detailed deployment instructions including:
- Docker deployment
- AWS infrastructure (Terraform)
- Kubernetes (EKS + Helm)
- CI/CD with GitHub Actions

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## 📝 License

[Your License Here]

## 👤 Author

Bibek Gupta

---

Built with ❤️ using FastAPI, Next.js, React Native, and TurboRepo
