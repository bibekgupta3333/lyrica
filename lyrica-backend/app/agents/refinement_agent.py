"""
Refinement Agent for Lyrics Quality Improvement.

This agent reviews and refines generated lyrics to improve
quality, coherence, rhyme scheme, and emotional impact.
"""

import asyncio
from typing import Dict, List

from loguru import logger

from app.agents.state import AgentState, AgentStatus, WorkflowStatus
from app.services.llm import get_llm_service


class RefinementAgent:
    """
    Refinement Agent responsible for improving lyrics quality.

    This agent:
    1. Reviews generated lyrics from Generation Agent
    2. Identifies areas for improvement
    3. Refines lyrics for better flow, rhyme, and impact
    4. Can iterate multiple times if needed
    """

    def __init__(self, llm_provider: str = None, max_iterations: int = 2):
        """
        Initialize the refinement agent.

        Args:
            llm_provider: LLM provider to use (defaults to config)
            max_iterations: Maximum number of refinement iterations
        """
        self.name = "Refinement"
        self.llm = get_llm_service(llm_provider)
        self.max_iterations = max_iterations
        logger.info(
            f"Initialized {self.name} agent with provider: {llm_provider or 'default'}, "
            f"max_iterations: {max_iterations}"
        )

    async def run(self, state: AgentState) -> Dict:
        """
        Execute the refinement agent.

        Args:
            state: Current agent state

        Returns:
            Dictionary with state updates
        """
        logger.info(f"{self.name} agent starting for user {state.user_id}")
        state.mark_agent_running(self.name)

        try:
            # Validate that we have generated lyrics
            if not state.generated_lyrics:
                raise ValueError("No generated lyrics available from Generation Agent")

            current_lyrics = state.generated_lyrics
            refinement_changes = []
            iterations = 0

            # Iterative refinement
            while iterations < self.max_iterations:
                iterations += 1
                logger.debug(f"Refinement iteration {iterations}/{self.max_iterations}")

                # Analyze current lyrics
                issues = await self._analyze_lyrics(current_lyrics, state)

                # If no significant issues, we're done
                if not issues or self._is_quality_acceptable(issues):
                    logger.info(f"Lyrics quality acceptable after {iterations} iteration(s)")
                    break

                # Refine lyrics
                refined = await self._refine_lyrics(current_lyrics, issues, state)

                # Track changes
                changes_made = self._compare_versions(current_lyrics, refined)
                refinement_changes.extend(changes_made)

                current_lyrics = refined

            # Update song sections with refined content
            if state.song_structure:
                self._update_sections_with_refined_lyrics(current_lyrics, state)

            logger.info(
                f"Refinement completed after {iterations} iteration(s), "
                f"{len(refinement_changes)} changes made"
            )

            # Update state
            state.refined_lyrics = current_lyrics
            state.refinement_iterations = iterations
            state.refinement_changes = refinement_changes
            state.workflow_status = WorkflowStatus.EVALUATING
            state.mark_agent_completed(self.name)

            return {
                "refined_lyrics": current_lyrics,
                "refinement_changes": refinement_changes,
                "refinement_iterations": iterations,
                "refinement_status": AgentStatus.COMPLETED,
                "workflow_status": WorkflowStatus.EVALUATING,
            }

        except Exception as e:
            logger.error(f"{self.name} agent failed: {str(e)}")
            state.mark_agent_failed(self.name, str(e))
            return {
                "refinement_status": AgentStatus.FAILED,
                "workflow_status": WorkflowStatus.FAILED,
                "errors": [f"Refinement failed: {str(e)}"],
            }

    async def _analyze_lyrics(self, lyrics: str, state: AgentState) -> List[str]:
        """
        Analyze lyrics to identify issues and areas for improvement.

        Args:
            lyrics: Current lyrics text
            state: Current agent state

        Returns:
            List of identified issues
        """
        prompt = f"""You are a professional songwriter and lyrics editor. Analyze the following song lyrics and identify any issues or areas for improvement.

**Song Context:**
- Genre: {state.genre or 'Not specified'}
- Mood: {state.mood or 'Not specified'}
- Theme: {state.theme or 'Not specified'}

**Lyrics:**
{lyrics}

**Analysis Criteria:**
1. Rhyme scheme consistency
2. Syllable count and rhythm
3. Emotional coherence
4. Imagery and metaphors
5. Clichés or overused phrases
6. Flow between sections
7. Overall impact and memorability

**Instructions:**
- List specific issues you find (be critical but constructive)
- Focus on the most important improvements
- If lyrics are already excellent, say "NO_ISSUES"

Output format:
ISSUE: [brief description of issue]
ISSUE: [another issue]
...

Analyze now:"""

        llm_response = await self.llm.generate(prompt)
        response = llm_response.content

        # Parse issues from response
        issues = []
        for line in response.strip().split("\n"):
            line = line.strip()
            if line.startswith("ISSUE:"):
                issue = line.replace("ISSUE:", "").strip()
                if issue:
                    issues.append(issue)
            elif "NO_ISSUES" in line.upper():
                return []

        return issues

    def _is_quality_acceptable(self, issues: List[str]) -> bool:
        """
        Determine if issues are minor enough to accept current quality.

        Args:
            issues: List of identified issues

        Returns:
            True if quality is acceptable, False otherwise
        """
        # If very few issues, accept
        if len(issues) <= 2:
            return True

        # Check if issues are minor (contain keywords like "minor", "slight", "small")
        minor_keywords = ["minor", "slight", "small", "tiny", "could be"]
        minor_count = sum(
            1 for issue in issues if any(keyword in issue.lower() for keyword in minor_keywords)
        )

        # If most issues are minor, accept
        if minor_count >= len(issues) * 0.7:
            return True

        return False

    async def _refine_lyrics(self, lyrics: str, issues: List[str], state: AgentState) -> str:
        """
        Refine lyrics based on identified issues.

        Args:
            lyrics: Current lyrics
            issues: List of issues to address
            state: Current agent state

        Returns:
            Refined lyrics
        """
        issues_text = "\n".join(f"- {issue}" for issue in issues)

        prompt = f"""You are a professional songwriter and lyrics editor. Refine the following song lyrics to address the identified issues while maintaining the song's essence and structure.

**Song Context:**
- Genre: {state.genre or 'Not specified'}
- Mood: {state.mood or 'Not specified'}
- Theme: {state.theme or 'Not specified'}

**Current Lyrics:**
{lyrics}

**Issues to Address:**
{issues_text}

**Instructions:**
- Keep the same structure and section labels
- Maintain the core theme and narrative
- Address the issues while improving overall quality
- Keep the same number of lines per section
- Output ONLY the refined lyrics, no explanations

Refined lyrics:"""

        llm_response = await self.llm.generate(prompt)
        response = llm_response.content

        return response.strip()

    def _compare_versions(self, original: str, refined: str) -> List[str]:
        """
        Compare two versions and identify changes made.

        Args:
            original: Original lyrics
            refined: Refined lyrics

        Returns:
            List of changes made
        """
        changes = []

        # Simple comparison (could be enhanced with diff algorithms)
        original_lines = original.strip().split("\n")
        refined_lines = refined.strip().split("\n")

        for i, (orig, ref) in enumerate(zip(original_lines, refined_lines)):
            if orig.strip() != ref.strip():
                changes.append(f"Line {i+1}: Changed wording for better flow/rhyme")

        # Check if lines were added or removed
        if len(refined_lines) != len(original_lines):
            diff = len(refined_lines) - len(original_lines)
            if diff > 0:
                changes.append(f"Added {diff} line(s) for better structure")
            else:
                changes.append(f"Removed {abs(diff)} line(s) for better conciseness")

        return changes[:10]  # Limit to top 10 changes for brevity

    def _update_sections_with_refined_lyrics(self, refined_lyrics: str, state: AgentState) -> None:
        """
        Update individual song sections with refined content.

        Args:
            refined_lyrics: Complete refined lyrics
            state: Current agent state
        """
        if not state.song_structure or not state.song_structure.sections:
            return

        # Split refined lyrics by section
        sections = refined_lyrics.split("\n\n")
        current_section_idx = 0

        for section_text in sections:
            # Extract content (skip section label line)
            lines = section_text.strip().split("\n")
            if lines and lines[0].startswith("[") and lines[0].endswith("]"):
                content = "\n".join(lines[1:])
            else:
                content = section_text.strip()

            # Update corresponding section
            if current_section_idx < len(state.song_structure.sections):
                section = state.song_structure.sections[current_section_idx]
                section.content = content
                section.refined = True
                current_section_idx += 1
