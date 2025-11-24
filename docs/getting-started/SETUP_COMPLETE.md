# 🎉 Lyrica Monorepo Setup Complete!

Your Lyrica monorepo is now fully configured with TurboRepo and React Native CLI.

## ✅ What's Been Set Up

### 1. **Monorepo Structure**
- ✅ TurboRepo configuration
- ✅ pnpm workspaces
- ✅ Three workspace packages (backend, web, mobile)
- ✅ Unified scripts and configuration

### 2. **Backend (lyrica-backend)**
- ✅ FastAPI application
- ✅ SQLAlchemy models
- ✅ Alembic migrations
- ✅ CRUD operations
- ✅ Health check endpoints
- ✅ Docker Compose services (PostgreSQL, Redis, ChromaDB)
- ✅ Virtual environment setup scripts

### 3. **Web (lyrica-web)**
- ✅ Next.js 16 with App Router
- ✅ TypeScript configuration
- ✅ Tailwind CSS styling
- ✅ Home page with feature showcase
- ✅ Generate page (placeholder UI)
- ✅ Environment configuration

### 4. **Mobile (lyrica-mobile)**
- ✅ React Native CLI 0.76+ setup
- ✅ TypeScript configuration
- ✅ React Navigation
- ✅ iOS native files (Podfile, etc.)
- ✅ Android native files (Gradle, Kotlin)
- ✅ Beautiful home screen component
- ✅ Dark mode support

### 5. **Infrastructure**
- ✅ Docker Compose with PostgreSQL, Redis, ChromaDB
- ✅ Unified start script (`start.sh`)
- ✅ Git configuration
- ✅ Comprehensive documentation

## 📂 Project Structure

```
lyrica/
├── package.json                    # Root workspace config
├── pnpm-workspace.yaml             # Workspace definition
├── turbo.json                      # TurboRepo pipeline
├── docker-compose.yml              # Services (Postgres, Redis, Chroma)
├── start.sh                        # Unified start script
│
├── lyrica-backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/endpoints/       # API endpoints
│   │   ├── core/                   # Config, middleware, security
│   │   ├── models/                 # Database models
│   │   ├── schemas/                # Pydantic schemas
│   │   ├── crud/                   # CRUD operations
│   │   └── main.py                 # App entry point
│   ├── alembic/                    # Migrations
│   ├── scripts/                    # Setup & utility scripts
│   ├── requirements-min.txt        # Core dependencies
│   ├── Dockerfile
│   └── package.json                # For TurboRepo integration
│
├── lyrica-web/                     # Next.js Web App
│   ├── src/
│   │   └── app/
│   │       ├── page.tsx            # Home page
│   │       └── generate/
│   │           └── page.tsx        # Generate page
│   ├── public/
│   ├── .env.local                  # Environment variables
│   └── package.json
│
└── lyrica-mobile/                  # React Native Mobile
    ├── src/
    │   ├── screens/
    │   │   └── HomeScreen.tsx      # Main screen
    │   └── App.tsx                 # Root component
    ├── android/                    # Android native
    │   ├── app/
    │   │   ├── src/main/
    │   │   │   ├── java/com/lyrica/
    │   │   │   └── AndroidManifest.xml
    │   │   └── build.gradle
    │   └── build.gradle
    ├── ios/                        # iOS native
    │   └── Podfile
    ├── index.js                    # Entry point
    └── package.json
```

## 🚀 Quick Start Commands

### 1. Install Dependencies (First Time Only)

```bash
# At root of lyrica folder
pnpm install

# Set up backend
cd lyrica-backend
bash scripts/setup.sh
cd ..
```

### 2. Start Docker Services

```bash
pnpm docker:up
```

### 3. Run Backend + Web

```bash
# Option 1: Use unified start script
bash start.sh

# Option 2: Use pnpm command
pnpm dev
```

This starts:
- Backend API on http://localhost:8000
- Web app on http://localhost:3000

### 4. Run Mobile (Optional)

Open a new terminal:

```bash
cd lyrica-mobile
pnpm install

# For iOS (macOS only)
cd ios && pod install && cd ..
pnpm ios

# For Android
pnpm android
```

## 🌐 Access Points

Once running, you can access:

| Service | URL | Description |
|---------|-----|-------------|
| Backend API | http://localhost:8000 | FastAPI server |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Health Check | http://localhost:8000/api/v1/health/health | Status endpoint |
| Web App | http://localhost:3000 | Next.js frontend |
| PostgreSQL | localhost:5432 | Database |
| Redis | localhost:6379 | Cache |
| ChromaDB | localhost:8001 | Vector store |
| Metro (Mobile) | localhost:8081 | RN bundler |

## 📝 Available Commands

### Root Level

```bash
pnpm dev              # Run backend + web
pnpm dev:all          # Run backend + web + mobile
pnpm dev:backend      # Backend only
pnpm dev:web          # Web only
pnpm dev:mobile       # Mobile only
pnpm build            # Build all
pnpm test             # Test all
pnpm lint             # Lint all
pnpm format           # Format all
pnpm clean            # Clean artifacts
pnpm docker:up        # Start services
pnpm docker:down      # Stop services
pnpm db:upgrade       # Run migrations
pnpm db:seed          # Seed database
```

### Backend (cd lyrica-backend)

```bash
make dev              # Run server
make test             # Run tests
make lint             # Lint code
make format           # Format code
make db-upgrade       # Apply migrations
make db-seed          # Seed data
```

### Web (cd lyrica-web)

```bash
pnpm dev              # Dev server
pnpm build            # Build
pnpm start            # Production
```

### Mobile (cd lyrica-mobile)

```bash
pnpm start            # Metro bundler
pnpm android          # Run Android
pnpm ios              # Run iOS
```

## 📖 Documentation

Comprehensive guides are available:

| Document | Description |
|----------|-------------|
| [README.md](./README.md) | Main project overview |
| [QUICK_START.md](./QUICK_START.md) | 5-minute quick start |
| [MONOREPO_GUIDE.md](./MONOREPO_GUIDE.md) | Monorepo architecture |
| [MOBILE_SETUP.md](./MOBILE_SETUP.md) | Mobile setup guide |
| [WBS.md](./WBS.md) | Work breakdown structure |
| [SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md) | System design |
| [DATABASE_DESIGN.md](./DATABASE_DESIGN.md) | Database schema |
| [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) | Deployment steps |

## 🎯 Next Steps

### Immediate

1. ✅ **Test the setup**: Run `pnpm dev` and access the endpoints
2. ✅ **Check health**: Visit http://localhost:8000/api/v1/health/health
3. ✅ **Explore API**: Visit http://localhost:8000/docs
4. ✅ **View web app**: Visit http://localhost:3000

### Short Term (Next Features to Build)

Based on WBS.md, the next sections to implement are:

1. **Section 2.3**: Vector Store & RAG
   - ChromaDB integration
   - Embedding model setup
   - Semantic search
   
2. **Section 2.4**: Ollama Integration
   - LLM client setup
   - Prompt templates
   - Streaming responses
   
3. **Section 2.5**: LangGraph Agents
   - Planning agent
   - Generation agent
   - Refinement agent
   - Evaluation agent
   
4. **Section 2.6**: API Endpoints
   - Lyrics generation endpoint
   - WebSocket streaming
   - CRUD operations

### Mobile Development

1. Add lyrics generation screen
2. Implement API integration
3. Add history/favorites
4. Real-time streaming UI

### Web Development

1. Complete generate page functionality
2. Add authentication
3. Build lyrics display components
4. Add export/share features

## 🛠️ Development Workflow

### Daily Development

```bash
# 1. Start services
pnpm docker:up

# 2. Run dev servers
pnpm dev

# 3. Make changes (files auto-reload)

# 4. Test changes
pnpm test

# 5. Commit
git add .
git commit -m "feat: your change"
```

### Adding Dependencies

```bash
# Backend (Python)
cd lyrica-backend
source venv/bin/activate
pip install <package>
pip freeze > requirements.txt

# Web (Node.js)
pnpm --filter lyrica-web add <package>

# Mobile (Node.js)
pnpm --filter lyrica-mobile add <package>
```

### Database Changes

```bash
# 1. Modify models in lyrica-backend/app/models/
# 2. Create migration
cd lyrica-backend
make db-migrate

# 3. Apply migration
make db-upgrade
```

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Backend (8000)
lsof -ti:8000 | xargs kill -9

# Web (3000)
lsof -ti:3000 | xargs kill -9

# Mobile (8081)
lsof -ti:8081 | xargs kill -9
```

### Docker Issues

```bash
# Restart services
pnpm docker:down
pnpm docker:up

# Clean volumes
docker-compose down -v
pnpm docker:up
```

### Backend Issues

```bash
cd lyrica-backend
rm -rf venv
bash scripts/setup.sh
```

### Frontend Issues

```bash
# Web
cd lyrica-web
rm -rf .next node_modules
pnpm install

# Mobile
cd lyrica-mobile
rm -rf node_modules
pnpm install
```

## 💡 Tips

1. **Use the unified start script**: `bash start.sh` handles everything
2. **Keep Docker running**: Services need to be up for backend
3. **Check logs**: Use `pnpm docker:logs` to debug service issues
4. **Hot reload enabled**: Changes reflect instantly in dev mode
5. **Read the docs**: Comprehensive guides available for each component

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes
3. Run tests: `pnpm test`
4. Lint code: `pnpm lint`
5. Commit: `git commit -m "feat: your feature"`
6. Push and create PR

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section
2. Review the relevant documentation
3. Check Docker logs: `pnpm docker:logs`
4. Verify services are running: `docker-compose ps`

---

**🎵 Ready to build amazing lyrics with AI! Happy coding! ✨**

