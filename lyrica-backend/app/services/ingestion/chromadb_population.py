"""
ChromaDB Population Service

Populates ChromaDB vector store with lyrics embeddings for RAG.
"""

from typing import Dict, List

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.lyrics import Lyrics
from app.services.embeddings import EmbeddingService
from app.services.vector_store import VectorStoreService
from app.utils.text_chunking import chunk_text


class ChromaDBPopulationService:
    """Service for populating ChromaDB with lyrics embeddings."""

    def __init__(self):
        """Initialize the population service."""
        self.vector_store = VectorStoreService()
        self.embedding_service = EmbeddingService()
        self.stats = {
            "lyrics_processed": 0,
            "chunks_created": 0,
            "embeddings_generated": 0,
            "documents_indexed": 0,
            "errors": 0,
        }

    async def populate_from_database(
        self,
        db: AsyncSession,
        batch_size: int = 32,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        reset_collection: bool = False,
    ) -> Dict[str, int]:
        """
        Populate ChromaDB from lyrics in the database.

        Args:
            db: Database session
            batch_size: Number of embeddings to generate at once
            chunk_size: Characters per chunk
            chunk_overlap: Overlap between chunks
            reset_collection: Whether to reset the collection first

        Returns:
            Dictionary with population statistics
        """
        logger.info("Starting ChromaDB population from database")

        # Reset collection if requested
        if reset_collection:
            logger.warning("Resetting ChromaDB collection...")
            self.vector_store.reset()
            logger.info("Collection reset complete")

        # Get all lyrics from database
        result = await db.execute(select(Lyrics))
        all_lyrics = result.scalars().all()

        if not all_lyrics:
            logger.warning("No lyrics found in database")
            return self.stats

        logger.info(f"Found {len(all_lyrics)} lyrics to process")
        logger.info(f"Chunk settings: size={chunk_size}, overlap={chunk_overlap}")
        logger.info("")

        # Process lyrics in batches
        texts_batch = []
        metadatas_batch = []
        ids_batch = []

        for idx, lyrics in enumerate(all_lyrics, 1):
            try:
                # Chunk the lyrics text
                chunks = chunk_text(
                    text=lyrics.content,
                    max_chunk_size=chunk_size,
                    overlap=chunk_overlap,
                    strategy="lyrics",
                )

                if not chunks:
                    logger.warning(f"No chunks generated for lyrics ID {lyrics.id}")
                    continue

                self.stats["lyrics_processed"] += 1
                self.stats["chunks_created"] += len(chunks)

                # Create document for each chunk
                for chunk_idx, chunk in enumerate(chunks):
                    doc_id = f"{lyrics.id}_{chunk_idx}"
                    metadata = {
                        "lyrics_id": str(lyrics.id),
                        "title": lyrics.title or "Untitled",
                        "genre": lyrics.genre or "unknown",
                        "mood": lyrics.mood or "neutral",
                        "language": lyrics.language or "en",
                        "doc_type": "lyrics",
                        "chunk_index": chunk_idx,
                        "total_chunks": len(chunks),
                    }

                    texts_batch.append(chunk)
                    metadatas_batch.append(metadata)
                    ids_batch.append(doc_id)

                # Process batch when it reaches batch_size
                if len(texts_batch) >= batch_size:
                    await self._process_batch(texts_batch, metadatas_batch, ids_batch)
                    texts_batch = []
                    metadatas_batch = []
                    ids_batch = []

                # Log progress every 10 lyrics
                if idx % 10 == 0:
                    logger.info(f"Progress: {idx}/{len(all_lyrics)} lyrics processed")

            except Exception as e:
                logger.error(f"Error processing lyrics ID {lyrics.id}: {e}")
                self.stats["errors"] += 1
                continue

        # Process remaining batch
        if texts_batch:
            await self._process_batch(texts_batch, metadatas_batch, ids_batch)

        logger.info("")
        logger.success("✅ ChromaDB population complete!")
        logger.info(f"   Lyrics processed: {self.stats['lyrics_processed']}")
        logger.info(f"   Chunks created: {self.stats['chunks_created']}")
        logger.info(f"   Embeddings generated: {self.stats['embeddings_generated']}")
        logger.info(f"   Documents indexed: {self.stats['documents_indexed']}")
        logger.info(f"   Errors: {self.stats['errors']}")

        # Verify final count
        final_count = self.vector_store.count()
        logger.info(f"   Final ChromaDB count: {final_count}")

        return self.stats

    async def _process_batch(
        self,
        texts: List[str],
        metadatas: List[Dict],
        ids: List[str],
    ):
        """Process a batch of documents."""
        try:
            # Add to vector store (it generates embeddings internally)
            await self.vector_store.add_documents(
                texts=texts,
                metadatas=metadatas,
                ids=ids,
            )
            self.stats["embeddings_generated"] += len(texts)
            self.stats["documents_indexed"] += len(texts)

        except Exception as e:
            logger.error(f"Error processing batch: {e}")
            self.stats["errors"] += 1
            raise

    def get_collection_stats(self) -> Dict[str, any]:
        """Get current ChromaDB collection statistics."""
        try:
            count = self.vector_store.count()
            return {
                "total_documents": count,
                "collection_name": self.vector_store.collection.name,
                "status": "ready" if count > 0 else "empty",
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {
                "total_documents": 0,
                "collection_name": "unknown",
                "status": "error",
                "error": str(e),
            }

    async def test_rag_search(
        self,
        query: str = "Write a happy love song",
        n_results: int = 5,
    ) -> bool:
        """
        Test RAG search functionality.

        Args:
            query: Test query
            n_results: Number of results to retrieve

        Returns:
            True if search works, False otherwise
        """
        try:
            logger.info(f"Testing RAG search with query: '{query}'")

            results = await self.vector_store.search(
                query=query,
                n_results=n_results,
            )

            if results and len(results["documents"]) > 0:
                logger.success(
                    f"✅ RAG search working! Retrieved {len(results['documents'])} results"
                )

                # Show first result
                if results["documents"]:
                    first_doc = results["documents"][0]
                    first_metadata = results["metadatas"][0] if results["metadatas"] else {}
                    logger.info(
                        f"   Top result: {first_metadata.get('title', 'Unknown')} ({first_metadata.get('genre', 'unknown')} / {first_metadata.get('mood', 'neutral')})"
                    )
                    logger.info(f"   Preview: {first_doc[:100]}...")

                return True
            else:
                logger.warning("⚠️  No results returned from RAG search")
                return False

        except Exception as e:
            logger.error(f"❌ RAG search test failed: {e}")
            return False
