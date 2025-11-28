"""
Vector Store Service
Handles ChromaDB operations for vector storage and retrieval.
"""

import uuid
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings
from loguru import logger

from app.core.config import settings
from app.services.embeddings import embedding_service


class VectorStoreService:
    """Service for managing vector storage with ChromaDB."""

    def __init__(self):
        """Initialize the vector store service."""
        self._client: Optional[chromadb.Client] = None
        self._collection: Optional[chromadb.Collection] = None
        self.collection_name = settings.chromadb_collection
        logger.info(f"Initializing vector store service")

    @property
    def client(self) -> chromadb.Client:
        """Lazy load ChromaDB client."""
        if self._client is None:
            try:
                logger.info(
                    f"Connecting to ChromaDB at {settings.chromadb_host}:{settings.chromadb_port}"
                )
                self._client = chromadb.HttpClient(
                    host=settings.chromadb_host,
                    port=settings.chromadb_port,
                    settings=ChromaSettings(
                        anonymized_telemetry=False,
                    ),
                )
                logger.info("ChromaDB client connected successfully")
            except Exception as e:
                logger.error(f"Failed to connect to ChromaDB: {e}")
                raise
        return self._client

    @property
    def collection(self) -> chromadb.Collection:
        """Get or create the collection."""
        if self._collection is None:
            try:
                self._collection = self.client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={
                        "description": "Lyrics and document embeddings",
                        "model": settings.embedding_model,
                        "dimension": settings.embedding_dimension,
                    },
                )
                logger.info(
                    f"Collection '{self.collection_name}' ready ({self._collection.count()} documents)"
                )
            except Exception as e:
                logger.error(f"Failed to get/create collection: {e}")
                raise
        return self._collection

    async def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Add documents to the vector store.

        Args:
            texts: List of text documents
            metadatas: Optional list of metadata dicts
            ids: Optional list of document IDs

        Returns:
            List of document IDs
        """
        if not texts:
            return []

        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in texts]

        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} documents")
        embeddings = await embedding_service.embed_texts(texts)

        # Prepare metadatas
        if metadatas is None:
            metadatas = [{} for _ in texts]

        try:
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids,
            )
            logger.info(f"Added {len(texts)} documents to vector store")
            return ids

        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise

    async def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Search for similar documents.

        Args:
            query: Search query text
            n_results: Number of results to return
            where: Metadata filters
            where_document: Document content filters

        Returns:
            Dictionary with ids, documents, metadatas, and distances
        """
        try:
            # Generate query embedding
            logger.info(f"Searching for: '{query[:100]}...'")
            query_embedding = await embedding_service.embed_text(query)

            # Search collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
                where_document=where_document,
                include=["documents", "metadatas", "distances"],
            )

            # Format results
            formatted_results = {
                "ids": results["ids"][0] if results["ids"] else [],
                "documents": results["documents"][0] if results["documents"] else [],
                "metadatas": results["metadatas"][0] if results["metadatas"] else [],
                "distances": results["distances"][0] if results["distances"] else [],
            }

            logger.info(f"Found {len(formatted_results['ids'])} similar documents")
            return formatted_results

        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            raise

    async def get_by_ids(self, ids: List[str]) -> Dict[str, Any]:
        """
        Get documents by IDs.

        Args:
            ids: List of document IDs

        Returns:
            Dictionary with documents and metadatas
        """
        try:
            results = self.collection.get(ids=ids, include=["documents", "metadatas"])
            logger.info(f"Retrieved {len(results['ids'])} documents")
            return results

        except Exception as e:
            logger.error(f"Error getting documents by IDs: {e}")
            raise

    async def update_documents(
        self,
        ids: List[str],
        texts: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """
        Update existing documents.

        Args:
            ids: List of document IDs to update
            texts: Optional new texts
            metadatas: Optional new metadatas
        """
        try:
            update_kwargs = {"ids": ids}

            if texts:
                embeddings = await embedding_service.embed_texts(texts)
                update_kwargs["embeddings"] = embeddings
                update_kwargs["documents"] = texts

            if metadatas:
                update_kwargs["metadatas"] = metadatas

            self.collection.update(**update_kwargs)
            logger.info(f"Updated {len(ids)} documents")

        except Exception as e:
            logger.error(f"Error updating documents: {e}")
            raise

    async def delete_documents(self, ids: List[str]) -> None:
        """
        Delete documents by IDs.

        Args:
            ids: List of document IDs to delete
        """
        try:
            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents")

        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            raise

    def count(self) -> int:
        """Get the total number of documents in the collection."""
        return self.collection.count()

    def peek(self, limit: int = 10) -> Dict[str, Any]:
        """
        Peek at the first few documents.

        Args:
            limit: Number of documents to peek

        Returns:
            Dictionary with documents and metadatas
        """
        return self.collection.peek(limit=limit)

    def reset(self) -> None:
        """Delete all documents from the collection."""
        try:
            self.client.delete_collection(name=self.collection_name)
            self._collection = None
            logger.warning(f"Collection '{self.collection_name}' reset")

        except Exception as e:
            logger.error(f"Error resetting collection: {e}")
            raise


# Global vector store service instance
vector_store = VectorStoreService()
