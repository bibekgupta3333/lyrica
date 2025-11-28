"""
Evaluation Agent for Lyrics Quality Assessment.

This agent evaluates the quality of refined lyrics and provides
scores and feedback on various dimensions.
"""

import asyncio
import re
from typing import Dict

from loguru import logger

from app.agents.state import AgentState, AgentStatus, EvaluationScore, WorkflowStatus
from app.services.llm import get_llm_service


class EvaluationAgent:
    """
    Evaluation Agent responsible for assessing lyrics quality.

    This agent:
    1. Evaluates refined lyrics on multiple dimensions
    2. Provides numerical scores (0-10 scale)
    3. Generates detailed feedback and suggestions
    4. Determines if lyrics meet quality threshold
    """

    def __init__(
        self,
        llm_provider: str = None,
        quality_threshold: float = 6.5,
    ):
        """
        Initialize the evaluation agent.

        Args:
            llm_provider: LLM provider to use (defaults to config)
            quality_threshold: Minimum acceptable overall score (0-10)
        """
        self.name = "Evaluation"
        self.llm = get_llm_service(llm_provider)
        self.quality_threshold = quality_threshold
        logger.info(
            f"Initialized {self.name} agent with provider: {llm_provider or 'default'}, "
            f"threshold: {quality_threshold}"
        )

    async def run(self, state: AgentState) -> Dict:
        """
        Execute the evaluation agent.

        Args:
            state: Current agent state

        Returns:
            Dictionary with state updates
        """
        logger.info(f"{self.name} agent starting for user {state.user_id}")
        state.mark_agent_running(self.name)

        try:
            # Determine which lyrics to evaluate
            lyrics_to_evaluate = state.refined_lyrics or state.generated_lyrics

            if not lyrics_to_evaluate:
                raise ValueError("No lyrics available for evaluation")

            # Perform evaluation
            logger.debug("Evaluating lyrics quality...")
            evaluation = await self._evaluate_lyrics(lyrics_to_evaluate, state)

            # Determine if regeneration is needed
            needs_regeneration = evaluation.overall < self.quality_threshold

            # Set final lyrics if quality is acceptable
            final_lyrics = None
            if not needs_regeneration:
                final_lyrics = lyrics_to_evaluate
                workflow_status = WorkflowStatus.COMPLETED
                logger.info(f"Lyrics approved! Overall score: {evaluation.overall:.2f}/10")
            else:
                workflow_status = WorkflowStatus.FAILED
                logger.warning(
                    f"Lyrics below threshold ({evaluation.overall:.2f} < {self.quality_threshold})"
                )

            # Update state
            state.evaluation_score = evaluation
            state.needs_regeneration = needs_regeneration
            state.final_lyrics = final_lyrics
            state.workflow_status = workflow_status
            state.mark_agent_completed(self.name)

            return {
                "evaluation_score": evaluation,
                "needs_regeneration": needs_regeneration,
                "final_lyrics": final_lyrics,
                "evaluation_status": AgentStatus.COMPLETED,
                "workflow_status": workflow_status,
            }

        except Exception as e:
            logger.error(f"{self.name} agent failed: {str(e)}")
            state.mark_agent_failed(self.name, str(e))
            return {
                "evaluation_status": AgentStatus.FAILED,
                "workflow_status": WorkflowStatus.FAILED,
                "errors": [f"Evaluation failed: {str(e)}"],
            }

    async def _evaluate_lyrics(self, lyrics: str, state: AgentState) -> EvaluationScore:
        """
        Evaluate lyrics and generate scores.

        Args:
            lyrics: Lyrics to evaluate
            state: Current agent state

        Returns:
            EvaluationScore object with scores and feedback
        """
        prompt = self._build_evaluation_prompt(lyrics, state)

        # Get evaluation from LLM
        response = await asyncio.to_thread(self.llm.generate, prompt)

        # Parse scores and feedback
        evaluation = self._parse_evaluation_response(response)

        return evaluation

    def _build_evaluation_prompt(self, lyrics: str, state: AgentState) -> str:
        """Build prompt for lyrics evaluation."""
        return f"""You are an expert music critic and songwriting instructor. Evaluate the following song lyrics on multiple dimensions and provide detailed scores and feedback.

**Song Context:**
- Genre: {state.genre or 'Not specified'}
- Mood: {state.mood or 'Not specified'}
- Theme: {state.theme or 'Not specified'}
- User Prompt: {state.prompt}

**Lyrics to Evaluate:**
{lyrics}

**Evaluation Criteria:**

Rate each dimension on a scale of 0-10 (where 10 is exceptional):

1. **CREATIVITY** (0-10): Originality, unique perspectives, fresh language
2. **COHERENCE** (0-10): Logical flow, narrative consistency, thematic unity
3. **RHYME_QUALITY** (0-10): Rhyme scheme effectiveness, natural flow, not forced
4. **EMOTIONAL_IMPACT** (0-10): Emotional resonance, ability to connect with listeners
5. **GENRE_FIT** (0-10): How well it fits the intended genre and style

**Instructions:**
- Be objective and critical
- Provide specific examples for your ratings
- Suggest concrete improvements
- Calculate overall score as average of all dimensions

**Output Format:**

CREATIVITY: [score] | [brief justification]
COHERENCE: [score] | [brief justification]
RHYME_QUALITY: [score] | [brief justification]
EMOTIONAL_IMPACT: [score] | [brief justification]
GENRE_FIT: [score] | [brief justification]
OVERALL: [average score]

FEEDBACK:
[Detailed feedback about strengths and weaknesses]

SUGGESTIONS:
- [Specific suggestion 1]
- [Specific suggestion 2]
- [Specific suggestion 3]

Evaluate now:"""

    def _parse_evaluation_response(self, response: str) -> EvaluationScore:
        """
        Parse LLM evaluation response into EvaluationScore.

        Args:
            response: LLM response text

        Returns:
            EvaluationScore object
        """
        # Initialize default scores
        scores = {
            "creativity": 7.0,
            "coherence": 7.0,
            "rhyme_quality": 7.0,
            "emotional_impact": 7.0,
            "genre_fit": 7.0,
            "overall": 7.0,
        }
        feedback = ""
        suggestions = []

        lines = response.strip().split("\n")
        parsing_feedback = False
        parsing_suggestions = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Parse score lines
            if ":" in line and "|" in line and not parsing_feedback:
                try:
                    parts = line.split("|")
                    score_part = parts[0].strip()

                    # Extract dimension name and score
                    dimension, score_str = score_part.split(":", 1)
                    dimension = dimension.strip().lower().replace(" ", "_")

                    # Extract numeric score
                    score_match = re.search(r"(\d+(?:\.\d+)?)", score_str)
                    if score_match:
                        score = float(score_match.group(1))
                        # Ensure score is in 0-10 range
                        score = max(0.0, min(10.0, score))

                        if dimension in scores:
                            scores[dimension] = score
                except Exception as e:
                    logger.debug(f"Failed to parse score line: {line} - {str(e)}")

            # Parse feedback section
            elif line.startswith("FEEDBACK:"):
                parsing_feedback = True
                parsing_suggestions = False
                feedback_text = line.replace("FEEDBACK:", "").strip()
                if feedback_text:
                    feedback = feedback_text

            elif line.startswith("SUGGESTIONS:"):
                parsing_feedback = False
                parsing_suggestions = True

            # Accumulate feedback
            elif parsing_feedback:
                if not line.startswith("-") and not line.startswith("SUGGESTIONS"):
                    feedback += " " + line

            # Parse suggestions
            elif parsing_suggestions and line.startswith("-"):
                suggestion = line.lstrip("-").strip()
                if suggestion:
                    suggestions.append(suggestion)

        # Calculate overall as average if not explicitly provided
        if "overall" not in response.lower() or scores["overall"] == 7.0:
            dimension_scores = [
                scores["creativity"],
                scores["coherence"],
                scores["rhyme_quality"],
                scores["emotional_impact"],
                scores["genre_fit"],
            ]
            scores["overall"] = sum(dimension_scores) / len(dimension_scores)

        return EvaluationScore(
            overall=scores["overall"],
            creativity=scores["creativity"],
            coherence=scores["coherence"],
            rhyme_quality=scores["rhyme_quality"],
            emotional_impact=scores["emotional_impact"],
            genre_fit=scores["genre_fit"],
            feedback=feedback.strip() or "Evaluation completed successfully.",
            suggestions=suggestions or ["Continue refining based on feedback"],
        )
