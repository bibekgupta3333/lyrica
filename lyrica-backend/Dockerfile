# ============================================================================
# Production Dockerfile for Lyrica Backend
# ============================================================================

# Stage 1: Builder
FROM python:3.12-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  gcc \
  postgresql-client \
  && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Stage 2: Runtime
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PATH="/opt/venv/bin:$PATH" \
  ENVIRONMENT=production

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
  postgresql-client \
  curl \
  && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r lyrica && useradd -r -g lyrica lyrica

# Create app directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY --chown=lyrica:lyrica . .

# Create necessary directories
RUN mkdir -p /app/logs /app/ml_models /app/chroma_data && \
  chown -R lyrica:lyrica /app

# Switch to non-root user
USER lyrica

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run migrations and start server
CMD alembic upgrade head && \
  uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info
