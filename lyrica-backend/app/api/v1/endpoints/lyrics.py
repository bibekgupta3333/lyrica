"""
API Endpoints for Lyrics Management (CRUD Operations).

This module provides REST API endpoints for creating, reading,
updating, and deleting song lyrics.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.crud.lyrics import lyrics as crud_lyrics
from app.models.user import User
from app.schemas.lyrics import Lyrics, LyricsCreate, LyricsUpdate, LyricsWithSections

router = APIRouter()


# ============================================================================
# CRUD Endpoints
# ============================================================================


@router.post(
    "/generate",
    response_model=Lyrics,
    status_code=status.HTTP_201_CREATED,
    summary="Generate new lyrics",
    description="Generate song lyrics using the agent workflow and save to database",
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
        # TODO: Integrate with agent workflow
        # For now, create lyrics directly
        lyrics = await crud_lyrics.create_with_user(
            db=db, obj_in=lyrics_in, user_id=current_user.id
        )

        await db.commit()
        await db.refresh(lyrics)

        logger.info(f"Lyrics created with ID: {lyrics.id}")
        return lyrics

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

    lyrics = await crud_lyrics.get(db=db, id=lyrics_id)

    if not lyrics:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lyrics not found")

    # Check permissions: owner or public
    if lyrics.user_id != current_user.id and not lyrics.is_public:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden")

    # TODO: Load sections relationship
    # For now, return lyrics without sections loaded
    return lyrics


@router.get(
    "/",
    response_model=List[Lyrics],
    summary="List lyrics",
    description="Get list of lyrics with optional filters",
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
        await crud_lyrics.remove(db=db, id=lyrics_id)

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
        # TODO: Integrate with agent workflow to regenerate section
        # For now, just return the lyrics unchanged
        logger.warning("Section regeneration not yet implemented")

        return lyrics

    except Exception as e:
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
