# Docker Deployment Guide

Complete guide for deploying Lyrica using Docker in production.

## Table of Contents

- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Building Images](#building-images)
- [Running Services](#running-services)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Security](#security)

---

## Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 8GB+ RAM
- 20GB+ disk space

### 1. Setup Environment

```bash
# Copy environment template
cp .env.prod.example .env.prod

# Edit with your values
nano .env.prod
```

**Required Variables:**
- `POSTGRES_PASSWORD`: Secure database password
- `REDIS_PASSWORD`: Secure Redis password  
- `SECRET_KEY`: Generate with `openssl rand -hex 32`
- `NEXT_PUBLIC_API_URL`: Your production API URL
- `CORS_ORIGINS`: Allowed frontend origins

### 2. Build Images

```bash
# Build all services
pnpm docker:build

# Or manually
docker-compose -f docker-compose.prod.yml build
```

### 3. Start Services

```bash
# Start in detached mode
pnpm docker:up

# Or manually
docker-compose -f docker-compose.prod.yml up -d
```

### 4. Verify Deployment

```bash
# Check all services are running
docker-compose -f docker-compose.prod.yml ps

# View logs
pnpm docker:logs

# Test health endpoints
curl http://localhost:8000/api/v1/health
curl http://localhost:3000/api/health
```

---

## Configuration

### Service Ports

| Service | Internal | External (Default) |
|---------|----------|-------------------|
| Backend API | 8000 | 8000 |
| Frontend Web | 3000 | 3000 |
| PostgreSQL | 5432 | 5432 |
| Redis | 6379 | 6379 |
| ChromaDB | 8000 | 8001 |

**Customize ports in `.env.prod`:**
```bash
BACKEND_PORT=8000
WEB_PORT=3000
POSTGRES_PORT=5432
REDIS_PORT=6379
CHROMA_PORT=8001
```

### Resource Limits

Default resource constraints (per service):

**Backend:**
- CPUs: 2
- Memory: 4GB

**Frontend:**
- CPUs: 1
- Memory: 1GB

**Database:**
- CPUs: 1
- Memory: 1GB

**Adjust in `docker-compose.prod.yml`:**
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 4G
```

### LLM Configuration

Configure your LLM provider in `.env.prod`:

**Option 1: Ollama (Local)**
```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

**Option 2: OpenAI**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
```

**Option 3: Google Gemini**
```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-pro
```

---

## Building Images

### Build All Services

```bash
docker-compose -f docker-compose.prod.yml build --no-cache
```

### Build Specific Service

```bash
# Backend only
docker-compose -f docker-compose.prod.yml build backend

# Frontend only
docker-compose -f docker-compose.prod.yml build web
```

### Multi-Platform Builds (for ARM/AMD)

```bash
docker buildx create --name multiarch --use
docker buildx build --platform linux/amd64,linux/arm64 \
  -t lyrica-backend:prod ./lyrica-backend
```

---

## Running Services

### Start All Services

```bash
# Detached mode (background)
docker-compose -f docker-compose.prod.yml up -d

# Foreground (with logs)
docker-compose -f docker-compose.prod.yml up
```

### Start Specific Services

```bash
# Database only
docker-compose -f docker-compose.prod.yml up -d postgres redis chromadb

# Application only (requires databases running)
docker-compose -f docker-compose.prod.yml up -d backend web
```

### Stop Services

```bash
# Stop all
pnpm docker:down

# Or manually
docker-compose -f docker-compose.prod.yml down

# Stop and remove volumes (⚠️ destroys data!)
docker-compose -f docker-compose.prod.yml down -v
```

### Restart Services

```bash
# Restart all
pnpm docker:restart

# Restart specific service
docker-compose -f docker-compose.prod.yml restart backend
```

---

## Monitoring

### View Logs

```bash
# All services
pnpm docker:logs

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100 backend
```

### Service Status

```bash
# Check running containers
docker-compose -f docker-compose.prod.yml ps

# Resource usage
docker stats

# Health checks
docker inspect --format='{{.State.Health.Status}}' lyrica-backend-prod
```

### Access Container Shell

```bash
# Backend
docker exec -it lyrica-backend-prod sh

# Database
docker exec -it lyrica-postgres-prod psql -U lyrica -d lyrica_prod

# Redis
docker exec -it lyrica-redis-prod redis-cli
```

### Database Backup

```bash
# Export PostgreSQL dump
docker exec lyrica-postgres-prod pg_dump -U lyrica lyrica_prod > backup.sql

# Import backup
docker exec -i lyrica-postgres-prod psql -U lyrica lyrica_prod < backup.sql
```

---

## Troubleshooting

### Service Won't Start

**Check logs:**
```bash
docker-compose -f docker-compose.prod.yml logs backend
```

**Common issues:**
1. Port already in use → Change port in `.env.prod`
2. Missing environment variables → Check `.env.prod`
3. Database not ready → Wait for health check

**Force recreate:**
```bash
docker-compose -f docker-compose.prod.yml up -d --force-recreate backend
```

### Database Connection Issues

**Verify PostgreSQL is running:**
```bash
docker exec lyrica-postgres-prod pg_isready -U lyrica
```

**Check connection from backend:**
```bash
docker exec lyrica-backend-prod python -c "
from app.db.session import engine
import asyncio
asyncio.run(engine.connect())
print('✅ Database connected!')
"
```

### Out of Memory

**Check container memory:**
```bash
docker stats --no-stream
```

**Increase limits in `docker-compose.prod.yml`:**
```yaml
deploy:
  resources:
    limits:
      memory: 8G  # Increase from 4G
```

### Network Issues

**Inspect network:**
```bash
docker network inspect lyrica-network
```

**Recreate network:**
```bash
docker-compose -f docker-compose.prod.yml down
docker network rm lyrica-network
docker-compose -f docker-compose.prod.yml up -d
```

---

## Security

### Best Practices

1. **Never commit `.env.prod`**
   ```bash
   echo ".env.prod" >> .gitignore
   ```

2. **Use strong passwords**
   ```bash
   # Generate secure password
   openssl rand -base64 32
   ```

3. **Limit exposed ports**
   ```yaml
   # Only expose what's needed
   ports:
     - "127.0.0.1:5432:5432"  # Only localhost can access
   ```

4. **Run as non-root**
   - Already configured in Dockerfiles
   - Backend runs as `lyrica` user
   - Frontend runs as `nextjs` user

5. **Use secrets management**
   ```bash
   # Docker secrets (Swarm)
   docker secret create postgres_password ./password.txt
   ```

### SSL/TLS Configuration

**Use reverse proxy (NGINX) for HTTPS:**

```yaml
# Add to docker-compose.prod.yml
nginx:
  image: nginx:alpine
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf:ro
    - ./ssl:/etc/nginx/ssl:ro
  ports:
    - "80:80"
    - "443:443"
```

**Example `nginx.conf`:**
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location /api {
        proxy_pass http://backend:8000;
    }
    
    location / {
        proxy_pass http://web:3000;
    }
}
```

### Rate Limiting

Configure in `.env.prod`:
```bash
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_DAY=1000
```

---

## Production Checklist

Before deploying to production:

- [ ] Set strong passwords in `.env.prod`
- [ ] Configure `CORS_ORIGINS` with actual domains
- [ ] Set `NEXT_PUBLIC_API_URL` to production URL
- [ ] Enable SSL/TLS with reverse proxy
- [ ] Configure database backups
- [ ] Set up monitoring (Sentry, Datadog, etc.)
- [ ] Test all health endpoints
- [ ] Run database migrations
- [ ] Seed initial data (if needed)
- [ ] Configure log aggregation
- [ ] Set up alerting
- [ ] Document rollback procedure

---

## Quick Commands Reference

```bash
# Build
pnpm docker:build

# Start
pnpm docker:up

# Stop
pnpm docker:down

# Logs
pnpm docker:logs

# Restart
pnpm docker:restart

# Health check
curl http://localhost:8000/api/v1/health

# Database backup
docker exec lyrica-postgres-prod pg_dump -U lyrica > backup.sql

# View resource usage
docker stats

# Clean up (⚠️ removes volumes)
docker-compose -f docker-compose.prod.yml down -v
docker system prune -a --volumes
```

---

## Support

For issues or questions:
- Check logs: `pnpm docker:logs`
- GitHub Issues: [lyrica/issues](https://github.com/yourusername/lyrica/issues)
- Documentation: `/docs/`

---

**Last Updated:** November 2025
**Docker Version:** 20.10+
**Docker Compose Version:** 2.0+
