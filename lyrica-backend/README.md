# Lyrica Backend

Agentic Song Lyrics Generator - FastAPI Backend

## Features

- ✅ FastAPI framework with async support
- ✅ Pydantic v2 for data validation
- ✅ Structured logging with Loguru
- ✅ JWT authentication
- ✅ CORS middleware
- ✅ Request ID tracking
- ✅ Health check endpoints
- ✅ Prometheus metrics
- ✅ Environment-based configuration
- ✅ Docker support

## Requirements

- Python 3.12+
- PostgreSQL 15+
- Redis 7+
- Ollama (with Llama 3 or Mistral)
- ChromaDB

## Quick Start

### 1. Clone and Setup

```bash
cd lyrica-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 3. Run the Application

```bash
# Development mode with auto-reload
python app/main.py

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access the API

- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health
- **Metrics**: http://localhost:8000/metrics

## Project Structure

```
lyrica-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── api/
│   │   └── v1/
│   │       ├── api.py       # API router
│   │       └── endpoints/   # API endpoints
│   │           └── health.py
│   ├── core/
│   │   ├── config.py        # Configuration
│   │   ├── logging.py       # Logging setup
│   │   ├── middleware.py    # Custom middleware
│   │   └── security.py      # Security utilities
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   ├── agents/              # LangGraph agents
│   ├── db/                  # Database utilities
│   └── utils/               # Utility functions
├── tests/
│   ├── unit/
│   └── integration/
├── scripts/                 # Utility scripts
├── logs/                    # Log files
├── .env                     # Environment variables
├── .env.example             # Example environment file
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose config
└── README.md               # This file
```

## API Endpoints

### Health Checks

- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/ready` - Readiness check (Kubernetes)
- `GET /api/v1/health/live` - Liveness check (Kubernetes)
- `GET /api/v1/health/metrics` - System metrics
- `GET /api/v1/health/info` - Application info

### Coming Soon

- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/lyrics/generate` - Generate lyrics
- `GET /api/v1/lyrics/{id}` - Get lyrics by ID
- And more...

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/unit/test_health.py -v
```

### Code Quality

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint code
flake8 app/ tests/

# Type checking
mypy app/
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Show current version
alembic current
```

## Docker

### Build and Run

```bash
# Build image
docker build -t lyrica-backend .

# Run container
docker run -p 8000:8000 lyrica-backend

# Using docker-compose
docker-compose up -d
```

## Environment Variables

Key environment variables (see `.env.example` for full list):

```bash
# Application
APP_NAME=Lyrica
ENVIRONMENT=development
DEBUG=True

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/lyrica_dev

# Redis
REDIS_URL=redis://localhost:6379/0

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# Security
SECRET_KEY=your-secret-key-here
```

## Logging

Logs are written to:
- Console (stdout)
- File: `logs/app.log`

Log format can be configured as:
- `json` - Structured JSON logs
- `text` - Human-readable text logs

## Monitoring

- **Prometheus Metrics**: Available at `/metrics`
- **Health Checks**: Available at `/api/v1/health/*`
- **Request Logging**: All requests are logged with timing

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## License

[Your License Here]

## Authors

- Bibek Gupta

