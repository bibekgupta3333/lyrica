# Quick Start Guide

Get the Lyrica Backend up and running in 5 minutes!

## Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Ollama (optional for now)

## Step 1: Setup Environment

```bash
# Navigate to backend directory
cd lyrica-backend

# Run setup script
bash scripts/setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Create `.env` file with secure secret key
- Create necessary directories

## Step 2: Start Services

```bash
# Start PostgreSQL, Redis, and ChromaDB
docker-compose up -d postgres redis chromadb

# Check if services are running
docker-compose ps
```

## Step 3: Run the Application

Option 1 - Using the run script:
```bash
bash scripts/run.sh
```

Option 2 - Using make:
```bash
make run
```

Option 3 - Manually:
```bash
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Step 4: Test the API

Open your browser or use curl:

```bash
# Health check
curl http://localhost:8000/api/v1/health

# API documentation
open http://localhost:8000/docs
```

## Step 5: Run Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run tests
make test

# Run tests with coverage
make test-cov
```

## Available Commands

```bash
make help          # Show all available commands
make setup         # Setup development environment
make run           # Run development server
make test          # Run tests
make test-cov      # Run tests with coverage
make lint          # Run linters
make format        # Format code
make docker-up     # Start all Docker services
make docker-down   # Stop all Docker services
```

## API Endpoints

Once running, you can access:

- **API Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health
- **Readiness**: http://localhost:8000/api/v1/health/ready
- **Liveness**: http://localhost:8000/api/v1/health/live
- **Metrics**: http://localhost:8000/api/v1/health/metrics
- **Info**: http://localhost:8000/api/v1/health/info
- **Prometheus Metrics**: http://localhost:8000/metrics

## Development Workflow

1. **Make changes** to code in `app/` directory
2. **Server auto-reloads** - changes are reflected immediately
3. **Run tests** - `make test`
4. **Format code** - `make format`
5. **Check linting** - `make lint`

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Docker Services Not Starting

```bash
# Check Docker is running
docker ps

# Restart services
docker-compose down
docker-compose up -d
```

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Next Steps

Now that your backend is running, you can:

1. **Add Database Models** - Create SQLAlchemy models in `app/models/`
2. **Add API Endpoints** - Create new endpoints in `app/api/v1/endpoints/`
3. **Implement Authentication** - Add JWT authentication
4. **Setup LangGraph Agents** - Create the agent system
5. **Integrate Ollama** - Connect to the LLM
6. **Add Vector Store** - Integrate ChromaDB for RAG

Refer to the WBS.md for the complete implementation plan!

