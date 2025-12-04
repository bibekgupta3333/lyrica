"""
RAG API Endpoints
Endpoints for Retrieval-Augmented Generation functionality.
"""

import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services import ingestion_service, rag_service, vector_store

router = APIRouter(tags=["RAG (Retrieval-Augmented Generation)"])


# Pydantic Schemas
class IngestDocumentRequest(BaseModel):
    """Request for ingesting a document."""

    document_id: uuid.UUID = Field(
        ..., description="UUID of the document to ingest from the database"
    )
    chunking_strategy: str = Field(
        default="recursive",
        description="Chunking strategy: 'recursive' (smart), 'fixed' (by size), 'sentence' (by sentences), 'paragraph' (by paragraphs)",
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "document_id": "123e4567-e89b-12d3-a456-426614174000",
                    "chunking_strategy": "recursive",
                },
                {
                    "document_id": "123e4567-e89b-12d3-a456-426614174001",
                    "chunking_strategy": "sentence",
                },
                {
                    "document_id": "123e4567-e89b-12d3-a456-426614174002",
                    "chunking_strategy": "paragraph",
                },
            ]
        }


class IngestLyricsRequest(BaseModel):
    """Request for ingesting lyrics."""

    lyrics_id: uuid.UUID = Field(
        ..., description="UUID of the lyrics to ingest (preserves verse/chorus structure)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "lyrics_id": "123e4567-e89b-12d3-a456-426614174000",
            }
        }


class IngestCustomTextRequest(BaseModel):
    """Request for ingesting custom text."""

    text: str = Field(
        ...,
        min_length=10,
        description="Custom text to ingest (minimum 10 characters)",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional metadata dictionary (e.g., genre, mood, theme)",
    )
    chunking_strategy: str = Field(
        default="recursive",
        description="Chunking strategy: 'recursive', 'fixed', 'sentence', or 'paragraph'",
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "text": "This is a reference song about love and summer. It has verses and a chorus about beach days and sunsets.",
                    "metadata": {"genre": "pop", "mood": "happy", "theme": "love"},
                    "chunking_strategy": "recursive",
                },
                {
                    "text": "Pop songs typically have verse-chorus structure. Verses tell a story, choruses repeat the main theme.",
                    "metadata": {"type": "style_guide", "genre": "pop"},
                    "chunking_strategy": "paragraph",
                },
            ]
        }


class SearchRequest(BaseModel):
    """Request for vector search."""

    query: str = Field(..., min_length=3, description="Search query text (minimum 3 characters)")
    n_results: int = Field(default=5, ge=1, le=20, description="Number of results to return (1-20)")
    filters: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional filters (e.g., {'genre': 'pop', 'mood': 'happy'})",
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "query": "songs about falling in love",
                    "n_results": 5,
                    "filters": None,
                },
                {
                    "query": "upbeat pop music",
                    "n_results": 10,
                    "filters": {"genre": "pop"},
                },
                {
                    "query": "sad ballad lyrics",
                    "n_results": 5,
                    "filters": {"mood": "sad", "genre": "ballad"},
                },
            ]
        }


class RAGQueryRequest(BaseModel):
    """Request for RAG query."""

    query: str = Field(..., min_length=3, description="Query text for RAG (retrieval + generation)")
    n_results: int = Field(
        default=5, ge=1, le=20, description="Number of context documents to retrieve (1-20)"
    )
    filters: Optional[Dict[str, Any]] = Field(
        None, description="Optional filters for document retrieval"
    )
    system_prompt: Optional[str] = Field(
        None, description="Optional custom system prompt for LLM generation"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "query": "What are common themes in pop songs?",
                    "n_results": 5,
                    "filters": None,
                    "system_prompt": None,
                },
                {
                    "query": "Analyze the structure of hip-hop songs",
                    "n_results": 10,
                    "filters": {"genre": "hip-hop"},
                    "system_prompt": "You are a music analyst expert.",
                },
            ]
        }


class GenerateLyricsRequest(BaseModel):
    """Request for generating lyrics with RAG."""

    theme: str = Field(
        ..., min_length=3, description="Theme for the lyrics (e.g., 'summer love', 'freedom')"
    )
    genre: Optional[str] = Field(None, description="Music genre (e.g., 'pop', 'rock', 'hip-hop')")
    mood: Optional[str] = Field(
        None, description="Mood/emotion (e.g., 'happy', 'sad', 'energetic')"
    )
    structure: Optional[str] = Field(
        None,
        description="Song structure (e.g., 'verse-chorus-verse-chorus-bridge-chorus')",
    )
    n_context_docs: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of similar lyrics to use as context (1-10)",
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "theme": "summer love",
                    "genre": "pop",
                    "mood": "happy",
                    "structure": "verse-chorus-verse-chorus-bridge-chorus",
                    "n_context_docs": 3,
                },
                {
                    "theme": "freedom and rebellion",
                    "genre": "rock",
                    "mood": "energetic",
                    "structure": "verse-chorus-verse-chorus-solo-chorus",
                    "n_context_docs": 5,
                },
                {
                    "theme": "lost love",
                    "genre": "ballad",
                    "mood": "melancholic",
                    "structure": None,
                    "n_context_docs": 4,
                },
            ]
        }


class VectorStoreStats(BaseModel):
    """Vector store statistics."""

    total_documents: int
    collection_name: str


# Endpoints
@router.post(
    "/ingest/document",
    status_code=status.HTTP_201_CREATED,
    summary="Ingest document",
    description="Ingest a document from the database into the vector store for semantic search",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "recursive_chunking": {
                            "summary": "Recursive Chunking",
                            "value": {
                                "document_id": "123e4567-e89b-12d3-a456-426614174000",
                                "chunking_strategy": "recursive",
                            },
                        },
                        "sentence_chunking": {
                            "summary": "Sentence Chunking",
                            "value": {
                                "document_id": "123e4567-e89b-12d3-a456-426614174001",
                                "chunking_strategy": "sentence",
                            },
                        },
                        "paragraph_chunking": {
                            "summary": "Paragraph Chunking",
                            "value": {
                                "document_id": "123e4567-e89b-12d3-a456-426614174002",
                                "chunking_strategy": "paragraph",
                            },
                        },
                    }
                }
            }
        }
    },
)
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


@router.post(
    "/ingest/lyrics",
    status_code=status.HTTP_201_CREATED,
    summary="Ingest lyrics",
    description="Ingest lyrics into the vector store with specialized chunking (preserves verse/chorus structure)",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "ingest_lyrics": {
                            "summary": "Ingest Lyrics",
                            "value": {
                                "lyrics_id": "123e4567-e89b-12d3-a456-426614174000",
                            },
                        },
                    }
                }
            }
        }
    },
)
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


@router.post(
    "/ingest/custom",
    status_code=status.HTTP_201_CREATED,
    summary="Ingest custom text",
    description="Ingest custom text directly into the vector store (useful for reference material)",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "song_reference": {
                            "summary": "Song Reference Text",
                            "value": {
                                "text": "This is a reference song about love and summer. It has verses and a chorus about beach days and sunsets.",
                                "metadata": {"genre": "pop", "mood": "happy", "theme": "love"},
                                "chunking_strategy": "recursive",
                            },
                        },
                        "lyrics_style_guide": {
                            "summary": "Lyrics Style Guide",
                            "value": {
                                "text": "Pop songs typically have verse-chorus structure. Verses tell a story, choruses repeat the main theme. Bridge sections provide contrast.",
                                "metadata": {"type": "style_guide", "genre": "pop"},
                                "chunking_strategy": "paragraph",
                            },
                        },
                        "poetry_example": {
                            "summary": "Poetry Example",
                            "value": {
                                "text": "Roses are red, violets are blue. Poetry can inspire song lyrics with its rhythm and imagery.",
                                "metadata": {"type": "poetry", "style": "rhyming"},
                                "chunking_strategy": "sentence",
                            },
                        },
                    }
                }
            }
        }
    },
)
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


@router.post(
    "/search",
    summary="Semantic search",
    description="Perform semantic search on the vector store to find similar documents",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "love_song_search": {
                            "summary": "Search Love Songs",
                            "value": {
                                "query": "songs about falling in love",
                                "n_results": 5,
                                "filters": None,
                            },
                        },
                        "genre_filtered": {
                            "summary": "Genre Filtered Search",
                            "value": {
                                "query": "upbeat pop music",
                                "n_results": 10,
                                "filters": {"genre": "pop"},
                            },
                        },
                        "mood_filtered": {
                            "summary": "Mood Filtered Search",
                            "value": {
                                "query": "sad ballad lyrics",
                                "n_results": 5,
                                "filters": {"mood": "sad", "genre": "ballad"},
                            },
                        },
                        "theme_search": {
                            "summary": "Theme Search",
                            "value": {
                                "query": "songs about summer",
                                "n_results": 8,
                                "filters": {"theme": "summer"},
                            },
                        },
                    }
                }
            }
        }
    },
)
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


@router.post(
    "/query",
    summary="RAG query",
    description="Perform a RAG query: retrieve relevant documents and generate response using LLM",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "lyrics_question": {
                            "summary": "Lyrics Question",
                            "value": {
                                "query": "What are common themes in pop songs?",
                                "n_results": 5,
                                "filters": None,
                                "system_prompt": None,
                            },
                        },
                        "genre_analysis": {
                            "summary": "Genre Analysis",
                            "value": {
                                "query": "Analyze the structure of hip-hop songs",
                                "n_results": 10,
                                "filters": {"genre": "hip-hop"},
                                "system_prompt": "You are a music analyst expert.",
                            },
                        },
                        "creative_inspiration": {
                            "summary": "Creative Inspiration",
                            "value": {
                                "query": "Give me ideas for a love song chorus",
                                "n_results": 3,
                                "filters": {"theme": "love"},
                                "system_prompt": "You are a creative songwriter assistant.",
                            },
                        },
                    }
                }
            }
        }
    },
)
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


@router.post(
    "/generate/lyrics",
    summary="Generate lyrics with RAG",
    description="Generate lyrics using RAG with similar lyrics as context for inspiration",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "pop_love_song": {
                            "summary": "Pop Love Song",
                            "value": {
                                "theme": "summer love",
                                "genre": "pop",
                                "mood": "happy",
                                "structure": "verse-chorus-verse-chorus-bridge-chorus",
                                "n_context_docs": 3,
                            },
                        },
                        "rock_anthem": {
                            "summary": "Rock Anthem",
                            "value": {
                                "theme": "freedom and rebellion",
                                "genre": "rock",
                                "mood": "energetic",
                                "structure": "verse-chorus-verse-chorus-solo-chorus",
                                "n_context_docs": 5,
                            },
                        },
                        "ballad_heartbreak": {
                            "summary": "Ballad Heartbreak",
                            "value": {
                                "theme": "lost love",
                                "genre": "ballad",
                                "mood": "melancholic",
                                "structure": "verse-chorus-verse-chorus-bridge-chorus",
                                "n_context_docs": 4,
                            },
                        },
                        "hip_hop_motivational": {
                            "summary": "Hip-Hop Motivational",
                            "value": {
                                "theme": "overcoming obstacles",
                                "genre": "hip-hop",
                                "mood": "uplifting",
                                "structure": None,
                                "n_context_docs": 3,
                            },
                        },
                    }
                }
            }
        }
    },
)
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


@router.get(
    "/stats",
    summary="Get vector store statistics",
    description="Get statistics about the vector store (total documents, collection name)",
)
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


@router.delete(
    "/reset",
    summary="Reset vector store",
    description="Reset the vector store (delete all documents). ⚠️ WARNING: This action is irreversible!",
)
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
