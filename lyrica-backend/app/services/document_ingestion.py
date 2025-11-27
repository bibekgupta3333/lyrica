"""
Document Ingestion Service
Handles ingestion of documents into the vector store.
"""

import uuid
from typing import Any, Dict, List, Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.services.vector_store import vector_store
from app.utils.text_chunking import text_chunker


class DocumentIngestionService:
    """Service for ingesting documents into the vector store."""

    async def ingest_document(
        self,
        db: AsyncSession,
        document_id: uuid.UUID,
        chunking_strategy: str = "recursive",
    ) -> int:
        """
        Ingest a single document from database into vector store.

        Args:
            db: Database session
            document_id: ID of document to ingest
            chunking_strategy: Strategy for chunking text

        Returns:
            Number of chunks created
        """
        # Fetch document from database
        result = await db.execute(select(Document).where(Document.id == document_id))
        document = result.scalar_one_or_none()

        if not document:
            raise ValueError(f"Document {document_id} not found")

        logger.info(f"Ingesting document: {document.title}")

        # Chunk the document
        metadata = {
            "document_id": str(document.id),
            "title": document.title,
            "doc_type": document.doc_type,
            "genre": document.metadata.get("genre") if document.metadata else None,
            "mood": document.metadata.get("mood") if document.metadata else None,
            "language": document.language or "en",
            "created_at": document.created_at.isoformat(),
        }

        chunks = text_chunker.chunk_text(
            document.content, strategy=chunking_strategy, metadata=metadata
        )

        if not chunks:
            logger.warning(f"No chunks created for document {document_id}")
            return 0

        # Prepare data for vector store
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [
            {
                **{k: v for k, v in chunk.items() if k != "text"},
                "source": "database",
            }
            for chunk in chunks
        ]
        chunk_ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]

        # Add to vector store
        await vector_store.add_documents(texts=texts, metadatas=metadatas, ids=chunk_ids)

        logger.info(f"Ingested document {document_id} with {len(chunks)} chunks")
        return len(chunks)

    async def ingest_documents(
        self,
        db: AsyncSession,
        document_ids: Optional[List[uuid.UUID]] = None,
        doc_type: Optional[str] = None,
        chunking_strategy: str = "recursive",
    ) -> Dict[str, int]:
        """
        Ingest multiple documents into vector store.

        Args:
            db: Database session
            document_ids: Optional list of specific document IDs
            doc_type: Optional filter by document type
            chunking_strategy: Strategy for chunking text

        Returns:
            Dictionary with ingestion statistics
        """
        # Build query
        query = select(Document)

        if document_ids:
            query = query.where(Document.id.in_(document_ids))
        elif doc_type:
            query = query.where(Document.doc_type == doc_type)

        # Fetch documents
        result = await db.execute(query)
        documents = result.scalars().all()

        if not documents:
            logger.warning("No documents found to ingest")
            return {"total": 0, "successful": 0, "failed": 0, "chunks": 0}

        logger.info(f"Ingesting {len(documents)} documents")

        stats = {"total": len(documents), "successful": 0, "failed": 0, "chunks": 0}

        # Ingest each document
        for document in documents:
            try:
                chunks_count = await self.ingest_document(db, document.id, chunking_strategy)
                stats["successful"] += 1
                stats["chunks"] += chunks_count
            except Exception as e:
                logger.error(f"Failed to ingest document {document.id}: {e}")
                stats["failed"] += 1

        logger.info(
            f"Ingestion complete: {stats['successful']}/{stats['total']} documents, "
            f"{stats['chunks']} chunks"
        )
        return stats

    async def ingest_lyrics(self, db: AsyncSession, lyrics_id: uuid.UUID) -> int:
        """
        Ingest lyrics with specialized chunking.

        Args:
            db: Database session
            lyrics_id: ID of lyrics to ingest

        Returns:
            Number of chunks created
        """
        from app.models.lyrics import Lyrics

        # Fetch lyrics from database
        result = await db.execute(select(Lyrics).where(Lyrics.id == lyrics_id))
        lyrics = result.scalar_one_or_none()

        if not lyrics:
            raise ValueError(f"Lyrics {lyrics_id} not found")

        logger.info(f"Ingesting lyrics: {lyrics.title}")

        # Use specialized lyrics chunking
        metadata = {
            "lyrics_id": str(lyrics.id),
            "title": lyrics.title,
            "genre": lyrics.genre,
            "mood": lyrics.mood,
            "language": lyrics.language or "en",
            "doc_type": "lyrics",
            "created_at": lyrics.created_at.isoformat(),
        }

        chunks = text_chunker.chunk_lyrics(lyrics.content, metadata=metadata)

        if not chunks:
            logger.warning(f"No chunks created for lyrics {lyrics_id}")
            return 0

        # Prepare data for vector store
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [
            {**{k: v for k, v in chunk.items() if k != "text"}, "source": "lyrics"}
            for chunk in chunks
        ]
        chunk_ids = [f"{lyrics_id}_chunk_{i}" for i in range(len(chunks))]

        # Add to vector store
        await vector_store.add_documents(texts=texts, metadatas=metadatas, ids=chunk_ids)

        logger.info(f"Ingested lyrics {lyrics_id} with {len(chunks)} chunks")
        return len(chunks)

    async def ingest_custom_text(
        self,
        text: str,
        metadata: Dict[str, Any],
        chunking_strategy: str = "recursive",
        doc_id: Optional[str] = None,
    ) -> int:
        """
        Ingest custom text directly into vector store.

        Args:
            text: Text to ingest
            metadata: Metadata for the text
            chunking_strategy: Strategy for chunking text
            doc_id: Optional document ID

        Returns:
            Number of chunks created
        """
        if not doc_id:
            doc_id = str(uuid.uuid4())

        logger.info(f"Ingesting custom text (doc_id: {doc_id})")

        # Chunk the text
        chunks = text_chunker.chunk_text(text, strategy=chunking_strategy, metadata=metadata)

        if not chunks:
            logger.warning("No chunks created for custom text")
            return 0

        # Prepare data for vector store
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [
            {**{k: v for k, v in chunk.items() if k != "text"}, "source": "custom"}
            for chunk in chunks
        ]
        chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]

        # Add to vector store
        await vector_store.add_documents(texts=texts, metadatas=metadatas, ids=chunk_ids)

        logger.info(f"Ingested custom text with {len(chunks)} chunks")
        return len(chunks)

    async def delete_document_chunks(self, document_id: uuid.UUID) -> None:
        """
        Delete all chunks for a document from vector store.

        Args:
            document_id: ID of document
        """
        # Find all chunk IDs for this document
        # Since ChromaDB doesn't have a direct way to query by prefix,
        # we'll search for chunks with matching document_id in metadata
        try:
            # This is a workaround - in production, you might want to maintain
            # an index of chunk IDs per document
            logger.info(f"Deleting chunks for document {document_id}")
            # For now, we'll just log a warning
            logger.warning(
                "Chunk deletion by document_id not fully implemented. "
                "Consider maintaining a chunk ID index."
            )
        except Exception as e:
            logger.error(f"Error deleting document chunks: {e}")
            raise


# Global document ingestion service instance
ingestion_service = DocumentIngestionService()
