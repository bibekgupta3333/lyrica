# Lyrica Monorepo Guide

Complete guide to the TurboRepo-powered monorepo structure for Lyrica.

## 🏗️ Architecture Overview

Lyrica is organized as a monorepo using **TurboRepo** and **pnpm workspaces**, containing:

```
lyrica/
├── lyrica-backend/       # Python FastAPI backend
├── lyrica-web/           # Next.js web application
├── lyrica-mobile/        # React Native mobile app
├── package.json          # Root workspace configuration
├── turbo.json            # TurboRepo pipeline config
├── pnpm-workspace.yaml   # pnpm workspace definition
└── docker-compose.yml    # Shared services
```

## 📦 Workspace Packages

### 1. lyrica-backend (Python)
- **Type**: Backend API
- **Framework**: FastAPI 0.109+
- **Runtime**: Python 3.12+
- **Package Manager**: pip (within venv)
- **Dev Server**: uvicorn (port 8000)

### 2. lyrica-web (TypeScript)
- **Type**: Web Frontend
- **Framework**: Next.js 16+
- **Runtime**: Node.js 22+
- **Package Manager**: pnpm
- **Dev Server**: Next.js dev server (port 3000)

### 3. lyrica-mobile (TypeScript)
- **Type**: Mobile App
- **Framework**: React Native CLI 0.76+
- **Runtime**: Node.js 22+
- **Package Manager**: pnpm
- **Dev Server**: Metro bundler (port 8081)

## 🔧 Package Manager: pnpm

We use **pnpm** for its efficiency and workspace support:

```bash
# Install pnpm globally
npm install -g pnpm

# Install all dependencies
pnpm install

# Install in specific workspace
pnpm --filter lyrica-web add <package>
```

### Benefits of pnpm
- ✅ Fast installation (symlinked modules)
- ✅ Disk space efficient
- ✅ Strict dependency resolution
- ✅ Built-in monorepo support

## ⚡ TurboRepo

TurboRepo orchestrates tasks across the monorepo:

### Pipeline Configuration (`turbo.json`)

```json
{
  "pipeline": {
    "build": { "dependsOn": ["^build"], "outputs": [...] },
    "dev": { "cache": false, "persistent": true },
    "lint": { "dependsOn": ["^lint"] },
    "test": { "dependsOn": ["^build"] }
  }
}
```

### Key Features
- **Parallel Execution**: Run tasks across workspaces simultaneously
- **Incremental Builds**: Only rebuild changed packages
- **Remote Caching**: Share build artifacts (optional)
- **Task Pipeline**: Define dependencies between tasks

## 🚀 Common Commands

### Development

```bash
# Run backend + web (recommended for full-stack dev)
pnpm dev

# Run all including mobile
pnpm dev:all

# Run individual workspaces
pnpm dev:backend
pnpm dev:web
pnpm dev:mobile
```

### Building

```bash
# Build all
pnpm build

# Build specific workspace
pnpm build:backend
pnpm build:web
```

### Testing & Linting

```bash
# Run all tests
pnpm test

# Lint all
pnpm lint

# Format all
pnpm format
```

### Docker Services

```bash
# Start services
pnpm docker:up

# Stop services
pnpm docker:down

# View logs
pnpm docker:logs
```

### Database

```bash
# Create migration
pnpm db:migrate

# Apply migrations
pnpm db:upgrade

# Seed database
pnpm db:seed
```

### Cleanup

```bash
# Clean all build artifacts
pnpm clean

# Remove all node_modules
rm -rf node_modules */node_modules
pnpm install
```

## 📝 Package.json Scripts

### Root Package.json

The root `package.json` defines workspace-level scripts:

```json
{
  "scripts": {
    "dev": "turbo run dev --parallel --filter=lyrica-backend --filter=lyrica-web",
    "dev:all": "turbo run dev --parallel",
    "dev:backend": "turbo run dev --filter=lyrica-backend",
    "dev:web": "turbo run dev --filter=lyrica-web",
    "dev:mobile": "cd lyrica-mobile && pnpm start",
    "build": "turbo run build",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "format": "turbo run format"
  }
}
```

### Workspace Package.json

Each workspace has its own `package.json` with local scripts:

**lyrica-backend/package.json**:
```json
{
  "scripts": {
    "dev": "bash -c 'source venv/bin/activate && uvicorn app.main:app --reload'",
    "test": "bash -c 'source venv/bin/activate && pytest'",
    "lint": "bash -c 'source venv/bin/activate && flake8'"
  }
}
```

**lyrica-web/package.json**:
```json
{
  "scripts": {
    "dev": "next dev --port 3000",
    "build": "next build",
    "start": "next start",
    "lint": "eslint"
  }
}
```

**lyrica-mobile/package.json**:
```json
{
  "scripts": {
    "dev": "react-native start",
    "start": "react-native start",
    "android": "react-native run-android",
    "ios": "react-native run-ios"
  }
}
```

## 🔄 Workspace Dependencies

### Adding Dependencies

```bash
# Add to root (devDependencies only)
pnpm add -D <package> -w

# Add to specific workspace
pnpm --filter lyrica-web add <package>
pnpm --filter lyrica-web add -D <package>

# Add to all workspaces
pnpm add <package> -r
```

### Inter-Workspace Dependencies

Currently, our workspaces are independent. To share code:

1. **Create shared package** (future):
   ```bash
   mkdir packages/shared
   pnpm --filter lyrica-web add @lyrica/shared@workspace:*
   ```

2. **Use TurboRepo dependencies**:
   ```json
   {
     "pipeline": {
       "build": { "dependsOn": ["^build"] }
     }
   }
   ```

## 🐳 Docker Integration

### Services (docker-compose.yml)

- **PostgreSQL**: Database (port 5432)
- **Redis**: Cache (port 6379)
- **ChromaDB**: Vector store (port 8001)

### Usage

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f <service>

# Stop all
docker-compose down

# Remove volumes
docker-compose down -v
```

## 🔀 Git Workflow

### Branching Strategy

```bash
main              # Production-ready code
├── develop       # Development branch
└── feature/*     # Feature branches
```

### Commit Convention

Use conventional commits:

```
feat(web): add lyrics generation UI
fix(backend): resolve database connection issue
docs(mobile): update setup instructions
chore(root): update dependencies
```

### Gitignore

Root `.gitignore` covers all workspaces:
- `node_modules/`
- `venv/`
- `.env*`
- `dist/`, `build/`, `.next/`
- `*.pyc`, `__pycache__/`

## 📊 Monorepo Benefits

### For This Project

1. **Unified Versioning**: Single source of truth
2. **Shared Configuration**: ESLint, TypeScript, etc.
3. **Atomic Changes**: Update API + frontend in one PR
4. **Simplified CI/CD**: Single pipeline
5. **Code Sharing**: Easy to extract shared utilities

### Performance

- ✅ Parallel builds with TurboRepo
- ✅ Incremental builds (only changed packages)
- ✅ Cached task results
- ✅ Optimized with pnpm

## 🚨 Best Practices

### Do's ✅

- Use `pnpm` for all Node.js dependencies
- Run `pnpm dev` from root for full-stack development
- Keep shared configs in root
- Use workspace protocol for inter-package deps
- Document architectural decisions

### Don'ts ❌

- Don't use `npm` or `yarn` (conflicts with pnpm)
- Don't install packages in workspaces without `--filter`
- Don't commit `node_modules/` or `venv/`
- Don't duplicate configuration across workspaces

## 📈 Scaling the Monorepo

### Adding New Workspaces

1. Create new directory:
   ```bash
   mkdir packages/new-package
   ```

2. Add `package.json`:
   ```json
   {
     "name": "@lyrica/new-package",
     "version": "1.0.0",
     "private": true
   }
   ```

3. Update `pnpm-workspace.yaml`:
   ```yaml
   packages:
     - 'lyrica-*'
     - 'packages/*'
   ```

4. Run `pnpm install`

### Creating Shared Packages

For shared utilities, types, or components:

```bash
# Create shared package
mkdir -p packages/shared
cd packages/shared

# Initialize
cat > package.json << 'EOF'
{
  "name": "@lyrica/shared",
  "version": "1.0.0",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc"
  }
}
EOF

# Use in other workspaces
pnpm --filter lyrica-web add @lyrica/shared@workspace:*
```

## 🔍 Debugging

### Check Workspace Structure

```bash
pnpm list -r --depth 0
```

### Verify TurboRepo Config

```bash
npx turbo run build --dry-run
```

### Check pnpm Lockfile

```bash
pnpm why <package>
```

### View Dependency Graph

```bash
pnpm list --prod --depth 1
```

## 📚 Resources

- [TurboRepo Docs](https://turbo.build/repo/docs)
- [pnpm Workspace Guide](https://pnpm.io/workspaces)
- [Monorepo Tools](https://monorepo.tools/)

---

**Happy Monorepo Development!** 🚀

