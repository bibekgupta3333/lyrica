# 🎵 START HERE - Lyrica Monorepo

## Welcome to Lyrica!

This is a **TurboRepo monorepo** containing everything you need for the Lyrica agentic song lyrics generator.

## ⚡ Quick Start (3 Commands)

```bash
# 1. Install all dependencies
pnpm install

# 2. Start Docker services
pnpm docker:up

# 3. Run backend + web
pnpm dev
```

That's it! 🎉

- **Backend API**: http://localhost:8000
- **Web App**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

## 📁 What's in This Monorepo?

```
lyrica/                         # Root monorepo
├── lyrica-backend/             # Python FastAPI backend
├── lyrica-web/                 # Next.js web frontend
└── lyrica-mobile/              # React Native mobile app
```

### Unified Commands (Run from Root)

```bash
# Development
pnpm dev              # Run backend + web together
pnpm dev:backend      # Backend only
pnpm dev:web          # Web only
pnpm dev:mobile       # Mobile only

# Docker
pnpm docker:up        # Start PostgreSQL, Redis, ChromaDB
pnpm docker:down      # Stop services
pnpm docker:logs      # View logs

# Database
pnpm db:upgrade       # Run migrations
pnpm db:seed          # Seed sample data

# Code Quality
pnpm lint             # Lint all code
pnpm format           # Format all code
pnpm test             # Test all code

# Cleanup
pnpm clean            # Clean all build artifacts
```

## 🎯 Choose Your Path

### For Backend Development → [Backend README](./lyrica-backend/README.md)

```bash
cd lyrica-backend
make dev              # Start FastAPI server
make test             # Run tests
make db-upgrade       # Run migrations
```

Tech: FastAPI, SQLAlchemy, PostgreSQL, ChromaDB, LangGraph, Ollama

### For Web Development → [Web App](./lyrica-web/)

```bash
cd lyrica-web
pnpm dev              # Start Next.js dev server
pnpm build            # Build for production
```

Tech: Next.js 16, React 19, TypeScript, Tailwind CSS

### For Mobile Development → [Mobile Setup Guide](./MOBILE_SETUP.md)

```bash
cd lyrica-mobile
pnpm install          # Install dependencies
pnpm start            # Start Metro bundler
pnpm ios              # Run on iOS (macOS only)
pnpm android          # Run on Android
```

Tech: React Native CLI 0.76, TypeScript, React Navigation

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [README.md](./README.md) | **Main overview** - Start here for comprehensive info |
| [QUICK_START.md](./QUICK_START.md) | **5-minute guide** - Get running fast |
| [SETUP_COMPLETE.md](./SETUP_COMPLETE.md) | **Setup checklist** - What's been configured |
| [MONOREPO_GUIDE.md](./MONOREPO_GUIDE.md) | **Monorepo details** - TurboRepo & pnpm workspaces |
| [ARCHITECTURE_VISUAL.md](./ARCHITECTURE_VISUAL.md) | **Visual guide** - System diagrams |
| [MOBILE_SETUP.md](./MOBILE_SETUP.md) | **Mobile guide** - iOS & Android setup |
| [WBS.md](./WBS.md) | **Development roadmap** - Feature breakdown |
| [SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md) | **System design** - Architecture details |
| [DATABASE_DESIGN.md](./DATABASE_DESIGN.md) | **Database schema** - Tables & relationships |
| [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) | **Deployment** - AWS, Kubernetes, Terraform |

## 🛠️ Prerequisites

**Required:**
- Node.js 20+ (22+ recommended)
- Python 3.12+
- pnpm 8+
- Docker & Docker Compose

**Optional (for mobile):**
- Xcode 14+ (iOS, macOS only)
- Android Studio (Android)
- CocoaPods (iOS)

## 🚀 First Time Setup

### Step 1: Install pnpm (if not installed)

```bash
npm install -g pnpm
```

### Step 2: Clone & Install

```bash
cd lyrica
pnpm install
```

### Step 3: Setup Backend

```bash
cd lyrica-backend
bash scripts/setup.sh
cd ..
```

### Step 4: Start Services

```bash
pnpm docker:up
```

Wait 10 seconds for services to be ready.

### Step 5: Initialize Database

```bash
pnpm db:upgrade
pnpm db:seed
```

### Step 6: Run!

```bash
# Option 1: Automated script
bash start.sh

# Option 2: Manual
pnpm dev
```

## 🎉 Success Checklist

Access these URLs to verify everything works:

- [ ] Backend Health: http://localhost:8000/api/v1/health/health
- [ ] API Docs: http://localhost:8000/docs
- [ ] Web App: http://localhost:3000
- [ ] Test Generate: http://localhost:3000/generate

## 🔧 Common Issues & Solutions

### Port Already in Use

```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:3000 | xargs kill -9  # Web
lsof -ti:8081 | xargs kill -9  # Mobile
```

### Docker Not Running

```bash
# Start Docker Desktop
# Then run:
pnpm docker:up
```

### Backend Won't Start

```bash
cd lyrica-backend
rm -rf venv
bash scripts/setup.sh
cd ..
pnpm dev:backend
```

### pnpm Not Found

```bash
npm install -g pnpm
```

### Database Connection Error

```bash
pnpm docker:down
pnpm docker:up
# Wait 10 seconds
pnpm db:upgrade
```

## 💡 Pro Tips

1. **Always run from root**: Use `pnpm dev` from the `lyrica/` folder
2. **Keep Docker running**: Services must be up for backend to work
3. **Use unified commands**: `pnpm dev`, `pnpm test`, etc. work across all packages
4. **Check logs**: `pnpm docker:logs` shows service logs
5. **Hot reload is on**: Changes auto-reload in dev mode

## 🌳 Project Structure

```
lyrica/
│
├── 📄 Configuration Files
│   ├── package.json          # Root workspace config
│   ├── turbo.json            # TurboRepo pipeline
│   ├── pnpm-workspace.yaml   # Workspace definition
│   ├── docker-compose.yml    # Services
│   └── start.sh              # Unified start script
│
├── 🐍 lyrica-backend/        # Python Backend
│   ├── app/                  # FastAPI application
│   ├── tests/                # Tests
│   ├── scripts/              # Setup & utilities
│   ├── alembic/              # Database migrations
│   └── requirements.txt      # Python dependencies
│
├── 🌐 lyrica-web/            # Next.js Web
│   ├── src/app/              # App router pages
│   ├── src/components/       # React components
│   └── public/               # Static files
│
└── 📱 lyrica-mobile/         # React Native
    ├── src/                  # TypeScript source
    ├── android/              # Android native
    └── ios/                  # iOS native
```

## 🎓 Learning Path

1. **Start Simple**: Run `pnpm dev` and explore the web UI
2. **Understand Backend**: Check API docs at http://localhost:8000/docs
3. **Read Architecture**: Review [SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md)
4. **Build Features**: Follow [WBS.md](./WBS.md) for what to build next
5. **Deploy**: When ready, see [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

## 🚦 What's Next?

The monorepo is ready! Here's what to implement next (from WBS.md):

### ✅ Completed
- [x] Monorepo setup (TurboRepo + pnpm)
- [x] Backend foundation (FastAPI + PostgreSQL)
- [x] Web frontend (Next.js)
- [x] Mobile app (React Native CLI)
- [x] Database models & migrations
- [x] Health check endpoints
- [x] Docker services

### 🚧 Up Next (Priority Order)
1. **Vector Store & RAG** (Section 2.3)
   - ChromaDB integration
   - Embedding model
   - Semantic search

2. **Ollama Integration** (Section 2.4)
   - Local LLM setup
   - Prompt templates
   - Streaming

3. **LangGraph Agents** (Section 2.5)
   - Multi-agent system
   - Planning, generation, refinement agents

4. **Lyrics API** (Section 2.6)
   - Generation endpoints
   - WebSocket streaming
   - CRUD operations

## 📞 Need Help?

1. **Check Documentation**: See the docs list above
2. **View Logs**: `pnpm docker:logs` or `docker-compose logs -f`
3. **Restart Services**: `pnpm docker:down && pnpm docker:up`
4. **Clean Install**: `rm -rf node_modules && pnpm install`

## 🎯 Quick Commands Reference Card

```bash
# Most Common Commands
pnpm dev              # Start development
pnpm docker:up        # Start services
pnpm test             # Run tests
pnpm lint             # Check code

# Database
pnpm db:upgrade       # Apply migrations
pnpm db:seed          # Add sample data

# Individual Apps
pnpm dev:backend      # Backend only
pnpm dev:web          # Web only
pnpm dev:mobile       # Mobile only

# Cleanup
pnpm clean            # Clean builds
pnpm docker:down      # Stop services
```

---

## 🎵 Ready to Build!

Your monorepo is fully configured and ready for development.

**Start coding:**
```bash
pnpm dev
```

**Happy coding! ✨**

