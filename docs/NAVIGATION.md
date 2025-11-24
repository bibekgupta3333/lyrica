# 🧭 Documentation Navigation Guide

Quick guide to finding what you need in the Lyrica documentation.

## 📍 You Are Here

```
lyrica/
├── README.md              ← Main project overview
└── docs/                  ← YOU ARE HERE
    ├── README.md          ← Documentation index
    └── NAVIGATION.md      ← This file
```

## 🎯 Find What You Need Fast

### I'm New Here → Getting Started

Start in order:

1. **[START_HERE.md](./getting-started/START_HERE.md)** ⭐
   - First-time setup
   - Quick overview
   - Essential commands

2. **[QUICK_START.md](./getting-started/QUICK_START.md)**
   - 5-minute guide
   - Get running fast
   - Common issues

3. **[SETUP_COMPLETE.md](./getting-started/SETUP_COMPLETE.md)**
   - What's configured
   - Features list
   - Next steps

### I Want to Understand the System → Architecture

- **System Overview**: [SYSTEM_ARCHITECTURE.md](./architecture/SYSTEM_ARCHITECTURE.md)
  - Components & interactions
  - Tech stack details
  - Design decisions

- **Visual Diagrams**: [ARCHITECTURE_VISUAL.md](./architecture/ARCHITECTURE_VISUAL.md)
  - System diagrams
  - Flow charts
  - Architecture visuals

- **Database**: [DATABASE_DESIGN.md](./architecture/DATABASE_DESIGN.md)
  - Schema & tables
  - Relationships
  - ERD diagrams

### I'm Building Something → Guides

- **Monorepo**: [MONOREPO_GUIDE.md](./guides/MONOREPO_GUIDE.md)
  - TurboRepo usage
  - Workspace management
  - Commands & scripts

- **Mobile Development**: [MOBILE_SETUP.md](./guides/MOBILE_SETUP.md)
  - iOS setup (Xcode, CocoaPods)
  - Android setup (Android Studio)
  - React Native CLI

- **Deployment**: [DEPLOYMENT_GUIDE.md](./guides/DEPLOYMENT_GUIDE.md)
  - AWS infrastructure
  - Kubernetes & Helm
  - Terraform configs

### I Need the Roadmap → Planning

- **Feature Roadmap**: [WBS.md](./planning/WBS.md)
  - Work breakdown
  - Feature list
  - Development phases
  - Task priorities

## 📚 Documentation by Topic

### Backend Development
- [System Architecture](./architecture/SYSTEM_ARCHITECTURE.md) - FastAPI design
- [Database Design](./architecture/DATABASE_DESIGN.md) - PostgreSQL schema
- Backend-specific docs in `lyrica-backend/README.md`

### Frontend Development
- [System Architecture](./architecture/SYSTEM_ARCHITECTURE.md) - Frontend design
- [Quick Start](./getting-started/QUICK_START.md) - Run web app
- Web-specific setup in root README

### Mobile Development
- [Mobile Setup Guide](./guides/MOBILE_SETUP.md) - Complete iOS/Android setup
- [Quick Start](./getting-started/QUICK_START.md) - Run mobile app
- [Architecture](./architecture/SYSTEM_ARCHITECTURE.md) - Mobile architecture

### DevOps & Deployment
- [Deployment Guide](./guides/DEPLOYMENT_GUIDE.md) - Complete deployment
- [Monorepo Guide](./guides/MONOREPO_GUIDE.md) - CI/CD setup
- Docker configs in root `docker-compose.yml`

### AI/ML Features
- [System Architecture](./architecture/SYSTEM_ARCHITECTURE.md) - LangGraph, RAG
- [WBS.md](./planning/WBS.md) - AI features roadmap
- ChromaDB & Ollama sections

## 🔍 Search Tips

### By File Type
```bash
# Find all markdown files
find docs -name "*.md"

# Search within docs
grep -r "your-search-term" docs/
```

### By Topic
- **Setup**: `getting-started/`
- **Design**: `architecture/`
- **How-to**: `guides/`
- **Roadmap**: `planning/`

## 📖 Reading Order

### For Developers (First Time)
1. [START_HERE.md](./getting-started/START_HERE.md)
2. [QUICK_START.md](./getting-started/QUICK_START.md)
3. [MONOREPO_GUIDE.md](./guides/MONOREPO_GUIDE.md)
4. [SYSTEM_ARCHITECTURE.md](./architecture/SYSTEM_ARCHITECTURE.md)
5. [WBS.md](./planning/WBS.md)

### For DevOps/Deployment
1. [QUICK_START.md](./getting-started/QUICK_START.md)
2. [SYSTEM_ARCHITECTURE.md](./architecture/SYSTEM_ARCHITECTURE.md)
3. [DEPLOYMENT_GUIDE.md](./guides/DEPLOYMENT_GUIDE.md)

### For Mobile Developers
1. [START_HERE.md](./getting-started/START_HERE.md)
2. [MOBILE_SETUP.md](./guides/MOBILE_SETUP.md)
3. [SYSTEM_ARCHITECTURE.md](./architecture/SYSTEM_ARCHITECTURE.md)

## 💡 Pro Tips

1. **Bookmark** [docs/README.md](./README.md) - main index
2. **Use your IDE's search** - Cmd/Ctrl + Shift + F
3. **Check timestamps** - docs are updated with code
4. **Follow cross-references** - docs link to each other

## 🆘 Can't Find Something?

1. Check [docs/README.md](./README.md) - main index
2. Search in your IDE/editor
3. Check component-specific READMEs:
   - `lyrica-backend/README.md`
   - `lyrica-web/README.md`
   - `lyrica-mobile/README.md`

## 📊 Documentation Map

```
docs/
│
├── README.md ──────────────────────┐
│   (Start here for index)          │
│                                    │
├── getting-started/                 │
│   ├── START_HERE.md ←──────────────┘
│   │   Quick overview & first steps
│   │
│   ├── QUICK_START.md
│   │   5-min guide
│   │
│   └── SETUP_COMPLETE.md
│       What's configured
│
├── architecture/
│   ├── SYSTEM_ARCHITECTURE.md
│   │   Detailed system design
│   │
│   ├── ARCHITECTURE_VISUAL.md
│   │   Diagrams & flowcharts
│   │
│   └── DATABASE_DESIGN.md
│       Schema & relationships
│
├── guides/
│   ├── MONOREPO_GUIDE.md
│   │   TurboRepo & workspaces
│   │
│   ├── MOBILE_SETUP.md
│   │   iOS & Android
│   │
│   └── DEPLOYMENT_GUIDE.md
│       AWS, K8s, Terraform
│
└── planning/
    └── WBS.md
        Feature roadmap
```

---

**Can't find what you need? Start at [docs/README.md](./README.md)** 📚
