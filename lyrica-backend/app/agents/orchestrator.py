"""
Agent Orchestrator using LangGraph for Multi-Agent Workflow.

This module orchestrates the song generation workflow using LangGraph's
StateGraph to coordinate multiple agents: Planning, Generation,
Refinement, and Evaluation.
"""

from datetime import datetime
from typing import Dict, Literal

from langgraph.graph import END, StateGraph
from loguru import logger

from app.agents.evaluation_agent import EvaluationAgent
from app.agents.generation_agent import GenerationAgent
from app.agents.planning_agent import PlanningAgent
from app.agents.refinement_agent import RefinementAgent
from app.agents.state import AgentState, WorkflowStatus


class SongGenerationOrchestrator:
    """
    Orchestrates the multi-agent song generation workflow.

    The workflow follows this structure:
    START -> Planning -> Generation -> Refinement -> Evaluation -> END

    With conditional logic:
    - If evaluation fails: can retry (up to max_retries)
    - If agent fails: workflow fails
    """

    def __init__(
        self,
        llm_provider: str = None,
        quality_threshold: float = 6.5,
        max_refinement_iterations: int = 2,
    ):
        """
        Initialize the orchestrator.

        Args:
            llm_provider: LLM provider to use for all agents
            quality_threshold: Minimum quality score for evaluation
            max_refinement_iterations: Max iterations for refinement
        """
        self.llm_provider = llm_provider

        # Initialize agents
        self.planning_agent = PlanningAgent(llm_provider)
        self.generation_agent = GenerationAgent(llm_provider)
        self.refinement_agent = RefinementAgent(llm_provider, max_refinement_iterations)
        self.evaluation_agent = EvaluationAgent(llm_provider, quality_threshold)

        # Build workflow graph
        self.workflow = self._build_workflow()

        logger.info(
            f"Initialized SongGenerationOrchestrator with provider: {llm_provider or 'default'}"
        )

    def _build_workflow(self) -> StateGraph:
        """
        Build the LangGraph workflow.

        Returns:
            Compiled StateGraph workflow
        """
        # Create state graph
        workflow = StateGraph(AgentState)

        # Add agent nodes
        workflow.add_node("planning", self._planning_node)
        workflow.add_node("generation", self._generation_node)
        workflow.add_node("refinement", self._refinement_node)
        workflow.add_node("evaluation", self._evaluation_node)
        workflow.add_node("error_handler", self._error_handler_node)

        # Define workflow edges
        workflow.set_entry_point("planning")

        # Planning -> Generation (or error)
        workflow.add_conditional_edges(
            "planning",
            self._check_planning_status,
            {
                "continue": "generation",
                "error": "error_handler",
            },
        )

        # Generation -> Refinement (or error)
        workflow.add_conditional_edges(
            "generation",
            self._check_generation_status,
            {
                "continue": "refinement",
                "error": "error_handler",
            },
        )

        # Refinement -> Evaluation (or error)
        workflow.add_conditional_edges(
            "refinement",
            self._check_refinement_status,
            {
                "continue": "evaluation",
                "error": "error_handler",
            },
        )

        # Evaluation -> END or retry (or error)
        workflow.add_conditional_edges(
            "evaluation",
            self._check_evaluation_status,
            {
                "complete": END,
                "retry": "planning",  # Start over with retry
                "error": "error_handler",
            },
        )

        # Error handler always goes to END
        workflow.add_edge("error_handler", END)

        # Compile workflow
        return workflow.compile()

    async def _planning_node(self, state: AgentState) -> AgentState:
        """Planning agent node."""
        try:
            updates = await self.planning_agent.run(state)
            # Update state with returned values
            for key, value in updates.items():
                if hasattr(state, key):
                    setattr(state, key, value)
            return state
        except Exception as e:
            logger.error(f"Planning node error: {str(e)}")
            state.add_error(f"Planning failed: {str(e)}")
            state.workflow_status = WorkflowStatus.FAILED
            return state

    async def _generation_node(self, state: AgentState) -> AgentState:
        """Generation agent node."""
        try:
            updates = await self.generation_agent.run(state)
            for key, value in updates.items():
                if hasattr(state, key):
                    setattr(state, key, value)
            return state
        except Exception as e:
            logger.error(f"Generation node error: {str(e)}")
            state.add_error(f"Generation failed: {str(e)}")
            state.workflow_status = WorkflowStatus.FAILED
            return state

    async def _refinement_node(self, state: AgentState) -> AgentState:
        """Refinement agent node."""
        try:
            updates = await self.refinement_agent.run(state)
            for key, value in updates.items():
                if hasattr(state, key):
                    setattr(state, key, value)
            return state
        except Exception as e:
            logger.error(f"Refinement node error: {str(e)}")
            state.add_error(f"Refinement failed: {str(e)}")
            state.workflow_status = WorkflowStatus.FAILED
            return state

    async def _evaluation_node(self, state: AgentState) -> AgentState:
        """Evaluation agent node."""
        try:
            updates = await self.evaluation_agent.run(state)
            for key, value in updates.items():
                if hasattr(state, key):
                    setattr(state, key, value)

            # Set end time if workflow completed
            if state.workflow_status == WorkflowStatus.COMPLETED:
                state.workflow_end_time = datetime.utcnow()

            return state
        except Exception as e:
            logger.error(f"Evaluation node error: {str(e)}")
            state.add_error(f"Evaluation failed: {str(e)}")
            state.workflow_status = WorkflowStatus.FAILED
            return state

    async def _error_handler_node(self, state: AgentState) -> AgentState:
        """Error handler node."""
        state.workflow_status = WorkflowStatus.FAILED
        state.workflow_end_time = datetime.utcnow()
        logger.error(f"Workflow failed for user {state.user_id}. Errors: {state.errors}")
        return state

    def _check_planning_status(self, state: AgentState) -> Literal["continue", "error"]:
        """Check if planning succeeded."""
        if state.workflow_status == WorkflowStatus.FAILED:
            return "error"
        return "continue"

    def _check_generation_status(self, state: AgentState) -> Literal["continue", "error"]:
        """Check if generation succeeded."""
        if state.workflow_status == WorkflowStatus.FAILED:
            return "error"
        return "continue"

    def _check_refinement_status(self, state: AgentState) -> Literal["continue", "error"]:
        """Check if refinement succeeded."""
        if state.workflow_status == WorkflowStatus.FAILED:
            return "error"
        return "continue"

    def _check_evaluation_status(self, state: AgentState) -> Literal["complete", "retry", "error"]:
        """Check evaluation result and determine next step."""
        if state.workflow_status == WorkflowStatus.FAILED:
            # Check if we can retry
            if state.needs_regeneration and state.increment_retry():
                logger.info(
                    f"Quality below threshold, retrying (attempt {state.retry_count}/{state.max_retries})"
                )
                return "retry"
            return "error"

        if state.workflow_status == WorkflowStatus.COMPLETED:
            return "complete"

        return "error"

    async def generate_song(
        self,
        user_id: int,
        prompt: str,
        genre: str = None,
        mood: str = None,
        theme: str = None,
        length: str = "medium",
        style_references: list = None,
        use_rag: bool = True,
        max_retries: int = 3,
    ) -> AgentState:
        """
        Execute the complete song generation workflow.

        Args:
            user_id: User ID requesting the song
            prompt: User's prompt for song generation
            genre: Desired genre
            mood: Desired mood/emotion
            theme: Song theme/topic
            length: Song length (short, medium, long)
            style_references: Reference artists or songs
            use_rag: Whether to use RAG for context
            max_retries: Maximum retry attempts

        Returns:
            Final AgentState with generated song
        """
        logger.info(f"Starting song generation workflow for user {user_id}")

        # Initialize state
        initial_state = AgentState(
            user_id=user_id,
            prompt=prompt,
            genre=genre,
            mood=mood,
            theme=theme,
            length=length,
            style_references=style_references or [],
            use_rag=use_rag,
            max_retries=max_retries,
        )

        try:
            # Execute workflow
            final_state = await self.workflow.ainvoke(initial_state)

            # Log completion
            if final_state.workflow_status == WorkflowStatus.COMPLETED:
                duration = (
                    final_state.workflow_end_time - final_state.workflow_start_time
                ).total_seconds()
                logger.info(
                    f"Song generation completed in {duration:.2f}s. "
                    f"Score: {final_state.evaluation_score.overall:.2f}/10"
                )
            else:
                logger.warning(f"Song generation failed: {final_state.errors}")

            return final_state

        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            initial_state.add_error(f"Workflow execution failed: {str(e)}")
            initial_state.workflow_status = WorkflowStatus.FAILED
            initial_state.workflow_end_time = datetime.utcnow()
            return initial_state


# Singleton instance for easy access
_orchestrator_instance = None


def get_orchestrator(
    llm_provider: str = None,
    quality_threshold: float = 6.5,
    max_refinement_iterations: int = 2,
) -> SongGenerationOrchestrator:
    """
    Get or create orchestrator instance.

    Args:
        llm_provider: LLM provider to use
        quality_threshold: Minimum quality score
        max_refinement_iterations: Max refinement iterations

    Returns:
        SongGenerationOrchestrator instance
    """
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = SongGenerationOrchestrator(
            llm_provider, quality_threshold, max_refinement_iterations
        )
    return _orchestrator_instance
