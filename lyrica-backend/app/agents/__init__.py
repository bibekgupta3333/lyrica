"""
Multi-Agent Song Generation System using LangGraph.

This package contains the agent-based song generation system that
orchestrates multiple AI agents to create high-quality song lyrics.

Agents:
    - Planning Agent: Designs song structure
    - Generation Agent: Creates lyrics based on structure
    - Refinement Agent: Improves lyrics quality
    - Evaluation Agent: Assesses and scores lyrics

Usage:
    from app.agents import get_orchestrator

    orchestrator = get_orchestrator()
    result = await orchestrator.generate_song(
        user_id=1,
        prompt="A sad song about lost love",
        genre="pop",
        mood="melancholic"
    )
"""

from app.agents.evaluation_agent import EvaluationAgent
from app.agents.generation_agent import GenerationAgent
from app.agents.orchestrator import SongGenerationOrchestrator, get_orchestrator
from app.agents.planning_agent import PlanningAgent
from app.agents.refinement_agent import RefinementAgent
from app.agents.state import (
    AgentState,
    AgentStatus,
    EvaluationScore,
    SongSection,
    SongStructure,
    WorkflowStatus,
)

__all__ = [
    # Orchestrator
    "SongGenerationOrchestrator",
    "get_orchestrator",
    # Agents
    "PlanningAgent",
    "GenerationAgent",
    "RefinementAgent",
    "EvaluationAgent",
    # State
    "AgentState",
    "AgentStatus",
    "WorkflowStatus",
    "SongSection",
    "SongStructure",
    "EvaluationScore",
]
