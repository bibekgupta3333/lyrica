"""
Agent State Management for LangGraph Multi-Agent System.

This module defines the state schema and state management for the
song generation agent workflow using LangGraph's StateGraph.
"""

from datetime import datetime
from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    """Status of an agent in the workflow."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStatus(str, Enum):
    """Overall status of the agent workflow."""

    INITIALIZED = "initialized"
    PLANNING = "planning"
    GENERATING = "generating"
    REFINING = "refining"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    FAILED = "failed"


class SongSection(BaseModel):
    """Represents a section of a song (verse, chorus, bridge, etc.)."""

    type: str = Field(..., description="Section type (verse, chorus, bridge, etc.)")
    order: int = Field(..., description="Order in song structure")
    content: Optional[str] = Field(None, description="Generated lyrics content")
    length: Optional[int] = Field(None, description="Target length in lines")
    mood: Optional[str] = Field(None, description="Mood/emotion for this section")
    refined: bool = Field(default=False, description="Whether section has been refined")


class SongStructure(BaseModel):
    """Planned structure for the song."""

    sections: List[SongSection] = Field(default_factory=list, description="List of song sections")
    total_sections: int = Field(default=0, description="Total number of sections")
    estimated_duration: Optional[int] = Field(None, description="Estimated duration in seconds")
    structure_type: Optional[str] = Field(
        None, description="Type of structure (verse-chorus, AABA, etc.)"
    )


class EvaluationScore(BaseModel):
    """Evaluation scores for generated lyrics."""

    overall: float = Field(..., ge=0, le=10, description="Overall quality score (0-10)")
    creativity: float = Field(..., ge=0, le=10, description="Creativity score (0-10)")
    coherence: float = Field(..., ge=0, le=10, description="Coherence score (0-10)")
    rhyme_quality: float = Field(..., ge=0, le=10, description="Rhyme quality score (0-10)")
    emotional_impact: float = Field(..., ge=0, le=10, description="Emotional impact score (0-10)")
    genre_fit: float = Field(..., ge=0, le=10, description="Genre fit score (0-10)")
    feedback: Optional[str] = Field(None, description="Detailed feedback")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")


class AgentMessage(BaseModel):
    """Message from an agent."""

    agent: str = Field(..., description="Agent name")
    message: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: str = Field(default="info", description="Message level (info, warning, error)")


class AgentState(BaseModel):
    """
    Complete state for the song generation agent workflow.

    This state is passed between agents and updated as the workflow progresses.
    Each agent reads from and writes to specific parts of this state.
    """

    # Input parameters (set at initialization)
    user_id: int = Field(..., description="User ID requesting the song")
    prompt: str = Field(..., description="User's prompt for song generation")
    genre: Optional[str] = Field(None, description="Desired genre")
    mood: Optional[str] = Field(None, description="Desired mood/emotion")
    theme: Optional[str] = Field(None, description="Song theme/topic")
    length: Optional[str] = Field(default="medium", description="Song length (short, medium, long)")
    style_references: List[str] = Field(
        default_factory=list, description="Reference artists or songs"
    )

    # Workflow state
    workflow_status: WorkflowStatus = Field(
        default=WorkflowStatus.INITIALIZED, description="Current workflow status"
    )
    current_agent: Optional[str] = Field(None, description="Currently active agent")
    workflow_start_time: datetime = Field(default_factory=datetime.utcnow)
    workflow_end_time: Optional[datetime] = Field(None)

    # Agent statuses
    planning_status: AgentStatus = Field(default=AgentStatus.PENDING)
    generation_status: AgentStatus = Field(default=AgentStatus.PENDING)
    refinement_status: AgentStatus = Field(default=AgentStatus.PENDING)
    evaluation_status: AgentStatus = Field(default=AgentStatus.PENDING)

    # Planning agent output
    song_structure: Optional[SongStructure] = Field(None, description="Planned song structure")
    structure_reasoning: Optional[str] = Field(
        None, description="Reasoning behind structure choice"
    )

    # Generation agent output
    generated_lyrics: Optional[str] = Field(None, description="Generated lyrics")
    generation_metadata: dict = Field(default_factory=dict, description="Metadata from generation")

    # Refinement agent output
    refined_lyrics: Optional[str] = Field(None, description="Refined lyrics")
    refinement_changes: List[str] = Field(
        default_factory=list, description="List of refinements made"
    )
    refinement_iterations: int = Field(default=0, description="Number of refinement iterations")

    # Evaluation agent output
    evaluation_score: Optional[EvaluationScore] = Field(
        None, description="Quality evaluation scores"
    )
    needs_regeneration: bool = Field(
        default=False, description="Whether lyrics need to be regenerated"
    )

    # Final output
    final_lyrics: Optional[str] = Field(None, description="Final approved lyrics")
    title: Optional[str] = Field(None, description="Generated song title")

    # Communication and error handling
    messages: List[AgentMessage] = Field(default_factory=list, description="Messages from agents")
    errors: List[str] = Field(default_factory=list, description="Errors encountered")
    retry_count: int = Field(default=0, description="Number of retry attempts")
    max_retries: int = Field(default=3, description="Maximum retry attempts")

    # RAG context (optional)
    rag_context: List[str] = Field(default_factory=list, description="Retrieved context from RAG")
    use_rag: bool = Field(default=True, description="Whether to use RAG")

    # Additional metadata
    metadata: dict = Field(default_factory=dict, description="Additional metadata")

    class Config:
        """Pydantic config."""

        use_enum_values = True

    def add_message(self, agent: str, message: str, level: str = "info") -> None:
        """Add a message from an agent."""
        self.messages.append(AgentMessage(agent=agent, message=message, level=level))

    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(f"[{datetime.utcnow().isoformat()}] {error}")

    def increment_retry(self) -> bool:
        """
        Increment retry count and check if max retries exceeded.

        Returns:
            True if can retry, False if max retries exceeded
        """
        self.retry_count += 1
        return self.retry_count <= self.max_retries

    def mark_agent_running(self, agent_name: str) -> None:
        """Mark an agent as running."""
        self.current_agent = agent_name
        status_field = f"{agent_name.lower()}_status"
        if hasattr(self, status_field):
            setattr(self, status_field, AgentStatus.RUNNING)
        self.add_message(agent_name, f"{agent_name} agent started", "info")

    def mark_agent_completed(self, agent_name: str) -> None:
        """Mark an agent as completed."""
        status_field = f"{agent_name.lower()}_status"
        if hasattr(self, status_field):
            setattr(self, status_field, AgentStatus.COMPLETED)
        self.add_message(agent_name, f"{agent_name} agent completed", "info")

    def mark_agent_failed(self, agent_name: str, error: str) -> None:
        """Mark an agent as failed."""
        status_field = f"{agent_name.lower()}_status"
        if hasattr(self, status_field):
            setattr(self, status_field, AgentStatus.FAILED)
        self.add_error(f"{agent_name} failed: {error}")
        self.add_message(agent_name, f"{agent_name} agent failed: {error}", "error")

    def to_dict(self) -> dict:
        """Convert state to dictionary."""
        return self.model_dump()


class AgentStateUpdate(BaseModel):
    """Partial update to agent state (used for returning updates from agents)."""

    # Fields that can be updated by agents
    workflow_status: Optional[WorkflowStatus] = None
    planning_status: Optional[AgentStatus] = None
    generation_status: Optional[AgentStatus] = None
    refinement_status: Optional[AgentStatus] = None
    evaluation_status: Optional[AgentStatus] = None

    song_structure: Optional[SongStructure] = None
    generated_lyrics: Optional[str] = None
    refined_lyrics: Optional[str] = None
    evaluation_score: Optional[EvaluationScore] = None
    final_lyrics: Optional[str] = None
    title: Optional[str] = None

    messages: List[AgentMessage] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)

    class Config:
        """Pydantic config."""

        use_enum_values = True
