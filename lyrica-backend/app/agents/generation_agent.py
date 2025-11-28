"""
Generation Agent for Lyrics Creation.

This agent generates lyrics based on the song structure planned
by the Planning Agent, optionally using RAG for context.
"""

import asyncio
from typing import Dict, List

from loguru import logger

from app.agents.state import AgentState, AgentStatus, WorkflowStatus
from app.services.llm import get_llm_service
from app.services.rag import rag_service


class GenerationAgent:
    """
    Generation Agent responsible for creating song lyrics.

    This agent:
    1. Takes the planned song structure from Planning Agent
    2. Optionally retrieves relevant context using RAG
    3. Generates lyrics for each section
    4. Assembles the complete song
    """

    def __init__(self, llm_provider: str = None):
        """
        Initialize the generation agent.

        Args:
            llm_provider: LLM provider to use (defaults to config)
        """
        self.name = "Generation"
        self.llm = get_llm_service(llm_provider)
        logger.info(f"Initialized {self.name} agent with provider: {llm_provider or 'default'}")

    async def run(self, state: AgentState) -> Dict:
        """
        Execute the generation agent.

        Args:
            state: Current agent state

        Returns:
            Dictionary with state updates
        """
        logger.info(f"{self.name} agent starting for user {state.user_id}")
        state.mark_agent_running(self.name)

        try:
            # Validate that we have a structure
            if not state.song_structure or not state.song_structure.sections:
                raise ValueError("No song structure available from Planning Agent")

            # Retrieve RAG context if enabled
            rag_context = []
            if state.use_rag:
                logger.debug("Retrieving RAG context for generation")
                rag_context = await self._retrieve_rag_context(state)
                state.rag_context = rag_context

            # Generate lyrics for each section
            section_lyrics = []
            for section in state.song_structure.sections:
                logger.debug(f"Generating {section.type} (section {section.order})")
                section_text = await self._generate_section(section, state, rag_context)
                section.content = section_text
                section_lyrics.append(f"[{section.type.upper()}]\n{section_text}")

            # Assemble complete lyrics
            complete_lyrics = "\n\n".join(section_lyrics)

            # Generate title
            title = await self._generate_title(complete_lyrics, state)

            logger.info(
                f"Generated {len(section_lyrics)} sections, total length: {len(complete_lyrics)} chars"
            )

            # Update state
            state.generated_lyrics = complete_lyrics
            state.title = title
            state.workflow_status = WorkflowStatus.REFINING
            state.mark_agent_completed(self.name)

            return {
                "generated_lyrics": complete_lyrics,
                "title": title,
                "generation_metadata": {
                    "sections_count": len(section_lyrics),
                    "total_length": len(complete_lyrics),
                    "used_rag": state.use_rag,
                    "rag_context_count": len(rag_context),
                },
                "generation_status": AgentStatus.COMPLETED,
                "workflow_status": WorkflowStatus.REFINING,
            }

        except Exception as e:
            logger.error(f"{self.name} agent failed: {str(e)}")
            state.mark_agent_failed(self.name, str(e))
            return {
                "generation_status": AgentStatus.FAILED,
                "workflow_status": WorkflowStatus.FAILED,
                "errors": [f"Generation failed: {str(e)}"],
            }

    async def _retrieve_rag_context(self, state: AgentState) -> List[str]:
        """Retrieve relevant context from RAG system."""
        try:
            # Build search query from prompt and theme
            search_query = f"{state.prompt} {state.theme or ''} {state.genre or ''}"

            # Search vector store
            results = await rag_service.retrieve(
                query=search_query,
                collection_name="lyrics",
                n_results=5,
            )

            return [doc["content"] for doc in results]

        except Exception as e:
            logger.warning(f"Failed to retrieve RAG context: {str(e)}")
            return []

    async def _generate_section(self, section, state: AgentState, rag_context: List[str]) -> str:
        """
        Generate lyrics for a single section.

        Args:
            section: SongSection object
            state: Current agent state
            rag_context: Retrieved context from RAG

        Returns:
            Generated lyrics for the section
        """
        prompt = self._build_section_prompt(section, state, rag_context)

        # Generate with LLM
        response = await asyncio.to_thread(self.llm.generate, prompt)

        # Clean up response
        lyrics = self._clean_lyrics(response)

        return lyrics

    def _build_section_prompt(self, section, state: AgentState, rag_context: List[str]) -> str:
        """Build prompt for generating a specific section."""

        # Base context
        context = f"""You are a professional songwriter. Generate lyrics for the following section of a song:

**Song Context:**
- User Prompt: {state.prompt}
- Genre: {state.genre or 'Not specified'}
- Overall Mood: {state.mood or 'Not specified'}
- Theme: {state.theme or 'Not specified'}

**This Section:**
- Type: {section.type}
- Position: Section {section.order} of {state.song_structure.total_sections}
- Length: {section.length} lines
- Mood: {section.mood or state.mood or 'Not specified'}
"""

        # Add RAG context if available
        if rag_context:
            context += f"""
**Similar Lyrics (for inspiration):**
{chr(10).join(f"- {ctx[:200]}..." for ctx in rag_context[:3])}
"""

        # Add section-specific instructions
        section_instructions = self._get_section_instructions(section.type)
        context += f"\n**Instructions:**\n{section_instructions}\n"

        # Add constraints
        context += f"""
**Important:**
- Generate EXACTLY {section.length} lines
- Match the {section.mood or state.mood} mood
- Use vivid imagery and strong emotions
- Make it memorable and singable
- Do NOT include section labels like [VERSE] or [CHORUS]
- Output ONLY the lyrics, no explanations

Generate the {section.type} now:"""

        return context

    def _get_section_instructions(self, section_type: str) -> str:
        """Get specific instructions based on section type."""
        instructions = {
            "intro": "Create a captivating opening that sets the scene and draws listeners in.",
            "verse 1": "Establish the story, setting, and main character/perspective.",
            "verse 2": "Develop the narrative, add depth, show progression from verse 1.",
            "verse 3": "Bring new perspective or resolution to the story.",
            "chorus": "This is the emotional core and most memorable part. Make it powerful, repeatable, and catchy.",
            "pre-chorus": "Build anticipation and energy leading into the chorus.",
            "bridge": "Provide contrast, new perspective, or emotional climax. Change the pattern.",
            "outro": "Provide closure or leave a lasting impression. Can repeat key themes.",
        }

        # Normalize section type
        section_key = section_type.lower().strip()
        return instructions.get(
            section_key, "Create compelling, emotional lyrics that fit the song's narrative."
        )

    def _clean_lyrics(self, raw_text: str) -> str:
        """Clean up generated lyrics."""
        # Remove common artifacts
        text = raw_text.strip()

        # Remove section labels if LLM added them anyway
        lines = text.split("\n")
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            # Skip empty lines and section labels
            if not line or line.startswith("[") and line.endswith("]"):
                continue
            cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

    async def _generate_title(self, lyrics: str, state: AgentState) -> str:
        """
        Generate a title for the song.

        Args:
            lyrics: Complete generated lyrics
            state: Current agent state

        Returns:
            Generated song title
        """
        prompt = f"""Based on the following song lyrics, generate a compelling and memorable song title.

**Song Details:**
- Genre: {state.genre or 'Not specified'}
- Mood: {state.mood or 'Not specified'}
- Theme: {state.theme or 'Not specified'}

**Lyrics (excerpt):**
{lyrics[:500]}...

Generate a title that:
- Captures the essence of the song
- Is memorable and catchy
- Fits the genre and mood
- Is typically 1-5 words

Output ONLY the title, nothing else:"""

        response = await asyncio.to_thread(self.llm.generate, prompt)

        # Clean up title
        title = response.strip().strip("\"'")

        # Limit length
        if len(title) > 100:
            title = title[:100]

        return title
