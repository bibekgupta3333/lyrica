# Database Setup Guide

This guide explains how to set up and manage the database for Lyrica Backend.

## Database Models

The application uses the following database models:

### User Management
- **User**: User accounts and authentication
  - Authentication: email, username, password
  - Profile: full_name
  - Status: is_active, is_verified, is_superuser

### Lyrics
- **Lyrics**: Generated song lyrics
  - Content: title, content, structure
  - Metadata: genre, mood, theme, language
  - Metrics: quality_score, rhyme_score, creativity_score
  - Status: status, is_public, view_count, like_count

- **LyricsSection**: Individual sections (verse, chorus, etc.)
  - Content: section_type, content, rhyme_scheme
  - Metadata: generation_attempts, refinement_count

### Generation Tracking
- **GenerationHistory**: Track lyrics generation process
  - Input: prompt, genre, mood, theme
  - Process: status, agent_steps, iterations
  - Metrics: total_time, llm_time, retrieval_time

- **AgentLog**: Detailed logs for each agent step
  - Agent info: agent_name, step_number
  - State: input_state, output_state
  - Metrics: execution_time, tokens_used

### Feedback & Documents
- **UserFeedback**: User ratings and feedback
  - Ratings: overall, creativity, relevance, quality
  - Actions: is_liked, is_saved, is_shared

- **Document**: RAG system documents
  - Content: title, content
  - Metadata: genre, mood, artist, album
  - Vector store: chromadb_id, is_indexed

## Setup Steps

### 1. Start PostgreSQL

Using Docker Compose:

```bash
docker-compose up -d postgres
```

Or manually:
```bash
docker run -d \
  --name lyrica-postgres \
  -e POSTGRES_DB=lyrica_dev \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:15-alpine
```

### 2. Create Initial Migration

```bash
# Create migration from models
./scripts/create_migration.sh "initial_schema"

# Or manually:
alembic revision --autogenerate -m "initial schema"
```

### 3. Apply Migrations

```bash
# Apply all migrations
alembic upgrade head

# Check current version
alembic current

# View migration history
alembic history
```

### 4. Seed Database (Optional)

```bash
# Create sample data for development
python scripts/seed_db.py
```

This creates:
- 1 admin user: `admin@lyrica.com` / `admin123`
- 5 test users: `user1@example.com` / `password123`, etc.

## Database Management

### Create New Migration

When you modify models:

```bash
# Auto-generate migration
./scripts/create_migration.sh "add_new_field"

# Review the generated migration file in alembic/versions/
# Edit if necessary

# Apply the migration
alembic upgrade head
```

### Rollback Migration

```bash
# Rollback one version
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>

# Rollback all
alembic downgrade base
```

### View Database Status

```bash
# Check current migration version
alembic current

# View migration history
alembic history --verbose

# Show pending migrations
alembic heads
```

## Database Connection

The application uses SQLAlchemy with async support:

```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db

# In endpoint
async def some_endpoint(db: AsyncSession = Depends(get_db)):
    # Use database session
    result = await db.execute(select(User))
    users = result.scalars().all()
```

## CRUD Operations

Use the provided CRUD classes:

```python
from app.crud.user import user as user_crud
from app.schemas.user import UserCreate

# Create user
user_in = UserCreate(
    email="test@example.com",
    username="testuser",
    password="password123"
)
new_user = await user_crud.create(db, obj_in=user_in)

# Get user by ID
user = await user_crud.get(db, id=user_id)

# Get user by email
user = await user_crud.get_by_email(db, email="test@example.com")

# Update user
updated_user = await user_crud.update(
    db,
    db_obj=user,
    obj_in={"full_name": "New Name"}
)

# Delete user
await user_crud.delete(db, id=user_id)
```

## Common Tasks

### Reset Database

```bash
# Drop all tables
alembic downgrade base

# Recreate tables
alembic upgrade head

# Seed data
python scripts/seed_db.py
```

### Initialize Fresh Database

```bash
# Initialize database (creates tables)
python scripts/init_db.py

# Or create first migration
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

### Backup Database

```bash
# Using Docker
docker exec lyrica-postgres pg_dump -U postgres lyrica_dev > backup.sql

# Restore
docker exec -i lyrica-postgres psql -U postgres lyrica_dev < backup.sql
```

## Database Schema Visualization

```
users
├── id (UUID, PK)
├── email (String, Unique)
├── username (String, Unique)
├── password_hash (String)
├── full_name (String, Optional)
├── is_active (Boolean)
├── is_verified (Boolean)
├── is_superuser (Boolean)
└── timestamps

lyrics
├── id (UUID, PK)
├── user_id (UUID, FK -> users)
├── title (String, Optional)
├── content (Text)
├── structure (JSON)
├── genre, mood, theme (String)
├── generation_params (JSON)
├── quality_score, rhyme_score, etc. (Numeric)
├── status, is_public (String, Boolean)
└── timestamps

lyrics_sections
├── id (UUID, PK)
├── lyrics_id (UUID, FK -> lyrics)
├── section_type, section_order (String, Integer)
├── content (Text)
├── rhyme_scheme (String, Optional)
└── timestamps

generation_history
├── id (UUID, PK)
├── user_id (UUID, FK -> users)
├── lyrics_id (UUID, FK -> lyrics, Optional)
├── input_prompt, genre, mood (String)
├── status, agent_steps (String, JSON)
├── total_time_seconds, etc. (Numeric)
└── timestamps

agent_logs
├── id (UUID, PK)
├── generation_history_id (UUID, FK)
├── agent_name, step_number (String, Integer)
├── input_state, output_state (JSON)
├── execution_time_seconds (Numeric)
└── timestamps

user_feedback
├── id (UUID, PK)
├── user_id (UUID, FK -> users)
├── lyrics_id (UUID, FK -> lyrics)
├── overall_rating, etc. (Integer)
├── comment (Text, Optional)
├── is_liked, is_saved, is_shared (Boolean)
└── timestamps

documents
├── id (UUID, PK)
├── title, content (String, Text)
├── genre, mood, artist (String, Optional)
├── tags (Array[String])
├── chromadb_id (String, Optional)
├── is_indexed (Boolean)
└── timestamps
```

## Troubleshooting

### Connection Error

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check connection string in .env
echo $DATABASE_URL

# Test connection
docker exec -it lyrica-postgres psql -U postgres -d lyrica_dev
```

### Migration Conflicts

```bash
# If you have migration conflicts:
alembic heads  # Should show only one head

# If multiple heads, merge them:
alembic merge -m "merge heads" <rev1> <rev2>
```

### Foreign Key Issues

Make sure to:
1. Apply migrations in order
2. Don't delete tables with foreign key constraints
3. Use `ondelete="CASCADE"` or `ondelete="SET NULL"` in relationships

## Production Considerations

1. **Use RDS**: Use AWS RDS for production PostgreSQL
2. **Backups**: Enable automated backups
3. **Connection Pooling**: Configured in `app/db/session.py`
4. **Migrations**: Always test migrations in staging first
5. **Monitoring**: Use CloudWatch for RDS monitoring
6. **Security**: Use AWS Secrets Manager for credentials

## References

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [FastAPI Database Guide](https://fastapi.tiangolo.com/tutorial/sql-databases/)

