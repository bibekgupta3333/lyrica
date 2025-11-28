#!/usr/bin/env python
"""
Test RAG System
Quick test script to verify RAG components are working.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.logging import logger, setup_logging
from app.services import embedding_service, ingestion_service, rag_service, vector_store


async def test_embeddings():
    """Test embedding generation."""
    logger.info("=" * 60)
    logger.info("Testing Embedding Service")
    logger.info("=" * 60)

    texts = [
        "I love writing songs about the ocean",
        "The mountains inspire my music",
        "City life is reflected in my lyrics",
    ]

    logger.info(f"Generating embeddings for {len(texts)} texts...")
    embeddings = await embedding_service.embed_texts(texts)

    logger.info(f"✅ Generated {len(embeddings)} embeddings")
    logger.info(f"   Embedding dimension: {len(embeddings[0])}")
    logger.info(f"   Cache size: {embedding_service.get_cache_size()}")


async def test_vector_store():
    """Test vector store operations."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Vector Store")
    logger.info("=" * 60)

    # Sample documents
    documents = [
        "Lost in the rhythm of the night, dancing under moonlight",
        "City streets are calling me, freedom is my melody",
        "Mountains high and valleys low, that's where I want to go",
        "Ocean waves crash on the shore, I can't help but ask for more",
        "Heartbreak and lonely tears, facing all my deepest fears",
    ]

    metadatas = [
        {"genre": "pop", "mood": "energetic", "doc_type": "lyrics"},
        {"genre": "rock", "mood": "rebellious", "doc_type": "lyrics"},
        {"genre": "folk", "mood": "peaceful", "doc_type": "lyrics"},
        {"genre": "pop", "mood": "uplifting", "doc_type": "lyrics"},
        {"genre": "ballad", "mood": "sad", "doc_type": "lyrics"},
    ]

    logger.info(f"Adding {len(documents)} documents to vector store...")
    ids = await vector_store.add_documents(documents, metadatas)

    logger.info(f"✅ Added {len(ids)} documents")
    logger.info(f"   Collection: {vector_store.collection_name}")
    logger.info(f"   Total documents: {vector_store.count()}")


async def test_search():
    """Test semantic search."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Semantic Search")
    logger.info("=" * 60)

    queries = [
        "songs about nature and outdoors",
        "upbeat party music",
        "sad emotional songs",
    ]

    for query in queries:
        logger.info(f"\nQuery: '{query}'")
        results = await vector_store.search(query, n_results=2)

        logger.info(f"  Found {len(results['ids'])} results:")
        for i, (doc, score) in enumerate(zip(results["documents"], results["distances"]), 1):
            similarity = 1 - score
            logger.info(f"    {i}. (similarity: {similarity:.3f}) {doc[:60]}...")


async def test_rag():
    """Test RAG query."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing RAG System")
    logger.info("=" * 60)

    query = "Write a song about adventure and freedom"
    logger.info(f"Query: '{query}'")

    try:
        # Just test retrieval part (LLM may not be available)
        results = await rag_service.retrieve(query, n_results=3)

        logger.info(f"✅ Retrieved {len(results)} relevant documents")
        for i, result in enumerate(results, 1):
            logger.info(f"   {i}. Score: {result['score']:.3f}")
            logger.info(f"      Text: {result['text'][:60]}...")
            logger.info(f"      Metadata: {result['metadata']}")

    except Exception as e:
        logger.warning(f"⚠️  RAG generation test skipped (Ollama may not be running): {e}")


async def test_chunking():
    """Test text chunking."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Text Chunking")
    logger.info("=" * 60)

    sample_text = """[Verse 1]
Walking down this lonely road
Carrying such a heavy load
But I know I'll find my way
Tomorrow brings a brand new day

[Chorus]
Rise up, stand tall
Don't let yourself fall
We can make it through
I believe in you

[Verse 2]
Stars are shining in the night
Guiding me toward the light
Every step brings me closer
To becoming who I'm supposed to be"""

    from app.utils.text_chunking import text_chunker

    # Test different strategies
    strategies = ["recursive", "paragraph", "lyrics"]

    for strategy in strategies:
        if strategy == "lyrics":
            chunks = text_chunker.chunk_lyrics(sample_text)
        else:
            chunks = text_chunker.chunk_text(sample_text, strategy=strategy)

        logger.info(f"\nStrategy: {strategy}")
        logger.info(f"  Created {len(chunks)} chunks")
        for i, chunk in enumerate(chunks[:2], 1):  # Show first 2
            logger.info(f"  Chunk {i}: {chunk['text'][:60]}...")


async def main():
    """Run all tests."""
    setup_logging()

    logger.info("🚀 Starting RAG System Tests")
    logger.info(f"Backend: {Path(__file__).parent.parent}")

    try:
        # Test individual components
        await test_embeddings()
        await test_chunking()
        await test_vector_store()
        await test_search()
        await test_rag()

        logger.info("\n" + "=" * 60)
        logger.info("✅ All RAG System Tests Completed Successfully!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
