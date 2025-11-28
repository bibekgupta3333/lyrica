"""
RAG (Retrieval-Augmented Generation) Service
Combines vector search with LLM generation using flexible multi-provider LLM support.
"""

from typing import Any, Dict, List, Optional

from loguru import logger

from app.core.config import settings
from app.services.llm import BaseLLMService, get_llm_service
from app.services.vector_store import vector_store


class RAGService:
    """Service for Retrieval-Augmented Generation."""

    def __init__(self, provider: Optional[str] = None):
        """
        Initialize RAG service.

        Args:
            provider: Optional LLM provider override (ollama, openai, gemini, grok)
        """
        self.llm: Optional[BaseLLMService] = None
        self.provider_override = provider
        self.top_k = 5
        self.similarity_threshold = 0.7
        logger.info(f"RAG service initialized (provider: {provider or settings.llm_provider})")

    def _get_llm(self) -> BaseLLMService:
        """Get or create LLM instance."""
        if self.llm is None:
            self.llm = get_llm_service(self.provider_override)
            model_info = self.llm.get_model_info()
            logger.info(f"LLM service ready: {model_info['provider']} - {model_info['model']}")
        return self.llm

    async def retrieve(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query.

        Args:
            query: Search query
            n_results: Number of results to return
            filters: Optional metadata filters

        Returns:
            List of retrieved documents with metadata
        """
        logger.info(f"Retrieving documents for query: '{query[:100]}...'")

        # Search vector store
        results = await vector_store.search(query=query, n_results=n_results, where=filters)

        # Format results
        retrieved_docs = []
        for i in range(len(results["ids"])):
            doc = {
                "id": results["ids"][i],
                "text": results["documents"][i],
                "metadata": results["metadatas"][i],
                "distance": results["distances"][i],
                "score": 1 - results["distances"][i],  # Convert distance to similarity
            }
            retrieved_docs.append(doc)

        logger.info(f"Retrieved {len(retrieved_docs)} documents")
        return retrieved_docs

    async def generate(
        self,
        query: str,
        context: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate response using retrieved context.

        Args:
            query: User query
            context: Retrieved documents
            system_prompt: Optional system prompt

        Returns:
            Generated response
        """
        # Build prompt with context
        context_text = self._format_context(context)

        if system_prompt is None:
            system_prompt = (
                "You are a helpful AI assistant that generates song lyrics. "
                "Use the provided context to inform your response, but be creative "
                "and original in your generation."
            )

        full_prompt = f"""{system_prompt}

Context:
{context_text}

Query: {query}

Response:"""

        logger.info("Generating response with LLM")

        try:
            llm = self._get_llm()
            # Use the new flexible LLM service
            llm_response = await llm.generate(query, system_prompt=full_prompt)
            logger.info(f"Response generated successfully (tokens: {llm_response.tokens_used})")
            return llm_response.content

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    async def retrieve_and_generate(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Complete RAG pipeline: retrieve and generate.

        Args:
            query: User query
            n_results: Number of documents to retrieve
            filters: Optional metadata filters
            system_prompt: Optional system prompt

        Returns:
            Dictionary with response and retrieved context
        """
        logger.info(f"Starting RAG pipeline for: '{query[:100]}...'")

        # Retrieve relevant documents
        context = await self.retrieve(query=query, n_results=n_results, filters=filters)

        # Filter by similarity threshold
        filtered_context = [doc for doc in context if doc["score"] >= self.similarity_threshold]

        if not filtered_context:
            logger.warning(f"No documents above similarity threshold {self.similarity_threshold}")
            filtered_context = context[:1] if context else []

        # Generate response
        response = await self.generate(
            query=query, context=filtered_context, system_prompt=system_prompt
        )

        result = {
            "query": query,
            "response": response,
            "context": filtered_context,
            "num_retrieved": len(context),
            "num_used": len(filtered_context),
        }

        logger.info("RAG pipeline complete")
        return result

    async def retrieve_similar_lyrics(
        self,
        query: str,
        genre: Optional[str] = None,
        mood: Optional[str] = None,
        n_results: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar lyrics for inspiration.

        Args:
            query: Query text (theme, style, or partial lyrics)
            genre: Optional genre filter
            mood: Optional mood filter
            n_results: Number of results to return

        Returns:
            List of similar lyrics with metadata
        """
        # Build filters
        filters = {}
        if genre:
            filters["genre"] = genre
        if mood:
            filters["mood"] = mood

        # Ensure we only get lyrics
        filters["doc_type"] = "lyrics"

        logger.info(f"Searching for similar lyrics (genre={genre}, mood={mood}, n={n_results})")

        return await self.retrieve(query=query, n_results=n_results, filters=filters)

    async def generate_lyrics_with_context(
        self,
        theme: str,
        genre: Optional[str] = None,
        mood: Optional[str] = None,
        structure: Optional[str] = None,
        n_context_docs: int = 3,
    ) -> Dict[str, Any]:
        """
        Generate lyrics using RAG with similar lyrics as context.

        Args:
            theme: Lyrics theme/topic
            genre: Music genre
            mood: Mood/emotion
            structure: Song structure (e.g., "verse-chorus-verse-chorus-bridge-chorus")
            n_context_docs: Number of context documents to use

        Returns:
            Dictionary with generated lyrics and context
        """
        # Retrieve similar lyrics
        similar_lyrics = await self.retrieve_similar_lyrics(
            query=theme, genre=genre, mood=mood, n_results=n_context_docs
        )

        # Build system prompt
        structure_text = structure or "verse-chorus-verse-chorus-bridge-chorus"
        system_prompt = f"""You are a creative songwriter. Generate original song lyrics based on the theme and style.

Theme: {theme}
Genre: {genre or 'any'}
Mood: {mood or 'any'}
Structure: {structure_text}

Use the provided similar lyrics for inspiration on style and structure, but create completely original content.
Format the lyrics with clear section labels like [Verse 1], [Chorus], [Bridge], etc."""

        # Generate lyrics
        result = await self.retrieve_and_generate(
            query=f"Write lyrics about: {theme}",
            n_results=n_context_docs,
            filters={"doc_type": "lyrics"},
            system_prompt=system_prompt,
        )

        # Add generation parameters to result
        result["theme"] = theme
        result["genre"] = genre
        result["mood"] = mood
        result["structure"] = structure_text

        return result

    def _format_context(self, context: List[Dict[str, Any]]) -> str:
        """Format retrieved context for prompt."""
        if not context:
            return "No relevant context available."

        formatted = []
        for i, doc in enumerate(context, 1):
            metadata = doc.get("metadata", {})
            title = metadata.get("title", "Untitled")
            score = doc.get("score", 0)

            formatted.append(
                f"[Document {i}] (Relevance: {score:.2f})\n" f"Title: {title}\n" f"{doc['text']}\n"
            )

        return "\n---\n".join(formatted)

    def set_similarity_threshold(self, threshold: float):
        """Set the similarity threshold for filtering results."""
        if not 0 <= threshold <= 1:
            raise ValueError("Threshold must be between 0 and 1")
        self.similarity_threshold = threshold
        logger.info(f"Similarity threshold set to {threshold}")


# Global RAG service instance
rag_service = RAGService()
