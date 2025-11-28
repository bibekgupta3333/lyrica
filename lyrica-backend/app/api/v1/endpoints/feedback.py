"""
API Endpoints for User Feedback Management.

This module provides REST API endpoints for submitting and
managing user feedback on generated lyrics.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.crud import feedback as crud_feedback
from app.models.user import User
from app.schemas.feedback import Feedback, FeedbackCreate, FeedbackStats

router = APIRouter()


# ============================================================================
# Feedback Endpoints
# ============================================================================


@router.post(
    "/",
    response_model=Feedback,
    status_code=status.HTTP_201_CREATED,
    summary="Submit feedback",
    description="Submit feedback for generated lyrics",
)
async def submit_feedback(
    feedback_in: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit feedback for lyrics.

    Users can rate lyrics on multiple dimensions:
    - **Overall rating** (1-5 stars)
    - **Creativity rating** (1-5 stars)
    - **Relevance rating** (1-5 stars)
    - **Quality rating** (1-5 stars)

    They can also:
    - Add comments
    - Add tags
    - Mark as liked
    """
    logger.info(f"User {current_user.id} submitting feedback for lyrics {feedback_in.lyrics_id}")

    try:
        # Create feedback
        feedback = await crud_feedback.feedback.create_with_user(
            db=db, obj_in=feedback_in, user_id=current_user.id
        )

        await db.commit()
        await db.refresh(feedback)

        logger.info(f"Feedback created with ID: {feedback.id}")
        return feedback

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feedback submission failed: {str(e)}",
        )


@router.get(
    "/",
    response_model=List[Feedback],
    summary="List user feedback",
    description="Get all feedback submitted by the current user",
)
async def list_my_feedback(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all feedback submitted by the current user.

    Returns feedback ordered by creation date (most recent first).
    """
    logger.debug(f"Listing feedback for user {current_user.id}")

    feedback_list = await crud_feedback.feedback.get_by_user(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )

    return feedback_list


@router.get(
    "/lyrics/{lyrics_id}",
    response_model=List[Feedback],
    summary="Get feedback for lyrics",
    description="Get all feedback for specific lyrics",
)
async def get_lyrics_feedback(
    lyrics_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all feedback for specific lyrics.

    Only accessible by:
    - The lyrics owner
    - Admin users (TODO: implement admin check)
    """
    logger.debug(f"Fetching feedback for lyrics {lyrics_id}")

    # TODO: Add ownership/permission check
    # For now, allow any authenticated user

    feedback_list = await crud_feedback.feedback.get_by_lyrics(db=db, lyrics_id=lyrics_id)

    return feedback_list


@router.get(
    "/stats",
    response_model=FeedbackStats,
    summary="Get feedback statistics",
    description="Get overall feedback statistics (admin only)",
)
async def get_feedback_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get feedback statistics across all users.

    Returns:
    - Total feedback count
    - Average rating
    - Rating distribution
    - Recent feedback count (last 7 days)

    **Note**: Currently accessible to all users.
    In production, this should be admin-only.
    """
    logger.debug("Fetching feedback statistics")

    stats = await crud_feedback.feedback.get_stats(db=db)

    return FeedbackStats(**stats)


@router.delete(
    "/{feedback_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete feedback",
    description="Delete specific feedback entry",
)
async def delete_feedback(
    feedback_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete specific feedback entry.

    Only the feedback author can delete their own feedback.
    """
    logger.info(f"Deleting feedback {feedback_id} by user {current_user.id}")

    # Get existing feedback
    feedback = await crud_feedback.feedback.get(db=db, id=feedback_id)

    if not feedback:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")

    # Check ownership
    if feedback.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own feedback",
        )

    try:
        # Delete feedback
        await crud_feedback.feedback.remove(db=db, id=feedback_id)

        await db.commit()

        logger.info(f"Feedback {feedback_id} deleted successfully")
        return None

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feedback deletion failed: {str(e)}",
        )
