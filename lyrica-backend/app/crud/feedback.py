"""
CRUD operations for Feedback model.
"""

from datetime import datetime, timedelta
from typing import List
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.feedback import UserFeedback
from app.schemas.feedback import FeedbackCreate


class CRUDFeedback(CRUDBase[UserFeedback, FeedbackCreate, dict]):
    """CRUD operations for UserFeedback model."""

    async def create_with_user(
        self, db: AsyncSession, *, obj_in: FeedbackCreate, user_id: UUID
    ) -> UserFeedback:
        """
        Create feedback for a specific user.

        Args:
            db: Database session
            obj_in: Feedback creation schema
            user_id: User ID

        Returns:
            Created feedback instance
        """
        obj_in_data = obj_in.model_dump()
        db_obj = UserFeedback(**obj_in_data, user_id=user_id)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_user(
        self, db: AsyncSession, *, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[UserFeedback]:
        """
        Get all feedback from a specific user.

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of feedback
        """
        result = await db.execute(
            select(UserFeedback)
            .where(UserFeedback.user_id == user_id)
            .order_by(UserFeedback.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_lyrics(self, db: AsyncSession, *, lyrics_id: UUID) -> List[UserFeedback]:
        """
        Get all feedback for specific lyrics.

        Args:
            db: Database session
            lyrics_id: Lyrics ID

        Returns:
            List of feedback
        """
        result = await db.execute(
            select(UserFeedback)
            .where(UserFeedback.lyrics_id == lyrics_id)
            .order_by(UserFeedback.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_stats(self, db: AsyncSession) -> dict:
        """
        Get feedback statistics.

        Args:
            db: Database session

        Returns:
            Dictionary with feedback statistics
        """
        # Total feedback count
        total_result = await db.execute(select(func.count(UserFeedback.id)))
        total_feedback = total_result.scalar() or 0

        # Average rating
        avg_result = await db.execute(select(func.avg(UserFeedback.overall_rating)))
        average_rating = float(avg_result.scalar() or 0)

        # Rating distribution
        rating_dist_result = await db.execute(
            select(UserFeedback.overall_rating, func.count(UserFeedback.id)).group_by(
                UserFeedback.overall_rating
            )
        )
        rating_distribution = {str(rating): count for rating, count in rating_dist_result.all()}

        # Feedback by tags (most common tags)
        # For simplicity, just count total feedback with tags
        tagged_result = await db.execute(
            select(func.count(UserFeedback.id)).where(UserFeedback.comment.isnot(None))
        )
        feedback_with_comments = tagged_result.scalar() or 0

        # Recent feedback (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_result = await db.execute(
            select(func.count(UserFeedback.id)).where(UserFeedback.created_at >= seven_days_ago)
        )
        recent_feedback_count = recent_result.scalar() or 0

        return {
            "total_feedback": total_feedback,
            "average_rating": round(average_rating, 2),
            "rating_distribution": rating_distribution,
            "feedback_with_comments": feedback_with_comments,
            "recent_feedback_count": recent_feedback_count,
        }


# Create singleton instance
feedback = CRUDFeedback(UserFeedback)
