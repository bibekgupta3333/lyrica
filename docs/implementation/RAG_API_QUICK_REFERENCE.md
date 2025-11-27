# RAG API Quick Reference

**Base URL**: `http://localhost:8000/api/v1/rag`

---

## 📊 Get Stats

**Endpoint**: `GET /stats`

```bash
curl http://localhost:8000/api/v1/rag/stats
```

**Response**:
```json
{
  "total_documents": 6,
  "collection_name": "lyrics_embeddings"
}
```

---

## 🔍 Semantic Search

**Endpoint**: `POST /search`

### Basic Search
```bash
curl -X POST http://localhost:8000/api/v1/rag/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "songs about love and heartbreak",
    "n_results": 5
  }'
```

### Search with Filters
```bash
curl -X POST http://localhost:8000/api/v1/rag/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "emotional songs",
    "n_results": 5,
    "filters": {
      "mood": "sad",
      "genre": "ballad"
    }
  }'
```

**Response**:
```json
{
  "query": "songs about love",
  "results": [
    {
      "id": "uuid",
      "text": "Document text...",
      "metadata": {"genre": "ballad", "mood": "sad"},
      "distance": 0.74,
      "score": 0.26
    }
  ],
  "count": 5
}
```

---

## 📝 Ingest Custom Text

**Endpoint**: `POST /ingest/custom`

```bash
curl -X POST http://localhost:8000/api/v1/rag/ingest/custom \
  -H "Content-Type: application/json" \
  -d '{
    "text": "[Verse 1]\nWalking down this road...\n\n[Chorus]\nI will fly...",
    "metadata": {
      "genre": "pop",
      "mood": "uplifting",
      "theme": "freedom"
    },
    "chunking_strategy": "lyrics"
  }'
```

**Chunking Strategies**:
- `recursive` - Default, uses multiple separators
- `fixed` - Fixed character count
- `sentence` - Splits by sentences
- `paragraph` - Splits by paragraphs
- `lyrics` - Preserves verse/chorus structure (best for lyrics)

**Response**:
```json
{
  "message": "Custom text ingested successfully",
  "chunks_created": 3
}
```

---

## 🎵 Ingest Lyrics from Database

**Endpoint**: `POST /ingest/lyrics`

```bash
curl -X POST http://localhost:8000/api/v1/rag/ingest/lyrics \
  -H "Content-Type: application/json" \
  -d '{
    "lyrics_id": "uuid-of-lyrics"
  }'
```

**Response**:
```json
{
  "message": "Lyrics ingested successfully",
  "lyrics_id": "uuid",
  "chunks_created": 4
}
```

---

## 📄 Ingest Document from Database

**Endpoint**: `POST /ingest/document`

```bash
curl -X POST http://localhost:8000/api/v1/rag/ingest/document \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "uuid-of-document",
    "chunking_strategy": "recursive"
  }'
```

---

## 🤖 RAG Query (Retrieve + Generate)

**Endpoint**: `POST /query`

```bash
curl -X POST http://localhost:8000/api/v1/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Write a song about overcoming challenges",
    "n_results": 5,
    "filters": {"genre": "rock"},
    "system_prompt": "You are a creative songwriter..."
  }'
```

**Response**:
```json
{
  "query": "Write a song about overcoming challenges",
  "response": "Generated lyrics here...",
  "context": [...],
  "num_retrieved": 5,
  "num_used": 3
}
```

---

## 🎸 Generate Lyrics with RAG

**Endpoint**: `POST /generate/lyrics`

```bash
curl -X POST http://localhost:8000/api/v1/rag/generate/lyrics \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "adventure and freedom",
    "genre": "rock",
    "mood": "energetic",
    "structure": "verse-chorus-verse-chorus-bridge-chorus",
    "n_context_docs": 3
  }'
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

## 🗑️ Reset Vector Store

**Endpoint**: `DELETE /reset`

⚠️ **WARNING**: This deletes all documents. Irreversible!

```bash
curl -X DELETE http://localhost:8000/api/v1/rag/reset
```

**Response**:
```json
{
  "message": "Vector store reset successfully"
}
```

---

## 📖 Interactive Documentation

View full API documentation with interactive testing:

```bash
# Open in browser
open http://localhost:8000/docs
```

---

## 🧪 Testing Examples

### Example 1: Ingest and Search
```bash
# 1. Ingest custom lyrics
curl -X POST http://localhost:8000/api/v1/rag/ingest/custom \
  -H "Content-Type: application/json" \
  -d '{
    "text": "[Verse 1]\nUnder the stars tonight\nFeeling alive and free\n\n[Chorus]\nThis is our moment\nLet it be",
    "metadata": {"genre": "pop", "mood": "romantic"},
    "chunking_strategy": "lyrics"
  }'

# 2. Check stats
curl http://localhost:8000/api/v1/rag/stats

# 3. Search for similar content
curl -X POST http://localhost:8000/api/v1/rag/search \
  -H "Content-Type: application/json" \
  -d '{"query": "romantic songs under stars", "n_results": 3}'
```

### Example 2: Filtered Search
```bash
# Search for upbeat pop songs only
curl -X POST http://localhost:8000/api/v1/rag/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "energetic dance music",
    "n_results": 5,
    "filters": {
      "genre": "pop",
      "mood": "energetic"
    }
  }'
```

### Example 3: Generate Lyrics
```bash
# Generate new lyrics with similar context
curl -X POST http://localhost:8000/api/v1/rag/generate/lyrics \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "chasing dreams",
    "genre": "pop-rock",
    "mood": "inspirational",
    "n_context_docs": 5
  }'
```

---

## 💡 Pro Tips

1. **Use Metadata Filters**: Narrow down results with `filters` parameter
2. **Adjust n_results**: More results = more context, but slower
3. **Lyrics Chunking**: Always use `"chunking_strategy": "lyrics"` for song lyrics
4. **Check Stats**: Use `/stats` to verify documents are being added
5. **Test with /docs**: Use Swagger UI for interactive API testing

---

## 🔧 Common Issues

### Issue: No results returned
**Solution**:
- Check if documents are ingested (`/stats`)
- Reduce filter constraints
- Increase `n_results`

### Issue: Poor search results
**Solution**:
- Ensure metadata is set correctly
- Use more descriptive queries
- Try different chunking strategies

### Issue: Slow responses
**Solution**:
- Reduce `n_results`
- Enable Redis caching
- Check ChromaDB connection

---

**Last Updated**: November 27, 2025
**Version**: 1.0.0
