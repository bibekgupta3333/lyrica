#!/bin/bash

# Lyrica Monorepo Start Script
# Starts all services and applications

set -e

echo "🚀 Starting Lyrica Monorepo..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "${YELLOW}⚠️  Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Start Docker services
echo "${BLUE}🐳 Starting Docker services (PostgreSQL, Redis, ChromaDB)...${NC}"
pnpm docker:up

# Wait for services to be healthy
echo "${BLUE}⏳ Waiting for services to be ready...${NC}"
sleep 5

# Check if backend venv exists
if [ ! -d "lyrica-backend/venv" ]; then
    echo "${YELLOW}📦 Backend virtual environment not found. Setting up...${NC}"
    cd lyrica-backend
    bash scripts/setup.sh
    cd ..
fi

# Check if database is initialized
echo "${BLUE}🗄️  Checking database status...${NC}"
cd lyrica-backend
source venv/bin/activate
python -c "from app.db.session import engine; import asyncio; asyncio.run(engine.connect())" 2>/dev/null || {
    echo "${YELLOW}📊 Initializing database...${NC}"
    alembic upgrade head || echo "Migrations not yet created"
    python scripts/seed_db.py || echo "Seeding skipped"
}
deactivate
cd ..

echo ""
echo "${GREEN}✅ All services are ready!${NC}"
echo ""
echo "${BLUE}📚 Tip: Check docs/getting-started/START_HERE.md for detailed info${NC}"
echo ""
echo "Starting applications..."
echo ""
echo "${GREEN}📍 Access Points:${NC}"
echo "   Backend API:  http://localhost:8000"
echo "   API Docs:     http://localhost:8000/docs"
echo "   Web App:      http://localhost:3000"
echo "   Mobile:       Metro Bundler on port 8081"
echo ""
echo "${BLUE}📱 Mobile Setup:${NC}"
echo "   To run mobile app, open a new terminal and run:"
echo "   cd lyrica-mobile && pnpm install"
echo "   pnpm android  (for Android)"
echo "   pnpm ios      (for iOS - macOS only)"
echo ""
echo "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Start all dev servers in parallel using turbo
pnpm dev

