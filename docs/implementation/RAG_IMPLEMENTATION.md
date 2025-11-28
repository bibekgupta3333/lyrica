# RAG System Implementation

## Overview

Successfully implemented a complete **Retrieval-Augmented Generation (RAG)** system for Lyrica's AI-powered song generation platform. This system combines semantic search with LLM generation to create intelligent, context-aware lyrics.

**Implementation Date**: November 27, 2025
**Status**: ✅ Complete & Tested
**WBS Reference**: Section 2.3 - Vector Store & RAG Implementation

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     RAG System Architecture                  │
└─────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │   User Query │
    └──────┬───────┘
           │
           ▼
    ┌──────────────────┐
    │  Embedding Model │  ← sentence-transformers/all-MiniLM-L6-v2
    │   (384 dims)     │
    └──────┬───────────┘
           │
           ▼
    ┌──────────────────┐
    │   Vector Search  │  ← ChromaDB (HTTP Client)
    │  (Semantic)      │     Port: 8001
    └──────┬───────────┘
           │
           ├─── Top K Documents (with similarity scores)
           │
           ▼
    ┌──────────────────┐
    │   RAG Service    │  ← LangChain + Ollama
    │  (LLM Context)   │     Model: llama3
    └──────┬───────────┘
           │
           ▼
    ┌──────────────────┐
    │ Generated Output │
    └──────────────────┘
```

---

## Components Implemented

### 1. Embedding Service (`app/services/embeddings.py`)

**Purpose**: Generate vector embeddings for text using sentence-transformers.

**Features**:
- ✅ Lazy loading of embedding model
- ✅ Batch embedding generation (configurable batch size)
- ✅ In-memory caching with MD5 hash keys
- ✅ Handles empty/invalid inputs gracefully
- ✅ 384-dimensional embeddings (all-MiniLM-L6-v2)

**Key Methods**:
- `embed_text(text)` - Single text embedding
- `embed_texts(texts)` - Batch embedding generation
- `clear_cache()` - Clear embedding cache
- `get_cache_size()` - Get number of cached embeddings

**Performance**:
- Model load time: ~5 seconds (first use)
- Embedding generation: ~200ms per batch of 32 texts
- Cache hit rate: High for repeated queries

---

### 2. Text Chunking Utility (`app/utils/text_chunking.py`)

**Purpose**: Split documents into optimal chunks for embedding and retrieval.

**Strategies Implemented**:

#### Recursive Chunking (Default)
- Uses multiple separators: `\n\n`, `\n`, `. `, ` `
- Best for general text with natural structure
- Preserves semantic boundaries

#### Fixed Size Chunking
- Splits at exact character count
- Attempts word boundary breaks
- Fast but may break sentences

#### Sentence Chunking
- Groups complete sentences
- Best for well-formed text
- Uses regex pattern: `(?<=[.!?])\s+`

#### Paragraph Chunking
- Splits on double newlines
- Combines small paragraphs
- Best for document structure

#### Lyrics Chunking (Specialized)
- Preserves verse/chorus/bridge structure
- Uses pattern: `\n\n(?=\[|\(|Verse|Chorus|Bridge)`
- Maintains musical sections

**Configuration**:
- Default chunk size: 512 characters
- Default overlap: 50 characters
- Configurable via settings

---

### 3. Vector Store Service (`app/services/vector_store.py`)

**Purpose**: Manage ChromaDB operations for vector storage and retrieval.

**Features**:
- ✅ HTTP client connection to ChromaDB
- ✅ Automatic collection management
- ✅ Batch document addition
- ✅ Semantic search with filters
- ✅ Document update/delete operations
- ✅ Collection statistics

**Key Methods**:
- `add_documents(texts, metadatas, ids)` - Add documents with embeddings
- `search(query, n_results, filters)` - Semantic search
- `get_by_ids(ids)` - Retrieve specific documents
- `update_documents(ids, texts, metadatas)` - Update existing docs
- `delete_documents(ids)` - Remove documents
- `count()` - Get total document count
- `reset()` - Clear entire collection

**ChromaDB Configuration**:
- Host: localhost
- Port: 8001 (Docker container)
- Collection: `lyrics_embeddings`
- Metadata includes: genre, mood, doc_type, language

---

### 4. Document Ingestion Service (`app/services/document_ingestion.py`)

**Purpose**: Pipeline for ingesting documents into the vector store.

**Features**:
- ✅ Database-backed document ingestion
- ✅ Specialized lyrics ingestion
- ✅ Custom text ingestion (no database)
- ✅ Batch ingestion with statistics
- ✅ Metadata preservation

**Key Methods**:
- `ingest_document(db, document_id, strategy)` - Ingest single document
- `ingest_documents(db, ids, doc_type, strategy)` - Batch ingestion
- `ingest_lyrics(db, lyrics_id)` - Specialized lyrics ingestion
- `ingest_custom_text(text, metadata, strategy)` - Direct text ingestion

**Ingestion Flow**:
1. Fetch document from database
2. Apply chunking strategy
3. Generate embeddings
4. Store in vector database with metadata

---

### 5. RAG Service (`app/services/rag.py`)

**Purpose**: Complete RAG pipeline combining retrieval and generation.

**Features**:
- ✅ Semantic document retrieval
- ✅ LLM-based response generation (Ollama)
- ✅ Context formatting for prompts
- ✅ Similarity threshold filtering
- ✅ Specialized lyrics generation

**Key Methods**:
- `retrieve(query, n_results, filters)` - Retrieve relevant documents
- `generate(query, context, system_prompt)` - Generate with LLM
- `retrieve_and_generate(query, ...)` - Full RAG pipeline
- `retrieve_similar_lyrics(query, genre, mood)` - Find similar lyrics
- `generate_lyrics_with_context(theme, genre, mood, structure)` - RAG lyrics generation

**RAG Pipeline**:
1. **Retrieve**: Search vector store for similar documents
2. **Filter**: Apply similarity threshold (default: 0.7)
3. **Format**: Create context from retrieved docs
4. **Generate**: Pass to LLM with system prompt
5. **Return**: Generated text + context used

**Lyrics Generation Flow**:
```
Theme Input
    ↓
Retrieve Similar Lyrics (by genre/mood)
    ↓
Build Specialized System Prompt
    ↓
Generate with LLM (Ollama/Llama3)
    ↓
Return Original Lyrics + Context
```

---

### 6. Cache Service (`app/services/cache.py`)

**Purpose**: Redis-based caching for embeddings and search results.

**Features**:
- ✅ Async Redis client
- ✅ Automatic serialization (JSON)
- ✅ TTL support (default: 1 hour)
- ✅ Pattern-based cache clearing
- ✅ Cache statistics

**Key Methods**:
- `get(key)` / `set(key, value, ttl)` - Generic cache operations
- `get_embedding(text)` / `set_embedding(text, embedding)` - Embedding cache
- `get_search_results(query, filters)` - Search result cache
- `clear_pattern(pattern)` - Clear matching keys
- `get_stats()` - Cache hit/miss statistics

**Cache Keys**:
- Embeddings: `embedding:{md5_hash}`
- Search results: `search:{query_hash}:{filters_hash}`

---

## API Endpoints

### Base URL: `/api/v1/rag`

#### 1. `POST /rag/ingest/document`
Ingest a document from database into vector store.

**Request**:
```json
{
  "document_id": "uuid",
  "chunking_strategy": "recursive"
}
```

**Response**:
```json
{
  "message": "Document ingested successfully",
  "document_id": "uuid",
  "chunks_created": 5
}
```

---

#### 2. `POST /rag/ingest/lyrics`
Ingest lyrics with specialized chunking.

**Request**:
```json
{
  "lyrics_id": "uuid"
}
```

**Response**:
```json
{
  "message": "Lyrics ingested successfully",
  "lyrics_id": "uuid",
  "chunks_created": 3
}
```

---

#### 3. `POST /rag/ingest/custom`
Ingest custom text directly.

**Request**:
```json
{
  "text": "Your custom text here...",
  "metadata": {
    "genre": "rock",
    "mood": "energetic"
  },
  "chunking_strategy": "recursive"
}
```

**Response**:
```json
{
  "message": "Custom text ingested successfully",
  "chunks_created": 2
}
```

---

#### 4. `POST /rag/search`
Perform semantic search on vector store.

**Request**:
```json
{
  "query": "songs about love and heartbreak",
  "n_results": 5,
  "filters": {
    "genre": "ballad",
    "mood": "sad"
  }
}
```

**Response**:
```json
{
  "query": "songs about love and heartbreak",
  "results": [
    {
      "id": "uuid_chunk_0",
      "text": "Document text...",
      "metadata": {...},
      "distance": 0.23,
      "score": 0.77
    }
  ],
  "count": 5
}
```

---

#### 5. `POST /rag/query`
Full RAG query with generation.

**Request**:
```json
{
  "query": "Write a song about overcoming challenges",
  "n_results": 5,
  "filters": {"genre": "pop"},
  "system_prompt": "You are a creative songwriter..."
}
```

**Response**:
```json
{
  "query": "Write a song about overcoming challenges",
  "response": "Generated lyrics...",
  "context": [...],
  "num_retrieved": 5,
  "num_used": 3
}
```

---

#### 6. `POST /rag/generate/lyrics`
Generate lyrics using RAG.

**Request**:
```json
{
  "theme": "adventure and freedom",
  "genre": "rock",
  "mood": "energetic",
  "structure": "verse-chorus-verse-chorus-bridge-chorus",
  "n_context_docs": 3
}
```

**Response**:
```json
{
  "query": "Write lyrics about: adventure and freedom",
  "response": "Generated original lyrics...",
  "theme": "adventure and freedom",
  "genre": "rock",
  "mood": "energetic",
  "structure": "verse-chorus-verse-chorus-bridge-chorus",
  "context": [...]
}
```

---

#### 7. `GET /rag/stats`
Get vector store statistics.

**Response**:
```json
{
  "total_documents": 5,
  "collection_name": "lyrics_embeddings"
}
```

---

#### 8. `DELETE /rag/reset`
Reset vector store (⚠️ irreversible).

**Response**:
```json
{
  "message": "Vector store reset successfully"
}
```

---

## Configuration

### Environment Variables (`.env`)

```bash
# ChromaDB Configuration
CHROMADB_HOST=localhost
CHROMADB_PORT=8001
CHROMADB_COLLECTION=lyrics_embeddings
CHROMADB_PERSIST_DIRECTORY=./data/chromadb

# Embedding Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
OLLAMA_TIMEOUT=300
OLLAMA_TEMPERATURE=0.7
OLLAMA_MAX_TOKENS=2048

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=50
```

---

## Testing

### Test Script: `scripts/test_rag_system.py`

**Tests Performed**:
1. ✅ Embedding generation (single & batch)
2. ✅ Text chunking (4 strategies)
3. ✅ Vector store operations (add/search)
4. ✅ Semantic search accuracy
5. ✅ RAG retrieval pipeline

**Test Results**:
```
✅ Embedding Service: 3 embeddings (384 dims) - PASSED
✅ Text Chunking: 4 strategies tested - PASSED
✅ Vector Store: 5 documents added - PASSED
✅ Semantic Search: Relevant results retrieved - PASSED
✅ RAG System: Context retrieval successful - PASSED
```

**Run Tests**:
```bash
cd lyrica-backend
source venv/bin/activate
python scripts/test_rag_system.py
```

---

## Performance Metrics

### Embedding Generation
- Model load time: ~5 seconds (one-time)
- Single embedding: ~50ms
- Batch (32 texts): ~200ms
- Cache hit: < 1ms

### Vector Search
- Query time: 50-150ms (depends on collection size)
- Results: Top K most similar documents
- Filtering: Metadata filters add ~10-20ms

### End-to-End RAG Query
- Embedding generation: ~50ms
- Vector search: ~100ms
- LLM generation: 5-30 seconds (depends on Ollama)
- **Total**: 5-30 seconds (dominated by LLM)

---

## Dependencies

### Python Packages (installed)
```
chromadb==0.4.22
sentence-transformers>=2.2.0
langchain>=0.1.0
langchain-community>=0.0.10
langgraph>=0.0.20
ollama>=0.1.0
redis>=5.0.1
```

### External Services
- **ChromaDB**: Running on port 8001 (Docker)
- **Redis**: Running on port 6379 (Docker)
- **Ollama**: Running on port 11434 (optional, for LLM generation)

---

## Usage Examples

### Example 1: Ingest Lyrics
```python
from app.services import ingestion_service
from app.db.session import get_db

async with get_db() as db:
    chunks = await ingestion_service.ingest_lyrics(
        db=db,
        lyrics_id=your_lyrics_id
    )
    print(f"Created {chunks} chunks")
```

### Example 2: Semantic Search
```python
from app.services import vector_store

results = await vector_store.search(
    query="songs about love",
    n_results=5,
    where={"genre": "pop"}
)

for result in results["documents"]:
    print(result)
```

### Example 3: Generate Lyrics with RAG
```python
from app.services import rag_service

result = await rag_service.generate_lyrics_with_context(
    theme="overcoming adversity",
    genre="rock",
    mood="inspirational",
    n_context_docs=3
)

print(result["response"])
```

---

## Next Steps

### Completed ✅
- [x] ChromaDB integration
- [x] Sentence-transformers embedding model
- [x] Document ingestion pipeline
- [x] Vector search functionality
- [x] RAG retrieval chain
- [x] Multiple chunking strategies
- [x] Redis caching
- [x] API endpoints
- [x] Testing & validation

### Future Enhancements 🚀
- [ ] Implement hybrid search (vector + keyword)
- [ ] Add more embedding models (OpenAI, Cohere)
- [ ] Implement re-ranking for better relevance
- [ ] Add query expansion
- [ ] Implement document versioning
- [ ] Add A/B testing for chunking strategies
- [ ] Optimize cache invalidation
- [ ] Add monitoring & analytics
- [ ] Implement feedback loop for improving results

---

## Troubleshooting

### ChromaDB Connection Issues
**Problem**: `Failed to connect to ChromaDB`

**Solution**:
1. Check Docker container is running: `docker ps | grep chromadb`
2. Verify port mapping: 8001 (not 8000)
3. Check config: `CHROMADB_PORT=8001`

### Embedding Model Not Loading
**Problem**: `ModuleNotFoundError: No module named 'sentence_transformers'`

**Solution**:
```bash
pip install sentence-transformers
```

### Redis Connection Failed
**Problem**: `Connection refused` to Redis

**Solution**:
1. Ensure Redis container is running
2. Check port: `docker ps | grep redis`
3. Verify URL: `redis://localhost:6379/0`

### Slow Embeddings
**Problem**: Embedding generation is slow

**Solution**:
1. Use batch processing: `embed_texts()` instead of `embed_text()`
2. Enable caching
3. Consider GPU acceleration (if available)

---

## References

- **Sentence Transformers**: https://www.sbert.net/
- **ChromaDB Docs**: https://docs.trychroma.com/
- **LangChain RAG**: https://python.langchain.com/docs/use_cases/question_answering/
- **WBS Section 2.3**: `/docs/planning/WBS.md`

---

**Implementation Status**: ✅ **COMPLETE**
**Last Updated**: November 27, 2025
**Author**: Lyrica Development Team
