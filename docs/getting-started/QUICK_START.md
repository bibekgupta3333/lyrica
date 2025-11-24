# Lyrica Quick Start Guide

Get the entire Lyrica monorepo running in minutes!

## Prerequisites

Make sure you have installed:

- **Node.js 22+** (or 20+)
- **pnpm 8+** (`npm install -g pnpm`)
- **Python 3.12+**
- **Docker & Docker Compose**

## 🚀 Quick Start (5 Minutes)

### Option 1: Automated Setup (Recommended)

```bash
# 1. Navigate to lyrica directory
cd lyrica

# 2. Install dependencies
pnpm install

# 3. Run everything!
bash start.sh
```

That's it! The script will:
- Start Docker services (PostgreSQL, Redis, ChromaDB)
- Set up Python backend environment
- Initialize database
- Start all development servers

### Option 2: Manual Setup

```bash
# 1. Install Node dependencies
pnpm install

# 2. Set up backend
cd lyrica-backend
bash scripts/setup.sh
cd ..

# 3. Start Docker services
pnpm docker:up

# 4. Initialize database
pnpm db:upgrade
pnpm db:seed

# 5. Run all apps
pnpm dev
```

## 📍 Access Your Apps

Once running, open:

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Web Application**: http://localhost:3000
- **Mobile App**: Metro bundler on port 8081 (requires Android/iOS setup)

## 🎯 What's Running?

### Services (Docker)
- ✅ PostgreSQL (port 5432)
- ✅ Redis (port 6379)
- ✅ ChromaDB (port 8001)

### Applications
- ✅ Backend (FastAPI) on port 8000
- ✅ Web (Next.js) on port 3000
- ✅ Mobile (React Native CLI) on port 8081

## 🛠️ Common Commands

```bash
# Development
pnpm dev              # Run all apps
pnpm dev:backend      # Backend only
pnpm dev:web          # Web only
pnpm dev:mobile       # Mobile only

# Docker
pnpm docker:up        # Start services
pnpm docker:down      # Stop services
pnpm docker:logs      # View logs

# Database
pnpm db:migrate       # Create migration
pnpm db:upgrade       # Apply migrations
pnpm db:seed          # Seed data

# Code Quality
pnpm lint             # Lint all
pnpm format           # Format all
pnpm test             # Test all

# Clean
pnpm clean            # Clean all build artifacts
```

## 🔧 Troubleshooting

### Port Already in Use

```bash
# Find and kill process on port 8000
lsof -i :8000
kill -9 <PID>

# Or change port in respective package.json
```

### Docker Not Running

```bash
# Start Docker Desktop or Docker daemon first
docker ps
```

### Backend Not Starting

```bash
cd lyrica-backend

# Recreate virtual environment
rm -rf venv
bash scripts/setup.sh

# Check Python version
python3 --version  # Should be 3.12+
```

### Database Connection Error

```bash
# Restart Docker services
pnpm docker:down
pnpm docker:up

# Wait a few seconds, then retry
```

### pnpm Command Not Found

```bash
npm install -g pnpm
```

## 📁 Project Structure

```
lyrica/
├── lyrica-backend/     # FastAPI + Python
├── lyrica-web/         # Next.js + React
├── lyrica-mobile/      # Expo + React Native
├── package.json        # Workspace config
├── turbo.json          # TurboRepo config
└── start.sh            # Unified start script
```

## 🎓 Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Test the Web App**: Visit http://localhost:3000
3. **Read the Docs**: Check out README.md for detailed info
4. **Start Coding**: Make changes and see live reload!

## 💡 Tips

- Use `pnpm dev` to run everything in parallel
- Each app auto-reloads on file changes
- Check `package.json` for all available commands
- View logs in terminal or with `pnpm docker:logs`

## 🆘 Need Help?

- Check [README.md](./README.md) for detailed documentation
- View [WBS.md](./WBS.md) for development roadmap
- See [SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md) for architecture details

---

Happy coding! 🎵✨

