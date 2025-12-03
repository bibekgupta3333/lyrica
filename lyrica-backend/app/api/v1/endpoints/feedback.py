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

from app.api.dependencies import get_current_user, get_db, require_admin
from app.crud.feedback import feedback as crud_feedback
from app.crud.lyrics import lyrics as crud_lyrics
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
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "positive_feedback": {
                            "summary": "Positive Feedback",
                            "description": "Submit positive feedback with all ratings and tags",
                            "value": {
                                "lyrics_id": "124c8ace-4bca-42b9-887f-1c94abd9b168",
                                "overall_rating": 5,
                                "creativity_rating": 5,
                                "relevance_rating": 5,
                                "quality_rating": 5,
                                "comment": "Amazing lyrics! Really captured the mood perfectly. The imagery is beautiful and the flow is excellent.",
                                "tags": ["creative", "emotional", "well-structured", "catchy"],
                                "is_liked": True,
                            },
                        },
                        "constructive_feedback": {
                            "summary": "Constructive Feedback",
                            "description": "Submit constructive feedback with suggestions",
                            "value": {
                                "lyrics_id": "124c8ace-4bca-42b9-887f-1c94abd9b168",
                                "overall_rating": 4,
                                "creativity_rating": 4,
                                "relevance_rating": 4,
                                "quality_rating": 3,
                                "comment": "Great work! The verses are strong, but the bridge could use more emotional depth. The chorus is catchy though!",
                                "tags": ["good-rhymes", "needs-improvement"],
                                "is_liked": False,
                            },
                        },
                        "minimal_feedback": {
                            "summary": "Minimal Feedback",
                            "description": "Submit minimal feedback with just rating",
                            "value": {
                                "lyrics_id": "124c8ace-4bca-42b9-887f-1c94abd9b168",
                                "overall_rating": 4,
                                "is_liked": True,
                            },
                        },
                        "detailed_review": {
                            "summary": "Detailed Review",
                            "description": "Submit detailed feedback with all fields",
                            "value": {
                                "lyrics_id": "124c8ace-4bca-42b9-887f-1c94abd9b168",
                                "overall_rating": 5,
                                "creativity_rating": 5,
                                "relevance_rating": 4,
                                "quality_rating": 5,
                                "comment": "This is one of the best lyrics I've heard! The wordplay is clever, the emotional connection is strong, and the structure flows perfectly. The bridge adds a nice contrast to the verses. Only minor suggestion would be to add more variation in the chorus repetition.",
                                "tags": ["inspiring", "well-written", "emotional", "professional"],
                                "is_liked": True,
                            },
                        },
                    }
                }
            }
        }
    },
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
        feedback = await crud_feedback.create_with_user(
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

    feedback_list = await crud_feedback.get_by_user(
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
    - Admin users
    """
    logger.debug(f"Fetching feedback for lyrics {lyrics_id}")

    # Check if lyrics exists
    lyrics = await crud_lyrics.get(db=db, id=lyrics_id)
    if not lyrics:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lyrics not found")

    # Check permissions: owner or admin
    is_admin = current_user.role == "admin" or current_user.is_superuser
    if lyrics.user_id != current_user.id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only lyrics owner or admin can view feedback.",
        )

    feedback_list = await crud_feedback.get_by_lyrics(db=db, lyrics_id=lyrics_id)

    return feedback_list


@router.get(
    "/stats",
    response_model=FeedbackStats,
    summary="Get feedback statistics",
    description="Get overall feedback statistics (admin only)",
)
async def get_feedback_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Get feedback statistics across all users.

    Returns:
    - Total feedback count
    - Average rating
    - Rating distribution
    - Recent feedback count (last 7 days)

    **Admin only**: This endpoint requires admin role.
    """
    logger.debug(f"Admin {current_user.id} fetching feedback statistics")

    stats = await crud_feedback.get_stats(db=db)

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

    Only the feedback author or admin can delete feedback.
    """
    logger.info(f"Deleting feedback {feedback_id} by user {current_user.id}")

    # Get existing feedback
    feedback = await crud_feedback.get(db=db, id=feedback_id)

    if not feedback:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")

    # Check ownership or admin permission
    is_admin = current_user.role == "admin" or current_user.is_superuser
    is_owner = feedback.user_id == current_user.id

    if not is_owner and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own feedback or must be an admin",
        )

    try:
        # Delete feedback
        await db.delete(feedback)

        await db.commit()

        logger.info(
            f"Feedback {feedback_id} deleted successfully by "
            f"{'admin' if is_admin else 'owner'} {current_user.id}"
        )
        return None

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feedback deletion failed: {str(e)}",
        )
