"""
Text Chunking Utilities
Provides various strategies for splitting text into chunks for embedding.
"""

import re
from typing import List, Optional

from loguru import logger

from app.core.config import settings


class TextChunker:
    """Utility class for splitting text into chunks."""

    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        separator: str = "\n\n",
    ):
        """
        Initialize the text chunker.

        Args:
            chunk_size: Maximum size of each chunk (characters)
            chunk_overlap: Number of characters to overlap between chunks
            separator: Primary separator for splitting text
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        self.separator = separator

    def chunk_text(
        self, text: str, strategy: str = "recursive", metadata: Optional[dict] = None
    ) -> List[dict]:
        """
        Split text into chunks using specified strategy.

        Args:
            text: Text to split
            strategy: Chunking strategy (recursive, fixed, sentence, paragraph)
            metadata: Optional metadata to attach to each chunk

        Returns:
            List of chunk dictionaries with text and metadata
        """
        if not text or not text.strip():
            return []

        if strategy == "recursive":
            chunks = self._recursive_chunk(text)
        elif strategy == "fixed":
            chunks = self._fixed_chunk(text)
        elif strategy == "sentence":
            chunks = self._sentence_chunk(text)
        elif strategy == "paragraph":
            chunks = self._paragraph_chunk(text)
        else:
            logger.warning(f"Unknown chunking strategy: {strategy}, using recursive")
            chunks = self._recursive_chunk(text)

        # Add metadata to chunks
        chunk_dicts = []
        for i, chunk_text in enumerate(chunks):
            chunk_dict = {
                "text": chunk_text,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "chunk_size": len(chunk_text),
            }
            if metadata:
                chunk_dict.update(metadata)
            chunk_dicts.append(chunk_dict)

        logger.info(f"Split text into {len(chunk_dicts)} chunks using {strategy} strategy")
        return chunk_dicts

    def _recursive_chunk(self, text: str) -> List[str]:
        """
        Recursively split text using multiple separators.
        Best for general text with natural structure.
        """
        separators = ["\n\n", "\n", ". ", " ", ""]
        return self._split_text_recursive(text, separators)

    def _split_text_recursive(self, text: str, separators: List[str]) -> List[str]:
        """Recursively split text using a list of separators."""
        if not separators:
            # Base case: split by characters
            return self._fixed_chunk(text)

        separator = separators[0]
        remaining_separators = separators[1:]

        if separator:
            splits = text.split(separator)
        else:
            splits = list(text)

        chunks = []
        current_chunk = ""

        for split in splits:
            # Add separator back (except for last split)
            if separator and split != splits[-1]:
                split = split + separator

            # If adding this split would exceed chunk size, process recursively
            if len(current_chunk) + len(split) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""

                # If split itself is too large, process with next separator
                if len(split) > self.chunk_size:
                    sub_chunks = self._split_text_recursive(split, remaining_separators)
                    chunks.extend(sub_chunks)
                else:
                    current_chunk = split
            else:
                current_chunk += split

        if current_chunk:
            chunks.append(current_chunk)

        # Apply overlap
        if self.chunk_overlap > 0 and len(chunks) > 1:
            chunks = self._apply_overlap(chunks)

        return chunks

    def _fixed_chunk(self, text: str) -> List[str]:
        """
        Split text into fixed-size chunks.
        Simple but may break words/sentences.
        """
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]

            # Try to break at word boundary
            if end < len(text) and not text[end].isspace():
                last_space = chunk.rfind(" ")
                if last_space > 0:
                    end = start + last_space

            chunks.append(text[start:end].strip())
            start = end - self.chunk_overlap

        return [c for c in chunks if c]

    def _sentence_chunk(self, text: str) -> List[str]:
        """
        Split text by sentences, grouping them into chunks.
        Best for text with clear sentence structure.
        """
        # Split into sentences (simple regex)
        sentences = re.split(r"(?<=[.!?])\s+", text)

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _paragraph_chunk(self, text: str) -> List[str]:
        """
        Split text by paragraphs, combining small paragraphs.
        Best for documents with paragraph structure.
        """
        paragraphs = text.split("\n\n")

        chunks = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current_chunk) + len(para) <= self.chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())

                # If single paragraph is too large, split it
                if len(para) > self.chunk_size:
                    sub_chunks = self._recursive_chunk(para)
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = para + "\n\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _apply_overlap(self, chunks: List[str]) -> List[str]:
        """Apply overlap between consecutive chunks."""
        if not chunks or self.chunk_overlap <= 0:
            return chunks

        overlapped_chunks = [chunks[0]]

        for i in range(1, len(chunks)):
            prev_chunk = chunks[i - 1]
            current_chunk = chunks[i]

            # Get overlap from previous chunk
            if len(prev_chunk) >= self.chunk_overlap:
                overlap_text = prev_chunk[-self.chunk_overlap :]
                # Only add overlap if current chunk doesn't already start with it
                if not current_chunk.startswith(overlap_text):
                    current_chunk = overlap_text + current_chunk

            overlapped_chunks.append(current_chunk)

        return overlapped_chunks

    @staticmethod
    def chunk_lyrics(lyrics_text: str, metadata: Optional[dict] = None) -> List[dict]:
        """
        Specialized chunking for lyrics text.
        Preserves verse/chorus structure.

        Args:
            lyrics_text: Lyrics text to chunk
            metadata: Optional metadata

        Returns:
            List of chunk dictionaries
        """
        # Split by common section markers
        section_pattern = r"\n\n(?=\[|\(|Verse|Chorus|Bridge|Intro|Outro)"
        sections = re.split(section_pattern, lyrics_text)

        chunks = []
        for i, section in enumerate(sections):
            section = section.strip()
            if not section:
                continue

            chunk_dict = {
                "text": section,
                "chunk_index": i,
                "total_chunks": len(sections),
                "chunk_size": len(section),
                "is_lyrics": True,
            }
            if metadata:
                chunk_dict.update(metadata)
            chunks.append(chunk_dict)

        return chunks


# Global text chunker instance
text_chunker = TextChunker()


# Convenience functions for easy imports
def chunk_text(
    text: str,
    max_chunk_size: int = 512,
    overlap: int = 50,
    strategy: str = "recursive",
    metadata: Optional[dict] = None,
) -> List[str]:
    """
    Convenience function to chunk text.

    Args:
        text: Text to chunk
        max_chunk_size: Maximum chunk size in characters
        overlap: Overlap between chunks
        strategy: Chunking strategy
        metadata: Optional metadata

    Returns:
        List of text chunks (strings)
    """
    chunker = TextChunker(chunk_size=max_chunk_size, chunk_overlap=overlap)

    # Use lyrics strategy if specified
    if strategy == "lyrics":
        chunk_dicts = TextChunker.chunk_lyrics(text, metadata)
    else:
        chunk_dicts = chunker.chunk_text(text, strategy, metadata)

    # Return just the text strings for backward compatibility
    return [chunk["text"] for chunk in chunk_dicts]


def chunk_lyrics(lyrics_text: str, metadata: Optional[dict] = None) -> List[str]:
    """
    Convenience function to chunk lyrics text.

    Args:
        lyrics_text: Lyrics to chunk
        metadata: Optional metadata

    Returns:
        List of lyric chunks (strings)
    """
    chunk_dicts = TextChunker.chunk_lyrics(lyrics_text, metadata)
    return [chunk["text"] for chunk in chunk_dicts]
