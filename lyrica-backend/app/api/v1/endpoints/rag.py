"""
RAG API Endpoints
Endpoints for Retrieval-Augmented Generation functionality.
"""

import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services import ingestion_service, rag_service, vector_store

router = APIRouter()


# Pydantic Schemas
class IngestDocumentRequest(BaseModel):
    """Request for ingesting a document."""

    document_id: uuid.UUID
    chunking_strategy: str = Field(
        default="recursive",
        description="Chunking strategy (recursive, fixed, sentence, paragraph)",
    )


class IngestLyricsRequest(BaseModel):
    """Request for ingesting lyrics."""

    lyrics_id: uuid.UUID


class IngestCustomTextRequest(BaseModel):
    """Request for ingesting custom text."""

    text: str = Field(..., min_length=10)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    chunking_strategy: str = Field(default="recursive")


class SearchRequest(BaseModel):
    """Request for vector search."""

    query: str = Field(..., min_length=3)
    n_results: int = Field(default=5, ge=1, le=20)
    filters: Optional[Dict[str, Any]] = None


class RAGQueryRequest(BaseModel):
    """Request for RAG query."""

    query: str = Field(..., min_length=3)
    n_results: int = Field(default=5, ge=1, le=20)
    filters: Optional[Dict[str, Any]] = None
    system_prompt: Optional[str] = None


class GenerateLyricsRequest(BaseModel):
    """Request for generating lyrics with RAG."""

    theme: str = Field(..., min_length=3)
    genre: Optional[str] = None
    mood: Optional[str] = None
    structure: Optional[str] = None
    n_context_docs: int = Field(default=3, ge=1, le=10)


class VectorStoreStats(BaseModel):
    """Vector store statistics."""

    total_documents: int
    collection_name: str


# Endpoints
@router.post("/ingest/document", status_code=status.HTTP_201_CREATED)
async def ingest_document(
    request: IngestDocumentRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Ingest a document from the database into the vector store.

    This endpoint chunks the document and stores embeddings for semantic search.
    """
    try:
        chunks_count = await ingestion_service.ingest_document(
            db=db,
            document_id=request.document_id,
            chunking_strategy=request.chunking_strategy,
        )

        return {
            "message": "Document ingested successfully",
            "document_id": str(request.document_id),
            "chunks_created": chunks_count,
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error ingesting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to ingest document",
        )


@router.post("/ingest/lyrics", status_code=status.HTTP_201_CREATED)
async def ingest_lyrics(
    request: IngestLyricsRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Ingest lyrics into the vector store with specialized chunking.

    This preserves verse/chorus structure for better retrieval.
    """
    try:
        chunks_count = await ingestion_service.ingest_lyrics(db=db, lyrics_id=request.lyrics_id)

        return {
            "message": "Lyrics ingested successfully",
            "lyrics_id": str(request.lyrics_id),
            "chunks_created": chunks_count,
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error ingesting lyrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to ingest lyrics",
        )


@router.post("/ingest/custom", status_code=status.HTTP_201_CREATED)
async def ingest_custom_text(
    request: IngestCustomTextRequest,
) -> Dict[str, Any]:
    """
    Ingest custom text directly into the vector store.

    Useful for adding reference material without storing in database.
    """
    try:
        chunks_count = await ingestion_service.ingest_custom_text(
            text=request.text,
            metadata=request.metadata,
            chunking_strategy=request.chunking_strategy,
        )

        return {
            "message": "Custom text ingested successfully",
            "chunks_created": chunks_count,
        }

    except Exception as e:
        logger.error(f"Error ingesting custom text: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to ingest custom text",
        )


@router.post("/search")
async def search_vectors(
    request: SearchRequest,
) -> Dict[str, Any]:
    """
    Perform semantic search on the vector store.

    Returns the most similar documents to the query.
    """
    try:
        results = await rag_service.retrieve(
            query=request.query,
            n_results=request.n_results,
            filters=request.filters,
        )

        return {"query": request.query, "results": results, "count": len(results)}

    except Exception as e:
        logger.error(f"Error searching vectors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search vectors",
        )


@router.post("/query")
async def rag_query(
    request: RAGQueryRequest,
) -> Dict[str, Any]:
    """
    Perform a RAG query: retrieve relevant documents and generate response.

    Combines semantic search with LLM generation.
    """
    try:
        result = await rag_service.retrieve_and_generate(
            query=request.query,
            n_results=request.n_results,
            filters=request.filters,
            system_prompt=request.system_prompt,
        )

        return result

    except Exception as e:
        logger.error(f"Error in RAG query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process RAG query",
        )


@router.post("/generate/lyrics")
async def generate_lyrics_with_rag(
    request: GenerateLyricsRequest,
) -> Dict[str, Any]:
    """
    Generate lyrics using RAG with similar lyrics as context.

    This endpoint uses semantic search to find similar lyrics and
    uses them as inspiration for generating new, original lyrics.
    """
    try:
        result = await rag_service.generate_lyrics_with_context(
            theme=request.theme,
            genre=request.genre,
            mood=request.mood,
            structure=request.structure,
            n_context_docs=request.n_context_docs,
        )

        return result

    except Exception as e:
        logger.error(f"Error generating lyrics with RAG: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate lyrics",
        )


@router.get("/stats")
async def get_vector_store_stats() -> VectorStoreStats:
    """
    Get statistics about the vector store.

    Returns the total number of documents and collection name.
    """
    try:
        count = vector_store.count()

        return VectorStoreStats(total_documents=count, collection_name=vector_store.collection_name)

    except Exception as e:
        logger.error(f"Error getting vector store stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get vector store stats",
        )


@router.delete("/reset")
async def reset_vector_store() -> Dict[str, str]:
    """
    Reset the vector store (delete all documents).

    ⚠️ WARNING: This action is irreversible!
    """
    try:
        vector_store.reset()
        return {"message": "Vector store reset successfully"}

    except Exception as e:
        logger.error(f"Error resetting vector store: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset vector store",
        )
