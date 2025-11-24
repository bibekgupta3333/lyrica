# Database Design
## Lyrica - Agentic Song Lyrics Generator

---

## Table of Contents
1. [Overview](#overview)
2. [Database Architecture](#database-architecture)
3. [Schema Design](#schema-design)
4. [Entity Relationship Diagram](#entity-relationship-diagram)
5. [Vector Store Design](#vector-store-design)
6. [Indexing Strategy](#indexing-strategy)
7. [Data Migration Strategy](#data-migration-strategy)
8. [Backup & Recovery](#backup--recovery)

---

## Overview

Lyrica uses a polyglot persistence approach with multiple database systems optimized for different use cases:

- **PostgreSQL**: Primary relational database for structured data
- **ChromaDB**: Vector database for semantic search and RAG
- **Redis**: In-memory cache for sessions and API responses

---

## Database Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Application Layer                            │
│                      (FastAPI Backend)                           │
└────────┬───────────────────────────┬──────────────┬─────────────┘
         │                           │              │
         │                           │              │
    ┌────▼──────┐            ┌──────▼──────┐   ┌──▼──────┐
    │PostgreSQL │            │  ChromaDB   │   │  Redis  │
    │   (RDS)   │            │ (Vector DB) │   │ (Cache) │
    │           │            │             │   │         │
    │ • Users   │            │ • Embeddings│   │ • Session│
    │ • Lyrics  │            │ • Metadata  │   │ • Cache │
    │ • History │            │ • Indexes   │   │ • Limits│
    └───────────┘            └─────────────┘   └─────────┘
```

---

## Schema Design

### PostgreSQL Schema

#### 1. Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT username_format CHECK (username ~* '^[A-Za-z0-9_-]{3,}$')
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_created_at ON users(created_at);
```

#### 2. User Preferences Table
```sql
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    preferred_genres TEXT[] DEFAULT '{}',
    preferred_moods TEXT[] DEFAULT '{}',
    default_structure JSONB DEFAULT '{}',
    language VARCHAR(10) DEFAULT 'en',
    theme VARCHAR(20) DEFAULT 'light',
    notifications_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT one_preference_per_user UNIQUE(user_id)
);

-- Indexes
CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);
```

#### 3. Lyrics Table
```sql
CREATE TABLE lyrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    content TEXT NOT NULL,
    structure JSONB NOT NULL,
    
    -- Metadata
    genre VARCHAR(100),
    mood VARCHAR(100),
    theme VARCHAR(255),
    language VARCHAR(10) DEFAULT 'en',
    
    -- Generation metadata
    prompt TEXT,
    generation_params JSONB DEFAULT '{}',
    model_used VARCHAR(100),
    generation_time_seconds DECIMAL(10, 2),
    
    -- Quality metrics
    quality_score DECIMAL(3, 2),
    rhyme_score DECIMAL(3, 2),
    creativity_score DECIMAL(3, 2),
    coherence_score DECIMAL(3, 2),
    
    -- Status
    status VARCHAR(50) DEFAULT 'draft',
    is_public BOOLEAN DEFAULT FALSE,
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    CONSTRAINT valid_status CHECK (status IN ('draft', 'completed', 'published', 'archived')),
    CONSTRAINT valid_quality_score CHECK (quality_score >= 0 AND quality_score <= 1),
    CONSTRAINT valid_rhyme_score CHECK (rhyme_score >= 0 AND rhyme_score <= 1),
    CONSTRAINT valid_creativity_score CHECK (creativity_score >= 0 AND creativity_score <= 1),
    CONSTRAINT valid_coherence_score CHECK (coherence_score >= 0 AND coherence_score <= 1)
);

-- Indexes
CREATE INDEX idx_lyrics_user_id ON lyrics(user_id);
CREATE INDEX idx_lyrics_created_at ON lyrics(created_at DESC);
CREATE INDEX idx_lyrics_genre ON lyrics(genre);
CREATE INDEX idx_lyrics_mood ON lyrics(mood);
CREATE INDEX idx_lyrics_status ON lyrics(status);
CREATE INDEX idx_lyrics_is_public ON lyrics(is_public) WHERE is_public = TRUE;
CREATE INDEX idx_lyrics_quality_score ON lyrics(quality_score DESC) WHERE quality_score IS NOT NULL;

-- Full-text search index
CREATE INDEX idx_lyrics_content_search ON lyrics USING gin(to_tsvector('english', content));
CREATE INDEX idx_lyrics_title_search ON lyrics USING gin(to_tsvector('english', title));
```

#### 4. Lyrics Sections Table
```sql
CREATE TABLE lyrics_sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lyrics_id UUID NOT NULL REFERENCES lyrics(id) ON DELETE CASCADE,
    section_type VARCHAR(50) NOT NULL,
    section_order INTEGER NOT NULL,
    content TEXT NOT NULL,
    rhyme_scheme VARCHAR(50),
    line_count INTEGER,
    
    -- Metadata
    generation_attempts INTEGER DEFAULT 1,
    refinement_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_section_type CHECK (section_type IN ('intro', 'verse', 'chorus', 'bridge', 'outro', 'pre-chorus', 'post-chorus')),
    CONSTRAINT unique_section_order UNIQUE(lyrics_id, section_order)
);

-- Indexes
CREATE INDEX idx_lyrics_sections_lyrics_id ON lyrics_sections(lyrics_id);
CREATE INDEX idx_lyrics_sections_order ON lyrics_sections(lyrics_id, section_order);
```

#### 5. Generation History Table
```sql
CREATE TABLE generation_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lyrics_id UUID REFERENCES lyrics(id) ON DELETE SET NULL,
    
    -- Input parameters
    input_prompt TEXT NOT NULL,
    genre VARCHAR(100),
    mood VARCHAR(100),
    theme VARCHAR(255),
    custom_structure JSONB,
    
    -- Process metadata
    status VARCHAR(50) DEFAULT 'pending',
    agent_steps JSONB DEFAULT '[]',
    iterations INTEGER DEFAULT 0,
    error_message TEXT,
    
    -- Performance metrics
    total_time_seconds DECIMAL(10, 2),
    llm_time_seconds DECIMAL(10, 2),
    retrieval_time_seconds DECIMAL(10, 2),
    
    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    CONSTRAINT valid_history_status CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled'))
);

-- Indexes
CREATE INDEX idx_generation_history_user_id ON generation_history(user_id);
CREATE INDEX idx_generation_history_started_at ON generation_history(started_at DESC);
CREATE INDEX idx_generation_history_status ON generation_history(status);
CREATE INDEX idx_generation_history_lyrics_id ON generation_history(lyrics_id);
```

#### 6. Agent Logs Table
```sql
CREATE TABLE agent_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    generation_history_id UUID NOT NULL REFERENCES generation_history(id) ON DELETE CASCADE,
    agent_name VARCHAR(100) NOT NULL,
    step_number INTEGER NOT NULL,
    
    -- Input/Output
    input_state JSONB,
    output_state JSONB,
    
    -- Metadata
    execution_time_seconds DECIMAL(10, 2),
    tokens_used INTEGER,
    model_used VARCHAR(100),
    
    -- Status
    status VARCHAR(50) DEFAULT 'success',
    error_message TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_agent_status CHECK (status IN ('success', 'failed', 'skipped'))
);

-- Indexes
CREATE INDEX idx_agent_logs_generation_history_id ON agent_logs(generation_history_id);
CREATE INDEX idx_agent_logs_agent_name ON agent_logs(agent_name);
CREATE INDEX idx_agent_logs_created_at ON agent_logs(created_at);
```

#### 7. User Feedback Table
```sql
CREATE TABLE user_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lyrics_id UUID NOT NULL REFERENCES lyrics(id) ON DELETE CASCADE,
    
    -- Ratings (1-5)
    overall_rating INTEGER,
    creativity_rating INTEGER,
    relevance_rating INTEGER,
    quality_rating INTEGER,
    
    -- Feedback
    comment TEXT,
    tags TEXT[] DEFAULT '{}',
    
    -- Actions
    is_liked BOOLEAN DEFAULT FALSE,
    is_saved BOOLEAN DEFAULT FALSE,
    is_shared BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_overall_rating CHECK (overall_rating >= 1 AND overall_rating <= 5),
    CONSTRAINT valid_creativity_rating CHECK (creativity_rating >= 1 AND creativity_rating <= 5),
    CONSTRAINT valid_relevance_rating CHECK (relevance_rating >= 1 AND relevance_rating <= 5),
    CONSTRAINT valid_quality_rating CHECK (quality_rating >= 1 AND quality_rating <= 5),
    CONSTRAINT one_feedback_per_user_lyrics UNIQUE(user_id, lyrics_id)
);

-- Indexes
CREATE INDEX idx_user_feedback_user_id ON user_feedback(user_id);
CREATE INDEX idx_user_feedback_lyrics_id ON user_feedback(lyrics_id);
CREATE INDEX idx_user_feedback_overall_rating ON user_feedback(overall_rating);
CREATE INDEX idx_user_feedback_created_at ON user_feedback(created_at);
```

#### 8. API Keys Table
```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    
    -- Permissions
    scopes TEXT[] DEFAULT '{}',
    
    -- Rate limiting
    rate_limit_per_minute INTEGER DEFAULT 60,
    rate_limit_per_day INTEGER DEFAULT 1000,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMP WITH TIME ZONE,
    usage_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    CONSTRAINT valid_scopes CHECK (scopes <@ ARRAY['read', 'write', 'generate', 'admin'])
);

-- Indexes
CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_key_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_is_active ON api_keys(is_active) WHERE is_active = TRUE;
```

#### 9. Documents Table (for RAG)
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255),
    content TEXT NOT NULL,
    
    -- Metadata
    genre VARCHAR(100),
    mood VARCHAR(100),
    artist VARCHAR(255),
    album VARCHAR(255),
    year INTEGER,
    language VARCHAR(10) DEFAULT 'en',
    
    -- Categorization
    tags TEXT[] DEFAULT '{}',
    custom_metadata JSONB DEFAULT '{}',
    
    -- Vector store reference
    chromadb_id VARCHAR(255) UNIQUE,
    
    -- Status
    is_indexed BOOLEAN DEFAULT FALSE,
    indexed_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_documents_genre ON documents(genre);
CREATE INDEX idx_documents_mood ON documents(mood);
CREATE INDEX idx_documents_is_indexed ON documents(is_indexed);
CREATE INDEX idx_documents_tags ON documents USING gin(tags);
CREATE INDEX idx_documents_chromadb_id ON documents(chromadb_id);
```

#### 10. Usage Statistics Table
```sql
CREATE TABLE usage_statistics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Metrics
    endpoint VARCHAR(255),
    method VARCHAR(10),
    status_code INTEGER,
    response_time_ms INTEGER,
    
    -- Request details
    request_size_bytes INTEGER,
    response_size_bytes INTEGER,
    user_agent TEXT,
    ip_address INET,
    
    -- Timestamps
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes (partitioned by date)
CREATE INDEX idx_usage_statistics_user_id ON usage_statistics(user_id);
CREATE INDEX idx_usage_statistics_timestamp ON usage_statistics(timestamp DESC);
CREATE INDEX idx_usage_statistics_endpoint ON usage_statistics(endpoint);
```

---

## Entity Relationship Diagram

```
┌──────────────┐
│    users     │
│──────────────│
│ id (PK)      │
│ email        │◀──────┐
│ username     │       │
│ password_hash│       │
│ created_at   │       │
└──────────────┘       │
       │               │
       │ 1             │
       │               │
       │ n             │
       │               │
┌──────▼──────────┐    │
│ user_preferences│    │
│─────────────────│    │
│ id (PK)         │    │
│ user_id (FK)    │    │
│ preferred_genres│    │
│ default_structure│   │
└─────────────────┘    │
                       │
       ┌───────────────┘
       │
       │ 1
       │
       │ n
       │
┌──────▼──────┐         ┌──────────────────┐
│   lyrics    │         │ generation_history│
│─────────────│         │──────────────────│
│ id (PK)     │◀───┐    │ id (PK)          │
│ user_id (FK)│    │    │ user_id (FK)     │
│ title       │    │    │ lyrics_id (FK)   │
│ content     │    │    │ input_prompt     │
│ genre       │    │    │ status           │
│ mood        │    │    │ agent_steps      │
│ structure   │    │    │ started_at       │
│ quality_score│   │    └──────────────────┘
└──────┬──────┘    │              │
       │           │              │ 1
       │ 1         │              │
       │           │              │ n
       │ n         │              │
       │           │    ┌─────────▼────────┐
┌──────▼──────────┐│    │   agent_logs     │
│lyrics_sections  ││    │──────────────────│
│─────────────────││    │ id (PK)          │
│ id (PK)         ││    │ generation_hist…│
│ lyrics_id (FK)  ││    │ agent_name       │
│ section_type    ││    │ step_number      │
│ section_order   ││    │ input_state      │
│ content         ││    │ output_state     │
└─────────────────┘│    └──────────────────┘
                   │
                   │ 1
                   │
                   │ n
                   │
           ┌───────┴─────────┐
           │  user_feedback  │
           │─────────────────│
           │ id (PK)         │
           │ user_id (FK)    │
           │ lyrics_id (FK)  │
           │ overall_rating  │
           │ comment         │
           │ is_liked        │
           └─────────────────┘


┌──────────────┐
│  documents   │
│──────────────│
│ id (PK)      │
│ title        │
│ content      │
│ genre        │
│ mood         │
│ chromadb_id  │──────▶ [ChromaDB Vector Store]
│ is_indexed   │
└──────────────┘


┌──────────────┐
│  api_keys    │
│──────────────│
│ id (PK)      │
│ user_id (FK) │──────▶ users.id
│ key_hash     │
│ scopes       │
│ is_active    │
└──────────────┘
```

---

## Vector Store Design (ChromaDB)

### Collection Structure

```python
# ChromaDB Collection Schema
{
    "name": "lyrics_embeddings",
    "metadata": {
        "description": "Song lyrics embeddings for RAG",
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "embedding_dimension": 384
    }
}
```

### Document Structure

```python
# Example document in ChromaDB
{
    "id": "doc_uuid_12345",
    "embedding": [0.123, -0.456, ...],  # 384-dimensional vector
    "document": "Full lyrics text...",
    "metadata": {
        "postgres_id": "uuid_from_postgres",
        "genre": "pop",
        "mood": "happy",
        "theme": "love",
        "artist": "Artist Name",
        "year": 2023,
        "language": "en",
        "chunk_index": 0,
        "total_chunks": 3,
        "word_count": 250,
        "avg_rhyme_density": 0.75,
        "indexed_at": "2024-01-01T00:00:00Z"
    }
}
```

### Chunking Strategy

```python
# Chunking configuration
CHUNK_CONFIG = {
    "chunk_size": 512,  # tokens
    "chunk_overlap": 50,  # tokens
    "separator": "\n\n",  # Split by double newline (verses/sections)
    "keep_separator": True
}

# Example chunking
"""
Original lyrics (1500 words):
Verse 1...
Chorus...
Verse 2...
Bridge...

Chunked into:
- Chunk 0: Verse 1 + Chorus (512 tokens)
- Chunk 1: Chorus + Verse 2 (512 tokens, 50 overlap)
- Chunk 2: Verse 2 + Bridge (512 tokens, 50 overlap)
"""
```

### Indexing Strategy

```python
# HNSW (Hierarchical Navigable Small World) Index
index_params = {
    "space": "cosine",  # Similarity metric
    "ef_construction": 200,  # Quality of index construction
    "M": 16  # Number of connections per layer
}

# Search parameters
search_params = {
    "k": 10,  # Number of results
    "ef": 50,  # Search quality
    "filter": {
        "genre": "pop",
        "mood": "happy"
    }
}
```

---

## Redis Cache Design

### Key Patterns

```python
# Cache key patterns
REDIS_KEYS = {
    # Session management
    "session:{user_id}": "User session data",
    "refresh_token:{token_hash}": "Refresh token storage",
    
    # API response cache
    "api:lyrics:{lyrics_id}": "Cached lyrics response",
    "api:search:{query_hash}": "Cached search results",
    "api:history:{user_id}:{page}": "Cached history page",
    
    # Rate limiting
    "rate_limit:user:{user_id}:{minute}": "Per-minute rate limit counter",
    "rate_limit:ip:{ip_address}:{minute}": "IP-based rate limit",
    "rate_limit:api_key:{key_hash}:{minute}": "API key rate limit",
    
    # Generation state
    "generation:state:{generation_id}": "Agent state during generation",
    "generation:progress:{generation_id}": "Generation progress",
    
    # Embeddings cache
    "embedding:{text_hash}": "Cached text embedding",
    "vector_search:{query_hash}": "Cached vector search results",
    
    # Statistics
    "stats:user:{user_id}:{date}": "Daily user statistics",
    "stats:global:{date}": "Global daily statistics"
}
```

### Data Structures

```python
# Redis data structures used

# 1. Strings (with TTL)
redis.setex("api:lyrics:123", 300, json_data)  # 5 min TTL

# 2. Hashes (for structured data)
redis.hset("session:user_123", {
    "user_id": "123",
    "email": "user@example.com",
    "login_at": "2024-01-01T00:00:00Z"
})

# 3. Lists (for queues)
redis.lpush("generation_queue", generation_id)

# 4. Sets (for unique collections)
redis.sadd("user:123:liked_lyrics", lyrics_id)

# 5. Sorted Sets (for rankings/leaderboards)
redis.zadd("popular_lyrics", {lyrics_id: view_count})

# 6. Counters (for rate limiting)
redis.incr("rate_limit:user:123:2024-01-01T12:00")
redis.expire("rate_limit:user:123:2024-01-01T12:00", 60)
```

### TTL Strategy

```python
# Time-to-live for different data types
TTL_CONFIG = {
    "session": 3600 * 24 * 7,  # 7 days
    "api_response": 300,  # 5 minutes
    "search_results": 600,  # 10 minutes
    "rate_limit": 60,  # 1 minute
    "generation_state": 3600,  # 1 hour
    "embedding_cache": 3600 * 24,  # 1 day
    "statistics": 3600 * 24 * 30  # 30 days
}
```

---

## Indexing Strategy

### PostgreSQL Indexes

```sql
-- B-tree indexes (default)
CREATE INDEX idx_lyrics_created_at ON lyrics(created_at DESC);
CREATE INDEX idx_lyrics_user_id ON lyrics(user_id);

-- Partial indexes (for specific conditions)
CREATE INDEX idx_lyrics_public 
ON lyrics(created_at DESC) 
WHERE is_public = TRUE AND status = 'published';

-- Composite indexes (for multi-column queries)
CREATE INDEX idx_lyrics_user_genre_created 
ON lyrics(user_id, genre, created_at DESC);

-- GIN indexes (for full-text search)
CREATE INDEX idx_lyrics_content_search 
ON lyrics 
USING gin(to_tsvector('english', content));

-- GIN indexes (for array columns)
CREATE INDEX idx_user_preferences_genres 
ON user_preferences 
USING gin(preferred_genres);

-- JSONB indexes
CREATE INDEX idx_lyrics_structure 
ON lyrics 
USING gin(structure);

-- Covering indexes (include additional columns)
CREATE INDEX idx_lyrics_user_id_covering 
ON lyrics(user_id) 
INCLUDE (title, genre, created_at);
```

### ChromaDB Indexes

```python
# HNSW index configuration
chromadb_index = {
    "index_type": "hnsw",
    "space": "cosine",
    "parameters": {
        "M": 16,  # Connections per element
        "ef_construction": 200,  # Build quality
        "ef_search": 50  # Search quality
    }
}

# Metadata indexes (for filtering)
metadata_indexes = [
    "genre",
    "mood",
    "year",
    "language"
]
```

---

## Data Migration Strategy

### Alembic Migration Structure

```python
# alembic/versions/001_initial_schema.py
"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), 
                  server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    
    # Create indexes
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_username', 'users', ['username'])
    
    # ... more tables

def downgrade():
    op.drop_table('users')
```

### Migration Commands

```bash
# Create a new migration
alembic revision --autogenerate -m "add_feedback_table"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

### Zero-Downtime Migration Strategy

```python
# Step 1: Add new column (nullable)
def upgrade():
    op.add_column('lyrics', 
        sa.Column('quality_score_v2', sa.Numeric(3, 2), nullable=True)
    )

# Step 2: Backfill data
def upgrade():
    connection = op.get_bind()
    connection.execute("""
        UPDATE lyrics 
        SET quality_score_v2 = quality_score 
        WHERE quality_score_v2 IS NULL
    """)

# Step 3: Make column not nullable
def upgrade():
    op.alter_column('lyrics', 'quality_score_v2', nullable=False)

# Step 4: Drop old column
def upgrade():
    op.drop_column('lyrics', 'quality_score')

# Step 5: Rename new column
def upgrade():
    op.alter_column('lyrics', 'quality_score_v2', 
                    new_column_name='quality_score')
```

---

## Backup & Recovery

### Backup Strategy

#### PostgreSQL Backups

```bash
# Automated daily backups
#!/bin/bash
# backup_postgres.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgres"
DB_NAME="lyrica_production"

# Full database backup
pg_dump -U postgres -h localhost $DB_NAME \
  | gzip > $BACKUP_DIR/lyrica_$DATE.sql.gz

# Upload to S3
aws s3 cp $BACKUP_DIR/lyrica_$DATE.sql.gz \
  s3://lyrica-backups/postgres/

# Retain only last 30 days locally
find $BACKUP_DIR -type f -mtime +30 -delete
```

**Backup Schedule:**
- Full backup: Daily at 2:00 AM UTC
- Incremental backup: Every 6 hours
- WAL archiving: Continuous
- Retention: 30 days local, 90 days S3

#### ChromaDB Backups

```python
# backup_chromadb.py
import chromadb
import tarfile
from datetime import datetime

def backup_chromadb():
    client = chromadb.PersistentClient(path="/data/chromadb")
    backup_path = f"/backups/chromadb_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
    
    # Create tar archive
    with tarfile.open(backup_path, "w:gz") as tar:
        tar.add("/data/chromadb", arcname="chromadb")
    
    # Upload to S3
    upload_to_s3(backup_path, "s3://lyrica-backups/chromadb/")
    
    return backup_path
```

### Recovery Procedures

#### PostgreSQL Recovery

```bash
# Restore from backup
gunzip < lyrica_20240101_020000.sql.gz | \
  psql -U postgres -h localhost lyrica_production

# Point-in-time recovery (PITR)
# 1. Restore base backup
# 2. Configure recovery.conf
# 3. Restore WAL files
# 4. Specify recovery target time
```

#### ChromaDB Recovery

```bash
# Extract backup
tar -xzf chromadb_20240101_020000.tar.gz -C /data/

# Restart ChromaDB service
kubectl rollout restart deployment/chromadb
```

### Disaster Recovery Plan

```
┌─────────────────────────────────────────────────────┐
│          Disaster Recovery Scenarios                 │
├─────────────────────────────────────────────────────┤
│                                                      │
│  RTO (Recovery Time Objective): 4 hours             │
│  RPO (Recovery Point Objective): 15 minutes         │
│                                                      │
│  Scenario 1: Database Corruption                    │
│  └─▶ Restore from latest backup (30 min)           │
│                                                      │
│  Scenario 2: Accidental Data Deletion               │
│  └─▶ Point-in-time recovery (1 hour)               │
│                                                      │
│  Scenario 3: Complete AZ Failure                    │
│  └─▶ Failover to standby in another AZ (15 min)    │
│                                                      │
│  Scenario 4: Regional Disaster                      │
│  └─▶ Restore from S3 to new region (4 hours)       │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## Performance Optimization

### Query Optimization

```sql
-- Use EXPLAIN ANALYZE to optimize queries
EXPLAIN ANALYZE
SELECT l.id, l.title, l.genre, u.username
FROM lyrics l
JOIN users u ON l.user_id = u.id
WHERE l.genre = 'pop'
  AND l.quality_score > 0.8
  AND l.created_at > NOW() - INTERVAL '30 days'
ORDER BY l.created_at DESC
LIMIT 20;

-- Result: Using appropriate indexes
-- Index Scan on idx_lyrics_genre_quality_created
-- Execution time: 5.234 ms
```

### Connection Pooling

```python
# SQLAlchemy connection pool configuration
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,  # Minimum connections
    max_overflow=30,  # Maximum additional connections
    pool_timeout=30,  # Seconds to wait for connection
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True  # Verify connections before use
)
```

### Partitioning Strategy

```sql
-- Partition large tables by date
CREATE TABLE usage_statistics (
    id UUID,
    user_id UUID,
    timestamp TIMESTAMP WITH TIME ZONE,
    -- ... other columns
) PARTITION BY RANGE (timestamp);

-- Create partitions
CREATE TABLE usage_statistics_2024_01 
PARTITION OF usage_statistics
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE usage_statistics_2024_02 
PARTITION OF usage_statistics
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Automated partition management
CREATE OR REPLACE FUNCTION create_monthly_partition()
RETURNS void AS $$
DECLARE
    start_date date;
    end_date date;
    partition_name text;
BEGIN
    start_date := date_trunc('month', CURRENT_DATE + interval '1 month');
    end_date := start_date + interval '1 month';
    partition_name := 'usage_statistics_' || to_char(start_date, 'YYYY_MM');
    
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF usage_statistics
         FOR VALUES FROM (%L) TO (%L)',
        partition_name, start_date, end_date
    );
END;
$$ LANGUAGE plpgsql;
```

---

## Monitoring & Maintenance

### Database Monitoring

```sql
-- Active connections
SELECT count(*) FROM pg_stat_activity WHERE state = 'active';

-- Long-running queries
SELECT pid, now() - query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active' AND now() - query_start > interval '5 minutes';

-- Table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

### Maintenance Tasks

```bash
# Vacuum and analyze (automated)
# Run daily at 3:00 AM
0 3 * * * psql -U postgres -d lyrica_production -c "VACUUM ANALYZE;"

# Reindex (monthly)
# Run first Sunday of month
0 4 1-7 * 0 psql -U postgres -d lyrica_production -c "REINDEX DATABASE lyrica_production;"

# Update statistics
# Run after large data imports
psql -U postgres -d lyrica_production -c "ANALYZE;"
```

---

## Security Measures

### Data Encryption

```sql
-- Enable pgcrypto extension
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt sensitive data
CREATE TABLE user_secrets (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    encrypted_data BYTEA,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert encrypted data
INSERT INTO user_secrets (user_id, encrypted_data)
VALUES (
    'user_uuid',
    pgp_sym_encrypt('sensitive_data', 'encryption_key')
);

-- Query encrypted data
SELECT pgp_sym_decrypt(encrypted_data, 'encryption_key')
FROM user_secrets
WHERE user_id = 'user_uuid';
```

### Row-Level Security

```sql
-- Enable RLS
ALTER TABLE lyrics ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY user_own_lyrics ON lyrics
    FOR ALL
    USING (user_id = current_user_id())
    WITH CHECK (user_id = current_user_id());

CREATE POLICY public_lyrics_readable ON lyrics
    FOR SELECT
    USING (is_public = TRUE);
```

### Audit Logging

```sql
-- Create audit log table
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name VARCHAR(100),
    operation VARCHAR(10),
    old_data JSONB,
    new_data JSONB,
    user_id UUID,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create audit trigger
CREATE OR REPLACE FUNCTION audit_trigger_func()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (table_name, operation, old_data, new_data, user_id)
    VALUES (
        TG_TABLE_NAME,
        TG_OP,
        row_to_json(OLD),
        row_to_json(NEW),
        current_setting('app.current_user_id', true)::UUID
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger
CREATE TRIGGER audit_lyrics
AFTER INSERT OR UPDATE OR DELETE ON lyrics
FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();
```

---

## Conclusion

This database design provides a scalable, performant, and secure foundation for the Lyrica lyrics generator. The combination of PostgreSQL for structured data, ChromaDB for vector search, and Redis for caching creates a robust data layer that supports the application's requirements.

Key features:
- ✅ Normalized schema with proper relationships
- ✅ Comprehensive indexing strategy
- ✅ Vector store integration for RAG
- ✅ Efficient caching with Redis
- ✅ Backup and disaster recovery
- ✅ Security with encryption and audit logging
- ✅ Performance optimization techniques

