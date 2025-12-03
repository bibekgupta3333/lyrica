"""
API Endpoints for Lyrics Management (CRUD Operations).

This module provides REST API endpoints for creating, reading,
updating, and deleting song lyrics.
"""

import re
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.orchestrator import get_orchestrator
from app.agents.state import WorkflowStatus
from app.api.dependencies import get_current_user, get_db
from app.crud.lyrics import lyrics as crud_lyrics
from app.models.lyrics import Lyrics as LyricsModel
from app.models.lyrics import LyricsSection
from app.models.user import User
from app.schemas.lyrics import Lyrics, LyricsCreate, LyricsUpdate, LyricsWithSections

router = APIRouter()


# ============================================================================
# Helper Functions
# ============================================================================


def _parse_lyrics_into_sections(lyrics_content: str) -> List[dict]:
    """
    Parse lyrics content into sections.

    Expected format: [SECTION_TYPE]\ncontent\n\n[SECTION_TYPE]\ncontent...

    Args:
        lyrics_content: Full lyrics text with section markers

    Returns:
        List of section dictionaries with type, order, and content
    """
    sections = []
    # Pattern to match section markers like [VERSE], [CHORUS], etc.
    section_pattern = r"\[([A-Z\s]+)\]\s*\n(.*?)(?=\n\[|$)"
    matches = re.finditer(section_pattern, lyrics_content, re.DOTALL | re.MULTILINE)

    for order, match in enumerate(matches, start=1):
        section_type = match.group(1).strip().lower()
        content = match.group(2).strip()

        if content:
            # Count lines
            line_count = len([line for line in content.split("\n") if line.strip()])
            sections.append(
                {
                    "section_type": section_type,
                    "section_order": order,
                    "content": content,
                    "line_count": line_count,
                }
            )

    return sections


async def _save_lyrics_sections(db: AsyncSession, lyrics_id: UUID, sections: List[dict]) -> None:
    """
    Save lyrics sections to database.

    Args:
        db: Database session
        lyrics_id: Lyrics ID
        sections: List of section dictionaries
    """
    for section_data in sections:
        section = LyricsSection(
            lyrics_id=lyrics_id,
            section_type=section_data["section_type"],
            section_order=section_data["section_order"],
            content=section_data["content"],
            line_count=section_data.get("line_count"),
        )
        db.add(section)

    await db.flush()


# ============================================================================
# CRUD Endpoints
# ============================================================================


@router.post(
    "/generate",
    response_model=Lyrics,
    status_code=status.HTTP_201_CREATED,
    summary="Generate new lyrics",
    description="Generate song lyrics using the agent workflow and save to database",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "pop_love_song": {
                            "summary": "Pop Love Song",
                            "value": {
                                "title": "Summer Dreams",
                                "content": "[Verse 1]\nWalking down the beach at sunset\nYour hand in mine feels so right\n[Chorus]\nSummer dreams and ocean breeze\nWith you is where I want to be",
                                "structure": {
                                    "sections": [
                                        {"type": "verse", "count": 2},
                                        {"type": "chorus", "count": 2},
                                        {"type": "bridge", "count": 1},
                                    ]
                                },
                                "genre": "pop",
                                "mood": "happy",
                                "theme": "love",
                                "language": "en",
                                "prompt": "Write a happy pop song about summer love",
                                "generation_params": {"temperature": 0.8, "max_length": 500},
                            },
                        },
                        "hip_hop_motivational": {
                            "summary": "Hip-Hop Motivational",
                            "value": {
                                "title": "Rise Above",
                                "content": "[Verse 1]\nStarted from the bottom now I'm here\nEvery obstacle made my vision clear\n[Chorus]\nRise above, never give up\nKeep pushing till you fill your cup",
                                "structure": {
                                    "sections": [
                                        {"type": "verse", "count": 3},
                                        {"type": "chorus", "count": 2},
                                    ]
                                },
                                "genre": "hip-hop",
                                "mood": "energetic",
                                "theme": "motivation",
                                "language": "en",
                            },
                        },
                        "ballad_heartbreak": {
                            "summary": "Ballad Heartbreak",
                            "value": {
                                "title": "Memories Fade",
                                "content": "[Verse 1]\nPictures on the wall remind me\nOf the love we used to know\n[Chorus]\nMemories fade like autumn leaves\nBut my heart still believes",
                                "structure": {
                                    "sections": [
                                        {"type": "verse", "count": 2},
                                        {"type": "chorus", "count": 3},
                                        {"type": "bridge", "count": 1},
                                    ]
                                },
                                "genre": "ballad",
                                "mood": "melancholic",
                                "theme": "heartbreak",
                                "language": "en",
                            },
                        },
                    }
                }
            }
        }
    },
)
async def generate_lyrics(
    lyrics_in: LyricsCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate new song lyrics using the multi-agent system.

    This endpoint:
    1. Validates input parameters
    2. Triggers the agent workflow (Planning → Generation → Refinement → Evaluation)
    3. Saves the generated lyrics to the database
    4. Returns the created lyrics object

    **Note**: For direct agent workflow usage without database storage,
    use `/api/v1/songs/generate` endpoint instead.
    """
    logger.info(f"Lyrics generation request from user {current_user.id}")

    try:
        # Initialize orchestrator
        orchestrator = get_orchestrator()

        # Prepare prompt - use provided prompt or build from other fields
        prompt = lyrics_in.prompt or f"Write a {lyrics_in.genre or 'song'} song"
        if lyrics_in.theme:
            prompt += f" about {lyrics_in.theme}"
        if lyrics_in.mood:
            prompt += f" with a {lyrics_in.mood} mood"

        # Determine length from structure if provided
        length = "medium"
        if lyrics_in.structure and isinstance(lyrics_in.structure, dict):
            sections = lyrics_in.structure.get("sections", [])
            total_sections = sum(s.get("count", 1) for s in sections)
            if total_sections <= 3:
                length = "short"
            elif total_sections >= 7:
                length = "long"

        # Execute agent workflow
        # Convert UUID to int for agent state (use hash to ensure it's a valid int)
        user_id_int = hash(str(current_user.id)) % (2**31)  # Ensure it fits in int32 range
        start_time = datetime.now()
        try:
            agent_state = await orchestrator.generate_song(
                user_id=user_id_int,
                prompt=prompt,
                genre=lyrics_in.genre,
                mood=lyrics_in.mood,
                theme=lyrics_in.theme,
                length=length,
                use_rag=True,
                max_retries=3,
            )
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Agent workflow execution failed: {str(e)}",
            )
        generation_time = (datetime.now() - start_time).total_seconds()

        # Check if workflow completed successfully
        # Handle case where workflow returns dict instead of AgentState
        if isinstance(agent_state, dict):
            workflow_status = agent_state.get("workflow_status")
            if workflow_status != WorkflowStatus.COMPLETED.value:
                error_msg = "; ".join(agent_state.get("errors", [])) or "Unknown error"
                logger.error(f"Agent workflow failed: {error_msg}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Lyrics generation failed: {error_msg}",
                )
            # Extract from dict
            final_lyrics_content = (
                agent_state.get("final_lyrics")
                or agent_state.get("refined_lyrics")
                or agent_state.get("generated_lyrics")
            )
            title = agent_state.get("title")
            eval_score = agent_state.get("evaluation_score")
        elif agent_state.workflow_status != WorkflowStatus.COMPLETED:
            error_msg = "; ".join(agent_state.errors) if agent_state.errors else "Unknown error"
            logger.error(f"Agent workflow failed: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lyrics generation failed: {error_msg}",
            )

        # Extract generated content (handle both dict and AgentState)
        if isinstance(agent_state, dict):
            final_lyrics_content = (
                agent_state.get("final_lyrics")
                or agent_state.get("refined_lyrics")
                or agent_state.get("generated_lyrics")
            )
            title = agent_state.get("title")
            song_structure = agent_state.get("song_structure")
            eval_score = agent_state.get("evaluation_score", {})
        else:
            final_lyrics_content = (
                agent_state.final_lyrics
                or agent_state.refined_lyrics
                or agent_state.generated_lyrics
            )
            title = agent_state.title
            song_structure = agent_state.song_structure
            eval_score = agent_state.evaluation_score

        if not final_lyrics_content:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No lyrics generated by agent workflow",
            )

        # Build structure from agent state
        structure = lyrics_in.structure or {}
        if song_structure:
            if isinstance(song_structure, dict):
                sections_list = song_structure.get("sections", [])
                structure = {
                    "sections": [
                        {
                            "type": s.get("type", "verse"),
                            "count": 1,
                            "length": s.get("length", 4),
                            "mood": s.get("mood"),
                        }
                        for s in sections_list
                    ],
                    "structure_type": song_structure.get("structure_type"),
                    "total_sections": song_structure.get("total_sections", len(sections_list)),
                }
            else:
                structure = {
                    "sections": [
                        {
                            "type": section.type,
                            "count": 1,
                            "length": section.length or 4,
                            "mood": section.mood,
                        }
                        for section in song_structure.sections
                    ],
                    "structure_type": song_structure.structure_type,
                    "total_sections": song_structure.total_sections,
                }

        # Extract genre, mood, theme (handle both dict and AgentState)
        if isinstance(agent_state, dict):
            genre = lyrics_in.genre or agent_state.get("genre")
            mood = lyrics_in.mood or agent_state.get("mood")
            theme = lyrics_in.theme or agent_state.get("theme")
        else:
            genre = lyrics_in.genre or agent_state.genre
            mood = lyrics_in.mood or agent_state.mood
            theme = lyrics_in.theme or agent_state.theme

        # Extract evaluation scores (handle both dict and object)
        quality_score = None
        rhyme_score = None
        creativity_score = None
        coherence_score = None

        if eval_score:
            if isinstance(eval_score, dict):
                overall = eval_score.get("overall", 0)
                quality_score = float(overall / 10.0) if overall else None
                rhyme_score = (
                    float(eval_score.get("rhyme_quality", 0) / 10.0)
                    if eval_score.get("rhyme_quality")
                    else None
                )
                creativity_score = (
                    float(eval_score.get("creativity", 0) / 10.0)
                    if eval_score.get("creativity")
                    else None
                )
                coherence_score = (
                    float(eval_score.get("coherence", 0) / 10.0)
                    if eval_score.get("coherence")
                    else None
                )
            else:
                quality_score = float(eval_score.overall / 10.0) if eval_score.overall else None
                rhyme_score = (
                    float(eval_score.rhyme_quality / 10.0) if eval_score.rhyme_quality else None
                )
                creativity_score = (
                    float(eval_score.creativity / 10.0) if eval_score.creativity else None
                )
                coherence_score = (
                    float(eval_score.coherence / 10.0) if eval_score.coherence else None
                )

        # Create lyrics object
        lyrics_data = {
            "title": title or lyrics_in.title,
            "content": final_lyrics_content,
            "structure": structure,
            "genre": genre,
            "mood": mood,
            "theme": theme,
            "language": lyrics_in.language,
            "prompt": prompt,
            "generation_params": lyrics_in.generation_params or {},
            "model_used": orchestrator.llm_provider or "default",
            "generation_time_seconds": generation_time,
            "quality_score": quality_score,
            "rhyme_score": rhyme_score,
            "creativity_score": creativity_score,
            "coherence_score": coherence_score,
            "status": "draft",
        }

        lyrics = LyricsModel(**lyrics_data, user_id=current_user.id)
        db.add(lyrics)
        await db.flush()
        await db.refresh(lyrics)

        # Parse and save sections
        sections_data = _parse_lyrics_into_sections(final_lyrics_content)
        if sections_data:
            await _save_lyrics_sections(db, lyrics.id, sections_data)

        await db.commit()
        await db.refresh(lyrics)

        # Log quality score
        if isinstance(eval_score, dict):
            score_str = f"{eval_score.get('overall', 'N/A')}/10" if eval_score else "N/A"
        else:
            score_str = f"{eval_score.overall}/10" if eval_score else "N/A"

        logger.info(f"Lyrics created with ID: {lyrics.id}, quality score: {score_str}")
        return lyrics

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to generate lyrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lyrics generation failed: {str(e)}",
        )


@router.get(
    "/{lyrics_id}",
    response_model=LyricsWithSections,
    summary="Get lyrics by ID",
    description="Retrieve lyrics by ID with sections",
    openapi_extra={
        "parameters": [
            {
                "name": "lyrics_id",
                "in": "path",
                "required": True,
                "schema": {"type": "string", "format": "uuid"},
                "examples": {
                    "example_id": {
                        "summary": "Example Lyrics ID",
                        "value": "123e4567-e89b-12d3-a456-426614174000",
                    },
                },
            }
        ]
    },
)
async def get_lyrics(
    lyrics_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve specific lyrics by ID.

    Returns the lyrics with all sections included.
    Only the owner or public lyrics can be accessed.
    """
    logger.debug(f"Fetching lyrics {lyrics_id} for user {current_user.id}")

    # Load lyrics
    lyrics = await crud_lyrics.get(db=db, id=lyrics_id)

    if not lyrics:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lyrics not found")

    # Check permissions: owner or public
    if lyrics.user_id != current_user.id and not lyrics.is_public:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden")

    # Load sections manually (relationship is commented out in model)
    sections_result = await db.execute(
        select(LyricsSection)
        .where(LyricsSection.lyrics_id == lyrics_id)
        .order_by(LyricsSection.section_order)
    )
    sections = list(sections_result.scalars().all())

    # Convert to response schema with sections
    # Use model_dump to get lyrics data, then add sections
    from app.schemas.lyrics import LyricsSection as LyricsSectionSchema

    lyrics_data = {
        "id": lyrics.id,
        "user_id": lyrics.user_id,
        "title": lyrics.title,
        "content": lyrics.content,
        "structure": lyrics.structure,
        "genre": lyrics.genre,
        "mood": lyrics.mood,
        "theme": lyrics.theme,
        "language": lyrics.language,
        "prompt": lyrics.prompt,
        "generation_params": lyrics.generation_params or {},
        "model_used": lyrics.model_used,
        "generation_time_seconds": (
            float(lyrics.generation_time_seconds) if lyrics.generation_time_seconds else None
        ),
        "quality_score": float(lyrics.quality_score) if lyrics.quality_score else None,
        "rhyme_score": float(lyrics.rhyme_score) if lyrics.rhyme_score else None,
        "creativity_score": float(lyrics.creativity_score) if lyrics.creativity_score else None,
        "coherence_score": float(lyrics.coherence_score) if lyrics.coherence_score else None,
        "status": lyrics.status,
        "is_public": lyrics.is_public,
        "view_count": lyrics.view_count,
        "like_count": lyrics.like_count,
        "created_at": lyrics.created_at,
        "updated_at": lyrics.updated_at,
        "sections": [LyricsSectionSchema.model_validate(section) for section in sections],
    }

    return LyricsWithSections.model_validate(lyrics_data)


@router.get(
    "/",
    response_model=List[Lyrics],
    summary="List lyrics",
    description="Get list of lyrics with optional filters",
    openapi_extra={
        "parameters": [
            {
                "name": "skip",
                "in": "query",
                "required": False,
                "schema": {"type": "integer", "default": 0, "minimum": 0},
                "examples": {
                    "first_page": {"summary": "First Page", "value": 0},
                    "second_page": {"summary": "Second Page", "value": 20},
                },
            },
            {
                "name": "limit",
                "in": "query",
                "required": False,
                "schema": {"type": "integer", "default": 100, "minimum": 1, "maximum": 100},
                "examples": {
                    "small": {"summary": "Small Page", "value": 10},
                    "default": {"summary": "Default", "value": 100},
                    "large": {"summary": "Large Page", "value": 100},
                },
            },
            {
                "name": "genre",
                "in": "query",
                "required": False,
                "schema": {"type": "string"},
                "examples": {
                    "pop": {"summary": "Pop Genre", "value": "pop"},
                    "rock": {"summary": "Rock Genre", "value": "rock"},
                    "hip-hop": {"summary": "Hip-Hop Genre", "value": "hip-hop"},
                },
            },
            {
                "name": "public_only",
                "in": "query",
                "required": False,
                "schema": {"type": "boolean", "default": False},
                "examples": {
                    "public": {"summary": "Public Only", "value": True},
                    "private": {"summary": "Private Only", "value": False},
                },
            },
        ]
    },
)
async def list_lyrics(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    public_only: bool = Query(False, description="Show only public lyrics"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List lyrics with optional filtering.

    - By default, returns user's own lyrics
    - Set `public_only=true` to see public lyrics from all users
    - Filter by `genre` to narrow results
    """
    logger.debug(
        f"Listing lyrics for user {current_user.id} "
        f"(skip={skip}, limit={limit}, genre={genre}, public_only={public_only})"
    )

    if public_only:
        if genre:
            lyrics_list = await crud_lyrics.get_by_genre(db=db, genre=genre, skip=skip, limit=limit)
            # Filter to public only
            lyrics_list = [l for l in lyrics_list if l.is_public]
        else:
            lyrics_list = await crud_lyrics.get_public(db=db, skip=skip, limit=limit)
    else:
        if genre:
            # Get user's lyrics filtered by genre
            all_user_lyrics = await crud_lyrics.get_by_user(
                db=db, user_id=current_user.id, skip=skip, limit=limit
            )
            lyrics_list = [l for l in all_user_lyrics if l.genre == genre]
        else:
            lyrics_list = await crud_lyrics.get_by_user(
                db=db, user_id=current_user.id, skip=skip, limit=limit
            )

    logger.debug(f"Found {len(lyrics_list)} lyrics")
    return lyrics_list


@router.put(
    "/{lyrics_id}",
    response_model=Lyrics,
    summary="Update lyrics",
    description="Update lyrics metadata or content",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "update_title": {
                            "summary": "Update Title Only",
                            "value": {"title": "My Awesome Song (Remix)"},
                        },
                        "update_content": {
                            "summary": "Update Content",
                            "value": {
                                "content": "[Verse 1]\nUpdated first verse\nWith new amazing lyrics\n[Chorus]\nThis is the updated chorus"
                            },
                        },
                        "publish_lyrics": {
                            "summary": "Publish Lyrics",
                            "value": {"status": "published", "is_public": True},
                        },
                        "make_private": {"summary": "Make Private", "value": {"is_public": False}},
                    }
                }
            }
        }
    },
)
async def update_lyrics(
    lyrics_id: UUID,
    lyrics_update: LyricsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update existing lyrics.

    Only the owner can update their lyrics.
    You can update:
    - Title
    - Content
    - Status (draft, published, archived)
    - Public/private visibility
    """
    logger.info(f"Updating lyrics {lyrics_id} by user {current_user.id}")

    # Get existing lyrics
    lyrics = await crud_lyrics.get(db=db, id=lyrics_id)

    if not lyrics:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lyrics not found")

    # Check ownership
    if lyrics.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own lyrics",
        )

    try:
        # Update lyrics
        updated_lyrics = await crud_lyrics.update(db=db, db_obj=lyrics, obj_in=lyrics_update)

        await db.commit()
        await db.refresh(updated_lyrics)

        logger.info(f"Lyrics {lyrics_id} updated successfully")
        return updated_lyrics

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update lyrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lyrics update failed: {str(e)}",
        )


@router.delete(
    "/{lyrics_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete lyrics",
    description="Delete lyrics by ID",
)
async def delete_lyrics(
    lyrics_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete specific lyrics by ID.

    Only the owner can delete their lyrics.
    This action is permanent and cannot be undone.
    """
    logger.info(f"Deleting lyrics {lyrics_id} by user {current_user.id}")

    # Get existing lyrics
    lyrics = await crud_lyrics.get(db=db, id=lyrics_id)

    if not lyrics:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lyrics not found")

    # Check ownership
    if lyrics.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own lyrics",
        )

    try:
        # Delete lyrics (cascade will handle sections)
        await crud_lyrics.delete(db=db, id=lyrics_id)

        await db.commit()

        logger.info(f"Lyrics {lyrics_id} deleted successfully")
        return None

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete lyrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lyrics deletion failed: {str(e)}",
        )


# ============================================================================
# Special Operations
# ============================================================================


@router.post(
    "/{lyrics_id}/regenerate",
    response_model=Lyrics,
    summary="Regenerate lyrics section",
    description="Regenerate a specific section of the lyrics",
    openapi_extra={
        "parameters": [
            {
                "name": "lyrics_id",
                "in": "path",
                "required": True,
                "schema": {"type": "string", "format": "uuid"},
                "examples": {
                    "example_id": {
                        "summary": "Example Lyrics ID",
                        "value": "123e4567-e89b-12d3-a456-426614174000",
                    },
                },
            },
            {
                "name": "section_type",
                "in": "query",
                "required": True,
                "schema": {"type": "string"},
                "examples": {
                    "verse": {"summary": "Regenerate Verse", "value": "verse"},
                    "chorus": {"summary": "Regenerate Chorus", "value": "chorus"},
                    "bridge": {"summary": "Regenerate Bridge", "value": "bridge"},
                    "intro": {"summary": "Regenerate Intro", "value": "intro"},
                },
            },
        ]
    },
)
async def regenerate_lyrics_section(
    lyrics_id: UUID,
    section_type: str = Query(..., description="Section to regenerate (verse, chorus, etc.)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Regenerate a specific section of existing lyrics.

    This endpoint:
    1. Fetches the existing lyrics and structure
    2. Re-runs the generation agent for the specified section
    3. Updates the lyrics in the database
    4. Returns the updated lyrics
    """
    logger.info(
        f"Regenerating {section_type} section of lyrics {lyrics_id} by user {current_user.id}"
    )

    # Get existing lyrics
    lyrics = await crud_lyrics.get(db=db, id=lyrics_id)

    if not lyrics:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lyrics not found")

    # Check ownership
    if lyrics.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only regenerate your own lyrics",
        )

    try:
        # Load sections
        sections_result = await db.execute(
            select(LyricsSection)
            .where(LyricsSection.lyrics_id == lyrics_id)
            .order_by(LyricsSection.section_order)
        )
        existing_sections = list(sections_result.scalars().all())

        # Find the section to regenerate
        section_to_regenerate = None
        for section in existing_sections:
            if section.section_type.lower() == section_type.lower():
                section_to_regenerate = section
                break

        if not section_to_regenerate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Section '{section_type}' not found in lyrics",
            )

        # Initialize orchestrator and generation agent
        orchestrator = get_orchestrator()
        generation_agent = orchestrator.generation_agent

        # Create a minimal agent state for section regeneration
        from app.agents.state import AgentState, SongSection

        user_id_int = hash(str(current_user.id)) % (2**31)
        section_state = AgentState(
            user_id=user_id_int,
            prompt=lyrics.prompt or f"Regenerate {section_type} section",
            genre=lyrics.genre,
            mood=lyrics.mood,
            theme=lyrics.theme,
            use_rag=True,
        )

        # Create a SongSection object for regeneration
        song_section = SongSection(
            type=section_type.lower(),
            order=section_to_regenerate.section_order,
            length=section_to_regenerate.line_count or 4,
            mood=lyrics.mood,
        )

        # Generate new section content
        rag_context = []
        if section_state.use_rag:
            rag_context = await generation_agent._retrieve_rag_context(section_state)

        new_content = await generation_agent._generate_section(
            song_section, section_state, rag_context
        )

        # Update the section
        section_to_regenerate.content = new_content
        section_to_regenerate.generation_attempts += 1
        section_to_regenerate.line_count = len(
            [line for line in new_content.split("\n") if line.strip()]
        )

        # Rebuild full lyrics content
        all_sections = []
        for section in sorted(existing_sections, key=lambda s: s.section_order):
            if section.id == section_to_regenerate.id:
                all_sections.append(f"[{section.section_type.upper()}]\n{new_content}")
            else:
                all_sections.append(f"[{section.section_type.upper()}]\n{section.content}")

        lyrics.content = "\n\n".join(all_sections)

        await db.commit()
        await db.refresh(lyrics)

        logger.info(f"Regenerated {section_type} section for lyrics {lyrics_id}")
        return lyrics

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to regenerate section: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Section regeneration failed: {str(e)}",
        )


@router.get(
    "/history",
    response_model=List[Lyrics],
    summary="Get generation history",
    description="Get user's lyrics generation history",
    openapi_extra={
        "parameters": [
            {
                "name": "skip",
                "in": "query",
                "required": False,
                "schema": {"type": "integer", "default": 0, "minimum": 0},
                "examples": {
                    "first_page": {"summary": "First Page", "value": 0},
                    "second_page": {"summary": "Second Page", "value": 50},
                },
            },
            {
                "name": "limit",
                "in": "query",
                "required": False,
                "schema": {"type": "integer", "default": 50, "minimum": 1, "maximum": 100},
                "examples": {
                    "small": {"summary": "Small Page", "value": 20},
                    "default": {"summary": "Default", "value": 50},
                    "large": {"summary": "Large Page", "value": 100},
                },
            },
        ]
    },
)
async def get_generation_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get user's lyrics generation history.

    Returns all lyrics created by the current user,
    ordered by creation date (most recent first).
    """
    logger.debug(f"Fetching generation history for user {current_user.id}")

    lyrics_list = await crud_lyrics.get_by_user(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )

    return lyrics_list


# ============================================================================
# Public Endpoints (no auth required)
# ============================================================================


@router.get(
    "/public/explore",
    response_model=List[Lyrics],
    summary="Explore public lyrics",
    description="Browse public lyrics from all users",
    openapi_extra={
        "parameters": [
            {
                "name": "skip",
                "in": "query",
                "required": False,
                "schema": {"type": "integer", "default": 0, "minimum": 0},
                "examples": {
                    "first_page": {"summary": "First Page", "value": 0},
                    "second_page": {"summary": "Second Page", "value": 20},
                },
            },
            {
                "name": "limit",
                "in": "query",
                "required": False,
                "schema": {"type": "integer", "default": 20, "minimum": 1, "maximum": 100},
                "examples": {
                    "small": {"summary": "Small Page", "value": 10},
                    "default": {"summary": "Default", "value": 20},
                    "large": {"summary": "Large Page", "value": 50},
                },
            },
            {
                "name": "genre",
                "in": "query",
                "required": False,
                "schema": {"type": "string"},
                "examples": {
                    "pop": {"summary": "Pop Genre", "value": "pop"},
                    "rock": {"summary": "Rock Genre", "value": "rock"},
                    "jazz": {"summary": "Jazz Genre", "value": "jazz"},
                },
            },
        ]
    },
)
async def explore_public_lyrics(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    db: AsyncSession = Depends(get_db),
):
    """
    Explore public lyrics from all users.

    No authentication required.
    Returns only lyrics marked as public and published.
    """
    logger.debug(f"Exploring public lyrics (skip={skip}, limit={limit}, genre={genre})")

    if genre:
        all_genre_lyrics = await crud_lyrics.get_by_genre(
            db=db, genre=genre, skip=skip, limit=limit
        )
        # Filter to public only
        lyrics_list = [l for l in all_genre_lyrics if l.is_public]
    else:
        lyrics_list = await crud_lyrics.get_public(db=db, skip=skip, limit=limit)

    return lyrics_list
