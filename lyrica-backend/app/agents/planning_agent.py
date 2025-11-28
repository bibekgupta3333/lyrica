"""
Planning Agent for Song Structure Design.

This agent analyzes the user's prompt and creates a structured plan
for the song, including sections, order, and overall structure.
"""

import asyncio
from typing import Dict, List

from loguru import logger

from app.agents.state import AgentState, AgentStatus, SongSection, SongStructure, WorkflowStatus
from app.services.llm import get_llm_service


class PlanningAgent:
    """
    Planning Agent responsible for designing song structure.

    This agent:
    1. Analyzes the user's prompt, genre, mood, and theme
    2. Determines appropriate song structure (verse-chorus, AABA, etc.)
    3. Plans the number and order of sections
    4. Sets mood and length guidelines for each section
    """

    def __init__(self, llm_provider: str = None):
        """
        Initialize the planning agent.

        Args:
            llm_provider: LLM provider to use (defaults to config)
        """
        self.name = "Planning"
        self.llm = get_llm_service(llm_provider)
        logger.info(f"Initialized {self.name} agent with provider: {llm_provider or 'default'}")

    async def run(self, state: AgentState) -> Dict:
        """
        Execute the planning agent.

        Args:
            state: Current agent state

        Returns:
            Dictionary with state updates
        """
        logger.info(f"{self.name} agent starting for user {state.user_id}")
        state.mark_agent_running(self.name)

        try:
            # Build planning prompt
            planning_prompt = self._build_planning_prompt(state)

            # Generate structure plan
            logger.debug(f"Generating song structure for prompt: {state.prompt[:100]}...")
            response = await asyncio.to_thread(self.llm.generate, planning_prompt)

            # Parse the structure from response
            structure = self._parse_structure_response(response, state)

            # Validate structure
            if not structure.sections:
                raise ValueError("Failed to generate valid song structure")

            logger.info(
                f"Generated structure with {structure.total_sections} sections: "
                f"{structure.structure_type}"
            )

            # Update state
            state.song_structure = structure
            state.workflow_status = WorkflowStatus.GENERATING
            state.mark_agent_completed(self.name)

            return {
                "song_structure": structure,
                "structure_reasoning": f"Created {structure.structure_type} structure with {structure.total_sections} sections",
                "planning_status": AgentStatus.COMPLETED,
                "workflow_status": WorkflowStatus.GENERATING,
            }

        except Exception as e:
            logger.error(f"{self.name} agent failed: {str(e)}")
            state.mark_agent_failed(self.name, str(e))
            return {
                "planning_status": AgentStatus.FAILED,
                "workflow_status": WorkflowStatus.FAILED,
                "errors": [f"Planning failed: {str(e)}"],
            }

    def _build_planning_prompt(self, state: AgentState) -> str:
        """Build the prompt for structure planning."""
        prompt = f"""You are a professional songwriter and music producer. Your task is to create a detailed structure plan for a song based on the following requirements:

**User Prompt:** {state.prompt}

**Genre:** {state.genre or 'Not specified'}
**Mood:** {state.mood or 'Not specified'}
**Theme:** {state.theme or 'Not specified'}
**Length:** {state.length or 'medium'}
**Style References:** {', '.join(state.style_references) if state.style_references else 'None'}

Please design a song structure that includes:

1. **Structure Type**: Choose an appropriate structure (e.g., Verse-Chorus, AABA, Verse-Chorus-Bridge)
2. **Sections**: List each section in order (e.g., Intro, Verse 1, Chorus, Verse 2, Chorus, Bridge, Chorus, Outro)
3. **Section Details**: For each section, specify:
   - Type (verse, chorus, bridge, intro, outro, pre-chorus)
   - Order/position in the song
   - Approximate length in lines (2-8 lines typically)
   - Mood/emotion for that section

Format your response as follows:

STRUCTURE_TYPE: [structure type name]
ESTIMATED_DURATION: [duration in seconds, e.g., 180]

SECTIONS:
1. INTRO | 2 lines | mood: mysterious
2. VERSE_1 | 8 lines | mood: reflective
3. CHORUS | 6 lines | mood: uplifting
[... continue for all sections]

REASONING: [Brief explanation of why this structure fits the song]

Now, create the structure plan:"""

        return prompt

    def _parse_structure_response(self, response: str, state: AgentState) -> SongStructure:
        """
        Parse the LLM response into a SongStructure object.

        Args:
            response: LLM response text
            state: Current agent state

        Returns:
            SongStructure object
        """
        sections: List[SongSection] = []
        structure_type = "verse-chorus"  # default
        estimated_duration = None

        lines = response.strip().split("\n")
        parsing_sections = False
        reasoning = ""

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Parse structure type
            if line.startswith("STRUCTURE_TYPE:"):
                structure_type = line.split(":", 1)[1].strip()

            # Parse estimated duration
            elif line.startswith("ESTIMATED_DURATION:"):
                try:
                    duration_str = line.split(":", 1)[1].strip()
                    estimated_duration = int("".join(filter(str.isdigit, duration_str)))
                except ValueError:
                    estimated_duration = 180  # default 3 minutes

            # Start parsing sections
            elif line.startswith("SECTIONS:"):
                parsing_sections = True

            # Parse reasoning
            elif line.startswith("REASONING:"):
                reasoning = line.split(":", 1)[1].strip()
                parsing_sections = False

            # Parse individual sections
            elif parsing_sections and "|" in line:
                try:
                    # Format: 1. VERSE_1 | 8 lines | mood: reflective
                    parts = line.split("|")
                    if len(parts) >= 2:
                        # Extract section type and number
                        section_part = parts[0].strip()
                        section_type = (
                            section_part.split(".", 1)[1].strip()
                            if "." in section_part
                            else section_part
                        )

                        # Extract length
                        length_part = parts[1].strip()
                        length = int("".join(filter(str.isdigit, length_part)))

                        # Extract mood
                        mood = None
                        if len(parts) >= 3:
                            mood_part = parts[2].strip()
                            if ":" in mood_part:
                                mood = mood_part.split(":", 1)[1].strip()

                        sections.append(
                            SongSection(
                                type=section_type.lower().replace("_", " "),
                                order=len(sections) + 1,
                                length=length,
                                mood=mood or state.mood,
                            )
                        )
                except Exception as e:
                    logger.warning(f"Failed to parse section line: {line} - {str(e)}")

        # If parsing failed, create default structure
        if not sections:
            sections = self._create_default_structure(state)
            structure_type = "verse-chorus (default)"

        return SongStructure(
            sections=sections,
            total_sections=len(sections),
            estimated_duration=estimated_duration or self._estimate_duration(sections),
            structure_type=structure_type,
        )

    def _create_default_structure(self, state: AgentState) -> List[SongSection]:
        """Create a default song structure if parsing fails."""
        logger.info("Creating default song structure")

        length_config = {
            "short": [
                ("verse 1", 6),
                ("chorus", 4),
                ("verse 2", 6),
                ("chorus", 4),
            ],
            "medium": [
                ("intro", 2),
                ("verse 1", 8),
                ("chorus", 6),
                ("verse 2", 8),
                ("chorus", 6),
                ("bridge", 6),
                ("chorus", 6),
                ("outro", 2),
            ],
            "long": [
                ("intro", 4),
                ("verse 1", 8),
                ("pre-chorus", 4),
                ("chorus", 8),
                ("verse 2", 8),
                ("pre-chorus", 4),
                ("chorus", 8),
                ("bridge", 8),
                ("chorus", 8),
                ("outro", 4),
            ],
        }

        sections_config = length_config.get(state.length, length_config["medium"])

        return [
            SongSection(
                type=section_type,
                order=idx + 1,
                length=length,
                mood=state.mood,
            )
            for idx, (section_type, length) in enumerate(sections_config)
        ]

    def _estimate_duration(self, sections: List[SongSection]) -> int:
        """
        Estimate song duration based on sections.

        Rough estimate: 3-5 seconds per line.
        """
        total_lines = sum(s.length or 4 for s in sections)
        return total_lines * 4  # 4 seconds per line average
