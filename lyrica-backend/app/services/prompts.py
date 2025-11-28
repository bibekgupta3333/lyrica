"""
Prompt templates for lyrics generation.

This module provides structured prompt templates for consistent
and high-quality lyrics generation across different styles and genres.
"""

from typing import Optional


class PromptTemplate:
    """Base class for prompt templates."""

    @staticmethod
    def format(**kwargs) -> str:
        """Format template with provided kwargs."""
        raise NotImplementedError


class LyricsGenerationPrompt(PromptTemplate):
    """Template for generating complete lyrics."""

    TEMPLATE = """Generate song lyrics based on the following requirements:

**Prompt:** {prompt}
**Genre:** {genre}
**Mood:** {mood}
**Theme:** {theme}
**Length:** {length} (short=1-2 verses, medium=2-3 verses, long=3-4 verses)

**Requirements:**
- Create a complete song with proper structure
- Include clear section markers ([Verse 1], [Chorus], [Bridge], etc.)
- Match the specified genre and mood
- Use appropriate rhyme schemes
- Create memorable hooks and choruses
- Maintain consistent theme throughout
- Use vivid imagery and metaphors

**Structure Guidelines:**
- Start with [Intro] or [Verse 1]
- Alternate between verses and chorus
- Include a bridge if length is medium/long
- End with final chorus or [Outro]

Generate creative and engaging lyrics now:"""

    @staticmethod
    def format(
        prompt: str,
        genre: str = "pop",
        mood: str = "neutral",
        theme: Optional[str] = None,
        length: str = "medium",
    ) -> str:
        """
        Format lyrics generation prompt.

        Args:
            prompt: User's prompt/idea
            genre: Musical genre
            mood: Emotional mood
            theme: Optional theme
            length: Song length (short/medium/long)

        Returns:
            Formatted prompt string
        """
        return LyricsGenerationPrompt.TEMPLATE.format(
            prompt=prompt,
            genre=genre,
            mood=mood,
            theme=theme or "general",
            length=length,
        )


class VersGenerationPrompt(PromptTemplate):
    """Template for generating a single verse."""

    TEMPLATE = """Generate a single {verse_type} for a {genre} song:

**Song Context:**
Title: {title}
Genre: {genre}
Mood: {mood}
Current Structure:
{context}

**Requirements:**
- Generate only the {verse_type} content (no section marker)
- Match the established style and rhyme scheme
- Connect smoothly with previous sections
- Maintain consistent theme and tone
- {lines_count} lines

Generate the {verse_type} content:"""

    @staticmethod
    def format(
        verse_type: str,
        title: str,
        genre: str,
        mood: str,
        context: str,
        lines_count: int = 4,
    ) -> str:
        """Format verse generation prompt."""
        return VersGenerationPrompt.TEMPLATE.format(
            verse_type=verse_type,
            title=title,
            genre=genre,
            mood=mood,
            context=context,
            lines_count=lines_count,
        )


class RefinementPrompt(PromptTemplate):
    """Template for refining existing lyrics."""

    TEMPLATE = """Refine and improve the following song lyrics:

**Original Lyrics:**
{original_lyrics}

**Genre:** {genre}
**Mood:** {mood}
**Improvement Focus:** {focus}

**Requirements:**
- Maintain the overall structure and theme
- Improve word choice and imagery
- Enhance rhyme quality if needed
- Strengthen emotional impact
- Keep the same section markers
- {improvement_instructions}

Provide the refined version:"""

    @staticmethod
    def format(
        original_lyrics: str,
        genre: str,
        mood: str,
        focus: str = "overall quality",
        improvement_instructions: str = "Make it more creative and engaging",
    ) -> str:
        """Format refinement prompt."""
        return RefinementPrompt.TEMPLATE.format(
            original_lyrics=original_lyrics,
            genre=genre,
            mood=mood,
            focus=focus,
            improvement_instructions=improvement_instructions,
        )


class SongPlanningPrompt(PromptTemplate):
    """Template for planning song structure."""

    TEMPLATE = """Plan the structure for a song based on these requirements:

**Prompt:** {prompt}
**Genre:** {genre}
**Mood:** {mood}
**Length:** {length}

**Task:**
Create a JSON structure defining the song sections (verses, chorus, bridge, etc.).

**Format:**
{{
  "title": "Song Title",
  "sections": [
    {{"type": "verse", "number": 1, "order": 0, "lines": 4, "theme": "introduction"}},
    {{"type": "chorus", "number": 1, "order": 1, "lines": 4, "theme": "main hook"}},
    ...
  ],
  "rhyme_scheme": "AABB",
  "estimated_duration": "3:30"
}}

Generate the song structure plan:"""

    @staticmethod
    def format(
        prompt: str, genre: str = "pop", mood: str = "neutral", length: str = "medium"
    ) -> str:
        """Format planning prompt."""
        return SongPlanningPrompt.TEMPLATE.format(
            prompt=prompt, genre=genre, mood=mood, length=length
        )


class EvaluationPrompt(PromptTemplate):
    """Template for evaluating lyrics quality."""

    TEMPLATE = """Evaluate the quality of these song lyrics:

**Lyrics:**
{lyrics}

**Genre:** {genre}
**Mood:** {mood}

**Evaluation Criteria:**
Rate each aspect from 0-10:

1. **Creativity**: Originality and unique expressions
2. **Coherence**: Logical flow and consistency
3. **Rhyme Quality**: Rhyme scheme and execution
4. **Emotional Impact**: Ability to evoke emotions
5. **Genre Fit**: Alignment with {genre} genre
6. **Mood Match**: Match with {mood} mood

**Format your response as JSON:**
{{
  "overall": 8.5,
  "creativity": 9.0,
  "coherence": 8.0,
  "rhyme_quality": 8.5,
  "emotional_impact": 9.0,
  "genre_fit": 8.0,
  "mood_match": 8.5,
  "feedback": "Brief constructive feedback",
  "suggestions": ["Suggestion 1", "Suggestion 2"]
}}

Provide your evaluation:"""

    @staticmethod
    def format(lyrics: str, genre: str, mood: str) -> str:
        """Format evaluation prompt."""
        return EvaluationPrompt.TEMPLATE.format(lyrics=lyrics, genre=genre, mood=mood)


# ============================================================================
# Convenience Functions
# ============================================================================


def get_generation_prompt(
    prompt: str,
    genre: str = "pop",
    mood: str = "neutral",
    theme: Optional[str] = None,
    length: str = "medium",
) -> str:
    """Get formatted lyrics generation prompt."""
    return LyricsGenerationPrompt.format(
        prompt=prompt, genre=genre, mood=mood, theme=theme, length=length
    )


def get_refinement_prompt(
    original_lyrics: str,
    genre: str,
    mood: str,
    focus: str = "overall quality",
) -> str:
    """Get formatted refinement prompt."""
    return RefinementPrompt.format(
        original_lyrics=original_lyrics, genre=genre, mood=mood, focus=focus
    )


def get_planning_prompt(
    prompt: str, genre: str = "pop", mood: str = "neutral", length: str = "medium"
) -> str:
    """Get formatted planning prompt."""
    return SongPlanningPrompt.format(prompt=prompt, genre=genre, mood=mood, length=length)


def get_evaluation_prompt(lyrics: str, genre: str, mood: str) -> str:
    """Get formatted evaluation prompt."""
    return EvaluationPrompt.format(lyrics=lyrics, genre=genre, mood=mood)
