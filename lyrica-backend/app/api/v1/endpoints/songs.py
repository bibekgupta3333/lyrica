"""
API Endpoints for Agent-Based Song Generation.

This module provides REST API endpoints for the multi-agent
song generation workflow using LangGraph orchestration.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents import get_orchestrator
from app.agents.state import AgentState, WorkflowStatus
from app.api.dependencies import get_current_user, get_db
from app.core.config import settings
from app.models.user import User

router = APIRouter()


# ============================================================================
# Request/Response Schemas
# ============================================================================


class SongGenerationRequest(BaseModel):
    """Request schema for song generation."""

    prompt: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="User prompt for song generation",
        example="Write a sad song about losing someone you love",
    )
    genre: Optional[str] = Field(
        None,
        max_length=50,
        description="Desired music genre",
        example="pop",
    )
    mood: Optional[str] = Field(
        None,
        max_length=50,
        description="Desired mood or emotion",
        example="melancholic",
    )
    theme: Optional[str] = Field(
        None,
        max_length=100,
        description="Song theme or topic",
        example="lost love",
    )
    length: str = Field(
        default="medium",
        description="Song length",
        example="medium",
    )
    style_references: List[str] = Field(
        default_factory=list,
        description="Reference artists or songs for style",
        example=["Adele", "Sam Smith"],
    )
    use_rag: bool = Field(
        default=True,
        description="Whether to use RAG for additional context",
    )
    llm_provider: Optional[str] = Field(
        None,
        description="LLM provider to use (ollama, openai, gemini)",
        example="ollama",
    )


class SongSectionResponse(BaseModel):
    """Response schema for song section."""

    type: str
    order: int
    content: Optional[str]
    length: Optional[int]
    mood: Optional[str]
    refined: bool


class SongStructureResponse(BaseModel):
    """Response schema for song structure."""

    sections: List[SongSectionResponse]
    total_sections: int
    estimated_duration: Optional[int]
    structure_type: Optional[str]


class EvaluationScoreResponse(BaseModel):
    """Response schema for evaluation scores."""

    overall: float
    creativity: float
    coherence: float
    rhyme_quality: float
    emotional_impact: float
    genre_fit: float
    feedback: Optional[str]
    suggestions: List[str]


class AgentMessageResponse(BaseModel):
    """Response schema for agent message."""

    agent: str
    message: str
    timestamp: str
    level: str


class SongGenerationResponse(BaseModel):
    """Response schema for song generation."""

    # Workflow info
    workflow_status: str
    workflow_duration: Optional[float] = Field(None, description="Workflow duration in seconds")

    # Generated content
    title: Optional[str]
    final_lyrics: Optional[str]
    generated_lyrics: Optional[str]
    refined_lyrics: Optional[str]

    # Structure
    song_structure: Optional[SongStructureResponse]

    # Evaluation
    evaluation_score: Optional[EvaluationScoreResponse]
    needs_regeneration: bool

    # Metadata
    refinement_iterations: int
    retry_count: int
    messages: List[AgentMessageResponse]
    errors: List[str]

    class Config:
        """Pydantic config."""

        from_attributes = True


# ============================================================================
# Endpoints
# ============================================================================


@router.post(
    "/generate",
    response_model=SongGenerationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a complete song with multi-agent system",
    description="Generate song lyrics using LangGraph orchestrated agents",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "pop_love_song": {
                            "summary": "Pop Love Song",
                            "value": {
                                "prompt": "Write a happy pop song about summer love",
                                "genre": "pop",
                                "mood": "happy",
                                "theme": "summer romance",
                                "length": "medium",
                                "style_references": ["Taylor Swift", "Ed Sheeran"],
                                "use_rag": True,
                                "llm_provider": "ollama",
                            },
                        },
                        "sad_ballad": {
                            "summary": "Sad Ballad",
                            "value": {
                                "prompt": "Write a melancholic ballad about losing someone you love",
                                "genre": "ballad",
                                "mood": "melancholic",
                                "theme": "lost love",
                                "length": "long",
                                "style_references": ["Adele", "Sam Smith"],
                                "use_rag": True,
                                "llm_provider": None,
                            },
                        },
                        "hip_hop_motivational": {
                            "summary": "Hip-Hop Motivational",
                            "value": {
                                "prompt": "Write an energetic hip-hop song about chasing dreams and never giving up",
                                "genre": "hip-hop",
                                "mood": "energetic",
                                "theme": "motivation",
                                "length": "medium",
                                "style_references": ["Kendrick Lamar", "Drake"],
                                "use_rag": True,
                                "llm_provider": "ollama",
                            },
                        },
                        "rock_anthem": {
                            "summary": "Rock Anthem",
                            "value": {
                                "prompt": "Write a powerful rock anthem about freedom and breaking free",
                                "genre": "rock",
                                "mood": "powerful",
                                "theme": "freedom",
                                "length": "long",
                                "style_references": ["Queen", "Led Zeppelin"],
                                "use_rag": True,
                                "llm_provider": None,
                            },
                        },
                    }
                }
            }
        }
    },
)
async def generate_song(
    request: SongGenerationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate a complete song using the multi-agent workflow.

    This endpoint orchestrates Planning, Generation, Refinement, and
    Evaluation agents to create high-quality song lyrics.

    The workflow:
    1. **Planning Agent**: Designs song structure based on prompt
    2. **Generation Agent**: Creates lyrics for each section (with RAG)
    3. **Refinement Agent**: Improves lyrics quality iteratively
    4. **Evaluation Agent**: Scores and validates final output

    Returns the complete song with evaluation scores and metadata.
    """
    logger.info(f"Song generation request from user {current_user.id}: {request.prompt[:50]}...")

    try:
        # Get orchestrator with configurable quality threshold from settings
        orchestrator = get_orchestrator(
            llm_provider=request.llm_provider,
            quality_threshold=settings.quality_threshold,
            max_refinement_iterations=2,
        )

        # Convert UUID to int for agent state (use hash to ensure it's a valid int)
        user_id_int = hash(str(current_user.id)) % (2**31)

        # Execute workflow
        result: AgentState = await orchestrator.generate_song(
            user_id=user_id_int,
            prompt=request.prompt,
            genre=request.genre,
            mood=request.mood,
            theme=request.theme,
            length=request.length,
            style_references=request.style_references,
            use_rag=request.use_rag,
            max_retries=3,
        )

        # Calculate duration
        duration = None
        if result.workflow_end_time and result.workflow_start_time:
            duration = (result.workflow_end_time - result.workflow_start_time).total_seconds()

        # Handle workflow_status (may be enum or string)
        workflow_status_str = (
            result.workflow_status.value
            if hasattr(result.workflow_status, "value")
            else str(result.workflow_status)
        )

        # Convert to response
        response = SongGenerationResponse(
            workflow_status=workflow_status_str,
            workflow_duration=duration,
            title=result.title,
            final_lyrics=result.final_lyrics,
            generated_lyrics=result.generated_lyrics,
            refined_lyrics=result.refined_lyrics,
            song_structure=(
                SongStructureResponse(
                    sections=[
                        SongSectionResponse(
                            type=s.type,
                            order=s.order,
                            content=s.content,
                            length=s.length,
                            mood=s.mood,
                            refined=s.refined,
                        )
                        for s in result.song_structure.sections
                    ],
                    total_sections=result.song_structure.total_sections,
                    estimated_duration=result.song_structure.estimated_duration,
                    structure_type=result.song_structure.structure_type,
                )
                if result.song_structure
                else None
            ),
            evaluation_score=(
                EvaluationScoreResponse(
                    overall=result.evaluation_score.overall,
                    creativity=result.evaluation_score.creativity,
                    coherence=result.evaluation_score.coherence,
                    rhyme_quality=result.evaluation_score.rhyme_quality,
                    emotional_impact=result.evaluation_score.emotional_impact,
                    genre_fit=result.evaluation_score.genre_fit,
                    feedback=result.evaluation_score.feedback,
                    suggestions=result.evaluation_score.suggestions,
                )
                if result.evaluation_score
                else None
            ),
            needs_regeneration=result.needs_regeneration,
            refinement_iterations=result.refinement_iterations,
            retry_count=result.retry_count,
            messages=[
                AgentMessageResponse(
                    agent=m.agent,
                    message=m.message,
                    timestamp=m.timestamp.isoformat(),
                    level=m.level,
                )
                for m in result.messages
            ],
            errors=result.errors,
        )

        # Log result
        is_completed = (
            workflow_status_str == WorkflowStatus.COMPLETED.value
            or workflow_status_str == "completed"
        )
        if is_completed:
            score = result.evaluation_score.overall if result.evaluation_score else 0.0
            logger.info(f"Song generation successful in {duration:.2f}s. " f"Score: {score:.2f}/10")
        else:
            logger.warning(f"Song generation failed: {result.errors}")

        return response

    except Exception as e:
        logger.error(f"Song generation endpoint failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Song generation failed: {str(e)}",
        )


@router.get(
    "/providers",
    summary="List available LLM providers",
    description="Get list of available LLM providers for song generation",
)
async def list_llm_providers():
    """List available LLM providers."""
    return {
        "providers": [
            {
                "name": "ollama",
                "display_name": "Ollama (Local)",
                "description": "Free local LLM (Llama 3, Mistral)",
                "cost": "free",
                "speed": "fast",
            },
            {
                "name": "openai",
                "display_name": "OpenAI GPT",
                "description": "GPT-4 and GPT-3.5 Turbo",
                "cost": "paid",
                "speed": "fast",
            },
            {
                "name": "gemini",
                "display_name": "Google Gemini",
                "description": "Gemini Pro",
                "cost": "paid",
                "speed": "fast",
            },
            {
                "name": "grok",
                "display_name": "xAI Grok",
                "description": "Grok 2",
                "cost": "paid",
                "speed": "fast",
            },
        ],
        "default": "ollama",
    }


@router.get(
    "/workflow-info",
    summary="Get workflow information",
    description="Get information about the agent workflow",
)
async def get_workflow_info():
    """Get information about the agent workflow."""
    return {
        "workflow": {
            "name": "Multi-Agent Song Generation",
            "description": "Orchestrated workflow using LangGraph",
            "agents": [
                {
                    "name": "Planning Agent",
                    "description": "Designs song structure based on prompt",
                    "output": "Song structure with sections",
                },
                {
                    "name": "Generation Agent",
                    "description": "Creates lyrics for each section",
                    "output": "Complete song lyrics",
                    "features": ["RAG context retrieval", "Section-by-section generation"],
                },
                {
                    "name": "Refinement Agent",
                    "description": "Improves lyrics quality",
                    "output": "Refined lyrics",
                    "features": ["Iterative refinement", "Quality analysis"],
                },
                {
                    "name": "Evaluation Agent",
                    "description": "Scores and validates lyrics",
                    "output": "Evaluation scores and feedback",
                    "features": [
                        "Multi-dimensional scoring",
                        "Quality threshold checking",
                        "Automatic retry if needed",
                    ],
                },
            ],
            "flow": "Planning → Generation → Refinement → Evaluation → Complete",
            "features": [
                "Automatic retry on low quality",
                "RAG-augmented generation",
                "Iterative refinement",
                "Comprehensive evaluation",
            ],
        },
        "configuration": {
            "quality_threshold": settings.quality_threshold,
            "max_refinement_iterations": 2,
            "max_retries": 3,
        },
    }
