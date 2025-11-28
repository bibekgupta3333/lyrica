# Lyrica API Reference

**Complete REST API documentation for the Lyrica backend.**

## Base URL

```
http://localhost:8000/api/v1
```

## API Categories

| Category | Endpoints | Status | Description |
|----------|-----------|--------|-------------|
| Health & System | 5 | ✅ Working | Health checks and system info |
| RAG & Vector Search | 8 | ✅ Working | Document ingestion and semantic search |
| Song Generation (Agents) | 3 | ✅ Working | Multi-agent song generation workflow |
| Lyrics Management | 8 | ⏳ Auth Required | CRUD operations for lyrics |
| User Feedback | 5 | ⏳ Auth Required | Feedback submission and statistics |
| Styles & Genres | 5 | ✅ Working | Genre, mood, theme discovery |

**Total: 35 unique endpoints**

---

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 1. Health & System (5 endpoints)

### GET `/health/health`

Basic health check.

```bash
curl http://localhost:8000/api/v1/health/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-28T03:04:07.128881",
  "version": "1.0.0",
  "environment": "development"
}
```

### GET `/health/health/ready`

Readiness check (database connection).

### GET `/health/health/live`

Liveness check.

### GET `/health/health/metrics`

System metrics (memory, CPU, etc.).

### GET `/health/health/info`

Detailed system information.

---

## 2. Styles & Genres (5 endpoints) 🆕

### GET `/styles/`

Get complete style catalog (genres + moods + themes + references).

```bash
curl http://localhost:8000/api/v1/styles/
```

**Response:**
```json
{
  "genres": [...],      // 12 genres
  "moods": [...],       // 10 moods
  "themes": [...],      // 10 themes
  "style_references": [...] // 10 artist references
}
```

### GET `/styles/genres`

List all available music genres.

**Response (sample):**
```json
[
  {
    "name": "pop",
    "description": "Contemporary popular music with catchy melodies",
    "examples": ["Taylor Swift - Shake It Off", "Ed Sheeran - Shape of You"]
  },
  {
    "name": "rock",
    "description": "Guitar-driven music with strong rhythms",
    "examples": ["Queen - Bohemian Rhapsody", "Led Zeppelin - Stairway to Heaven"]
  }
  // ... 10 more genres
]
```

### GET `/styles/moods`

List all available moods.

**Moods**: happy, sad, romantic, angry, calm, energetic, mysterious, nostalgic, empowering, dreamy

### GET `/styles/themes`

List all available themes.

**Themes**: love, loss, freedom, hope, nostalgia, adventure, identity, social issues, celebration, resilience

### GET `/styles/references`

List artist and song style references.

**References**: Taylor Swift, Ed Sheeran, Adele, The Weeknd, Kendrick Lamar, Coldplay, Billie Eilish, Sam Smith, Drake, Queen

---

## 3. Song Generation (Agents) (3 endpoints)

### POST `/songs/generate` 🔒

Generate complete song using multi-agent workflow.

**Authentication Required**: Yes

```bash
curl -X POST http://localhost:8000/api/v1/songs/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "prompt": "A motivational song about chasing dreams",
    "genre": "pop",
    "mood": "uplifting",
    "length": "medium",
    "use_rag": true
  }'
```

**Request Body:**
- `prompt` (required): User prompt for song generation (10-500 chars)
- `genre` (optional): Music genre (see `/styles/genres`)
- `mood` (optional): Desired mood (see `/styles/moods`)
- `theme` (optional): Song theme (see `/styles/themes`)
- `length` (optional): "short", "medium" (default), "long"
- `style_references` (optional): Array of artist names
- `use_rag` (optional): Use RAG for context (default: true)
- `llm_provider` (optional): "ollama" (default), "openai", "gemini", "grok"

**Response:**
```json
{
  "workflow_status": "completed",
  "workflow_duration": 45.2,
  "title": "Chasing Dreams",
  "final_lyrics": "[INTRO]\n...",
  "song_structure": {
    "sections": [...],
    "total_sections": 8,
    "structure_type": "verse-chorus"
  },
  "evaluation_score": {
    "overall": 8.2,
    "creativity": 8.5,
    "coherence": 8.0,
    "rhyme_quality": 8.3,
    "emotional_impact": 8.7,
    "genre_fit": 7.5
  },
  "refinement_iterations": 2,
  "retry_count": 0
}
```

### GET `/songs/providers`

List available LLM providers.

```bash
curl http://localhost:8000/api/v1/songs/providers
```

**Response:**
```json
{
  "providers": [
    {
      "name": "ollama",
      "display_name": "Ollama (Local)",
      "cost": "free",
      "speed": "fast"
    },
    // ... 3 more providers
  ],
  "default": "ollama"
}
```

### GET `/songs/workflow-info`

Get information about the multi-agent workflow.

---

## 4. RAG & Vector Search (8 endpoints)

### POST `/rag/ingest/document`

Ingest document from database into vector store.

### POST `/rag/ingest/lyrics`

Ingest lyrics by ID into vector store.

### POST `/rag/ingest/custom`

Ingest custom text into vector store.

### POST `/rag/search`

Semantic search in vector store.

```bash
curl -X POST http://localhost:8000/api/v1/rag/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "love songs",
    "n_results": 5
  }'
```

### POST `/rag/query`

Query RAG system (retrieval only, no generation).

### POST `/rag/generate/lyrics`

Generate lyrics using RAG-augmented generation.

### GET `/rag/stats`

Get RAG system statistics.

```bash
curl http://localhost:8000/api/v1/rag/stats
```

**Response:**
```json
{
  "total_documents": 11,
  "collection_name": "lyrics_embeddings"
}
```

### DELETE `/rag/reset`

Reset vector store (delete all documents).

---

## 5. Lyrics Management (8 endpoints) 🆕

### POST `/lyrics/generate` 🔒

Generate new lyrics and save to database.

**Authentication Required**: Yes

```bash
curl -X POST http://localhost:8000/api/v1/lyrics/generate \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Song",
    "content": "Verse 1...",
    "structure": {"sections": []},
    "genre": "pop"
  }'
```

### GET `/lyrics/{id}` 🔒

Retrieve lyrics by ID.

**Authentication Required**: Yes (owner or public)

### GET `/lyrics/` 🔒

List lyrics with filters.

**Authentication Required**: Yes

**Query Parameters:**
- `skip`: Number to skip (default: 0)
- `limit`: Max results (default: 100, max: 100)
- `genre`: Filter by genre
- `public_only`: Show only public lyrics

### PUT `/lyrics/{id}` 🔒

Update lyrics.

**Authentication Required**: Yes (owner only)

### DELETE `/lyrics/{id}` 🔒

Delete lyrics.

**Authentication Required**: Yes (owner only)

### POST `/lyrics/{id}/regenerate` 🔒

Regenerate a specific section.

**Authentication Required**: Yes (owner only)

**Query Parameters:**
- `section_type`: Section to regenerate (verse, chorus, etc.)

### GET `/lyrics/history` 🔒

Get user's generation history.

**Authentication Required**: Yes

### GET `/lyrics/public/explore`

Explore public lyrics (no auth required).

```bash
curl http://localhost:8000/api/v1/lyrics/public/explore?limit=20
```

**Query Parameters:**
- `skip`: Number to skip (default: 0)
- `limit`: Max results (default: 20, max: 100)
- `genre`: Filter by genre

**Response:**
```json
[
  {
    "id": "uuid",
    "title": "Song Title",
    "genre": "pop",
    "mood": "happy",
    "quality_score": 8.5,
    "like_count": 42,
    "created_at": "2025-11-28T..."
  }
]
```

---

## 6. User Feedback (5 endpoints) 🆕

### POST `/feedback/` 🔒

Submit feedback for lyrics.

**Authentication Required**: Yes

```bash
curl -X POST http://localhost:8000/api/v1/feedback/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "lyrics_id": "uuid",
    "overall_rating": 5,
    "creativity_rating": 5,
    "quality_rating": 4,
    "comment": "Great lyrics!",
    "is_liked": true
  }'
```

**Request Body:**
- `lyrics_id` (required): UUID of lyrics
- `overall_rating` (optional): 1-5 stars
- `creativity_rating` (optional): 1-5 stars
- `relevance_rating` (optional): 1-5 stars
- `quality_rating` (optional): 1-5 stars
- `comment` (optional): Text comment (max 1000 chars)
- `tags` (optional): Array of strings
- `is_liked` (optional): Boolean (default: false)

### GET `/feedback/` 🔒

List user's own feedback.

**Authentication Required**: Yes

### GET `/feedback/lyrics/{id}` 🔒

Get all feedback for specific lyrics.

**Authentication Required**: Yes (owner or admin)

### GET `/feedback/stats` 🔒

Get feedback statistics.

**Authentication Required**: Yes

**Response:**
```json
{
  "total_feedback": 150,
  "average_rating": 4.2,
  "rating_distribution": {
    "5": 80,
    "4": 40,
    "3": 20,
    "2": 5,
    "1": 5
  },
  "feedback_with_comments": 90,
  "recent_feedback_count": 25
}
```

### DELETE `/feedback/{id}` 🔒

Delete feedback entry.

**Authentication Required**: Yes (owner only)

---

## Authentication

### Currently

All protected endpoints return:

```json
{
  "detail": "Authentication not yet implemented. Please implement JWT validation."
}
```

**Status Code**: 501 Not Implemented

### Coming in WBS 2.7

Will implement:
- JWT token generation
- User registration/login endpoints
- Token validation
- Role-based access control (RBAC)
- Rate limiting

**Headers:**
```
Authorization: Bearer <jwt_token>
```

---

## Status Codes

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | Successful GET/PUT |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | No permission for resource |
| 404 | Not Found | Resource doesn't exist |
| 500 | Internal Server Error | Server error |
| 501 | Not Implemented | Feature not yet implemented |

---

## Rate Limiting

**Coming in WBS 2.7**

Will implement:
- Rate limiting per endpoint
- Rate limiting per user
- Rate limiting per IP

---

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `skip` (default: 0): Number of records to skip
- `limit` (default: varies, max: 100): Maximum records to return

**Example:**
```bash
curl http://localhost:8000/api/v1/lyrics/public/explore?skip=20&limit=10
```

---

## Error Handling

All errors return a consistent format:

```json
{
  "error": "Error Type",
  "message": "Human-readable error message",
  "request_id": "uuid"
}
```

---

## Testing

### Manual Testing

```bash
# Health check
curl http://localhost:8000/api/v1/health/health

# Get genres
curl http://localhost:8000/api/v1/styles/genres | jq '.[].name'

# Explore public lyrics
curl http://localhost:8000/api/v1/lyrics/public/explore

# Get workflow info
curl http://localhost:8000/api/v1/songs/workflow-info
```

### With Authentication (WBS 2.7)

```bash
# Login and get token (coming soon)
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -d '{"email": "user@example.com", "password": "password"}' \
  | jq -r '.access_token')

# Use token
curl http://localhost:8000/api/v1/lyrics/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## Quick Reference

### Public Endpoints (No Auth)

✅ Available now:
- All `/health/*` endpoints
- All `/styles/*` endpoints
- `GET /lyrics/public/explore`
- `GET /songs/providers`
- `GET /songs/workflow-info`
- `GET /rag/stats`

### Protected Endpoints (Auth Required)

⏳ Requires WBS 2.7 (Authentication):
- All `/lyrics/*` endpoints (except public/explore)
- All `/feedback/*` endpoints
- `POST /songs/generate`
- All `/rag/*` POST/DELETE endpoints

---

## Related Documentation

- [Agent System Guide](AGENT_SYSTEM_GUIDE.md) - Multi-agent workflow details
- [RAG Implementation](RAG_IMPLEMENTATION.md) - RAG system details
- [Flexible LLM Guide](FLEXIBLE_LLM_GUIDE.md) - LLM provider switching
- [Agent API Quick Reference](AGENT_API_QUICK_REFERENCE.md) - Agent endpoint examples
- [RAG API Quick Reference](RAG_API_QUICK_REFERENCE.md) - RAG endpoint examples

---

## Support

For issues or questions:
- Check Swagger UI: http://localhost:8000/docs
- Review logs: `tail -f lyrica-backend/logs/app.log`
- Check database: http://localhost:5050 (pgAdmin)
- Check Redis: http://localhost:8081 (Redis Commander)

---

**Last Updated**: November 28, 2025
**API Version**: 1.0.0
**Total Endpoints**: 35
