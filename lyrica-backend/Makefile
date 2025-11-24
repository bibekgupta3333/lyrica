.PHONY: help setup install run test lint format clean docker-build docker-up docker-down db-init db-migrate db-upgrade db-downgrade db-seed

help:
	@echo "Lyrica Backend - Available commands:"
	@echo ""
	@echo "Setup & Run:"
	@echo "  make setup        - Setup development environment"
	@echo "  make install      - Install dependencies"
	@echo "  make run          - Run development server"
	@echo ""
	@echo "Database:"
	@echo "  make db-init      - Initialize database tables"
	@echo "  make db-migrate   - Create new migration"
	@echo "  make db-upgrade   - Apply migrations"
	@echo "  make db-downgrade - Rollback one migration"
	@echo "  make db-seed      - Seed database with sample data"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test         - Run tests"
	@echo "  make test-cov     - Run tests with coverage"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-up    - Start Docker containers"
	@echo "  make docker-down  - Stop Docker containers"
	@echo "  make docker-logs  - View Docker logs"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean        - Clean temporary files"

setup:
	@echo "🚀 Setting up development environment..."
	@bash scripts/setup.sh

install:
	@echo "📚 Installing dependencies..."
	@pip install -r requirements.txt

run:
	@echo "🚀 Starting development server..."
	@uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	@echo "🧪 Running tests..."
	@pytest -v

test-cov:
	@echo "🧪 Running tests with coverage..."
	@pytest --cov=app --cov-report=html --cov-report=term tests/

lint:
	@echo "🔍 Running linters..."
	@flake8 app/ tests/
	@mypy app/

format:
	@echo "✨ Formatting code..."
	@black app/ tests/
	@isort app/ tests/

clean:
	@echo "🧹 Cleaning temporary files..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf htmlcov/
	@rm -f .coverage

docker-build:
	@echo "🐳 Building Docker image..."
	@docker build -t lyrica-backend .

docker-up:
	@echo "🐳 Starting Docker containers..."
	@docker-compose up -d

docker-down:
	@echo "🐳 Stopping Docker containers..."
	@docker-compose down

docker-logs:
	@docker-compose logs -f backend

db-init:
	@echo "🗄️  Initializing database..."
	@python scripts/init_db.py

db-migrate:
	@echo "📝 Creating new migration..."
	@read -p "Migration description: " desc; \
	./scripts/create_migration.sh "$$desc"

db-upgrade:
	@echo "⬆️  Applying migrations..."
	@alembic upgrade head

db-downgrade:
	@echo "⬇️  Rolling back migration..."
	@alembic downgrade -1

db-seed:
	@echo "🌱 Seeding database..."
	@python scripts/seed_db.py

