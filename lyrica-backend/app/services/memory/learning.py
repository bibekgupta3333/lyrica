"""
Learning mechanisms for mixing configuration optimization.

This module provides:
- User feedback collection for mixing configurations
- Quality metrics tracking over time
- Parameter optimization algorithms
- Feedback-to-improvement loop
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mixing_config import MixingConfiguration
from app.models.mixing_feedback import MixingFeedback, QualityMetricHistory
from app.services.memory.config_storage import get_config_storage


class FeedbackCollectionService:
    """Service for collecting and managing mixing feedback."""

    def __init__(self):
        """Initialize feedback collection service."""
        logger.success("FeedbackCollectionService initialized")

    async def collect_feedback(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        song_id: Optional[uuid.UUID],
        mixing_config_id: Optional[uuid.UUID],
        overall_mixing_rating: Optional[int] = None,
        vocals_clarity_rating: Optional[int] = None,
        music_balance_rating: Optional[int] = None,
        stereo_width_rating: Optional[int] = None,
        eq_quality_rating: Optional[int] = None,
        reverb_quality_rating: Optional[int] = None,
        pesq_score: Optional[float] = None,
        stoi_score: Optional[float] = None,
        mos_score: Optional[float] = None,
        overall_quality_score: Optional[float] = None,
        comment: Optional[str] = None,
        tags: Optional[List[str]] = None,
        improvement_suggestions: Optional[Dict] = None,
        is_liked: bool = False,
        would_use_again: bool = False,
        genre: Optional[str] = None,
        mood: Optional[str] = None,
    ) -> MixingFeedback:
        """
        Collect feedback for a mixing configuration.

        Args:
            db: Database session
            user_id: User ID
            song_id: Optional song ID
            mixing_config_id: Optional mixing configuration ID
            overall_mixing_rating: Overall mixing rating (1-5)
            vocals_clarity_rating: Vocals clarity rating (1-5)
            music_balance_rating: Music balance rating (1-5)
            stereo_width_rating: Stereo width rating (1-5)
            eq_quality_rating: EQ quality rating (1-5)
            reverb_quality_rating: Reverb quality rating (1-5)
            pesq_score: PESQ score from automated evaluation
            stoi_score: STOI score from automated evaluation
            mos_score: MOS score from automated evaluation
            overall_quality_score: Overall quality score
            comment: Optional comment
            tags: Optional tags
            improvement_suggestions: Optional improvement suggestions dict
            is_liked: Whether user liked the mixing
            would_use_again: Whether user would use this config again
            genre: Optional genre
            mood: Optional mood

        Returns:
            Created MixingFeedback instance
        """
        logger.info(f"Collecting feedback for mixing config: {mixing_config_id}")

        feedback = MixingFeedback(
            user_id=user_id,
            song_id=song_id,
            mixing_config_id=mixing_config_id,
            overall_mixing_rating=overall_mixing_rating,
            vocals_clarity_rating=vocals_clarity_rating,
            music_balance_rating=music_balance_rating,
            stereo_width_rating=stereo_width_rating,
            eq_quality_rating=eq_quality_rating,
            reverb_quality_rating=reverb_quality_rating,
            pesq_score=pesq_score,
            stoi_score=stoi_score,
            mos_score=mos_score,
            overall_quality_score=overall_quality_score,
            comment=comment,
            tags=tags or [],
            improvement_suggestions=improvement_suggestions or {},
            is_liked=is_liked,
            would_use_again=would_use_again,
            genre=genre,
            mood=mood,
        )

        db.add(feedback)
        await db.commit()
        await db.refresh(feedback)

        logger.success(f"Feedback collected: {feedback.id}")
        return feedback

    async def get_feedback_for_config(
        self, db: AsyncSession, mixing_config_id: uuid.UUID
    ) -> List[MixingFeedback]:
        """
        Get all feedback for a mixing configuration.

        Args:
            db: Database session
            mixing_config_id: Mixing configuration ID

        Returns:
            List of MixingFeedback instances
        """
        result = await db.execute(
            select(MixingFeedback)
            .where(MixingFeedback.mixing_config_id == mixing_config_id)
            .order_by(MixingFeedback.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_average_ratings(
        self, db: AsyncSession, mixing_config_id: uuid.UUID
    ) -> Dict[str, float]:
        """
        Get average ratings for a mixing configuration.

        Args:
            db: Database session
            mixing_config_id: Mixing configuration ID

        Returns:
            Dictionary with average ratings
        """
        result = await db.execute(
            select(
                func.avg(MixingFeedback.overall_mixing_rating).label("avg_overall"),
                func.avg(MixingFeedback.vocals_clarity_rating).label("avg_vocals"),
                func.avg(MixingFeedback.music_balance_rating).label("avg_music"),
                func.avg(MixingFeedback.stereo_width_rating).label("avg_stereo"),
                func.avg(MixingFeedback.eq_quality_rating).label("avg_eq"),
                func.avg(MixingFeedback.reverb_quality_rating).label("avg_reverb"),
                func.avg(MixingFeedback.overall_quality_score).label("avg_quality"),
                func.count(MixingFeedback.id).label("count"),
            ).where(MixingFeedback.mixing_config_id == mixing_config_id)
        )
        row = result.first()

        if row and row.count > 0:
            return {
                "overall_mixing": float(row.avg_overall or 0),
                "vocals_clarity": float(row.avg_vocals or 0),
                "music_balance": float(row.avg_music or 0),
                "stereo_width": float(row.avg_stereo or 0),
                "eq_quality": float(row.avg_eq or 0),
                "reverb_quality": float(row.avg_reverb or 0),
                "overall_quality": float(row.avg_quality or 0),
                "feedback_count": int(row.count),
            }
        return {
            "overall_mixing": 0.0,
            "vocals_clarity": 0.0,
            "music_balance": 0.0,
            "stereo_width": 0.0,
            "eq_quality": 0.0,
            "reverb_quality": 0.0,
            "overall_quality": 0.0,
            "feedback_count": 0,
        }


class QualityTrackingService:
    """Service for tracking quality metrics over time."""

    def __init__(self):
        """Initialize quality tracking service."""
        logger.success("QualityTrackingService initialized")

    async def track_quality_metrics(
        self,
        db: AsyncSession,
        mixing_config_id: Optional[uuid.UUID],
        song_id: Optional[uuid.UUID],
        pesq_score: Optional[float] = None,
        stoi_score: Optional[float] = None,
        mos_score: Optional[float] = None,
        overall_score: Optional[float] = None,
        avg_user_rating: Optional[float] = None,
        feedback_count: int = 0,
        genre: Optional[str] = None,
    ) -> QualityMetricHistory:
        """
        Track quality metrics for a mixing configuration.

        Args:
            db: Database session
            mixing_config_id: Optional mixing configuration ID
            song_id: Optional song ID
            pesq_score: PESQ score
            stoi_score: STOI score
            mos_score: MOS score
            overall_score: Overall quality score
            avg_user_rating: Average user rating
            feedback_count: Number of feedback entries
            genre: Optional genre

        Returns:
            Created QualityMetricHistory instance
        """
        logger.info(f"Tracking quality metrics for config: {mixing_config_id}")

        history = QualityMetricHistory(
            mixing_config_id=mixing_config_id,
            song_id=song_id,
            pesq_score=pesq_score,
            stoi_score=stoi_score,
            mos_score=mos_score,
            overall_score=overall_score,
            avg_user_rating=avg_user_rating,
            feedback_count=feedback_count,
            genre=genre,
            sample_count=1,
        )

        db.add(history)
        await db.commit()
        await db.refresh(history)

        logger.success(f"Quality metrics tracked: {history.id}")
        return history

    async def get_quality_trends(
        self,
        db: AsyncSession,
        mixing_config_id: uuid.UUID,
        days: int = 30,
    ) -> List[QualityMetricHistory]:
        """
        Get quality trends over time for a mixing configuration.

        Args:
            db: Database session
            mixing_config_id: Mixing configuration ID
            days: Number of days to look back

        Returns:
            List of QualityMetricHistory instances ordered by date
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        result = await db.execute(
            select(QualityMetricHistory)
            .where(
                QualityMetricHistory.mixing_config_id == mixing_config_id,
                QualityMetricHistory.created_at >= cutoff_date,
            )
            .order_by(QualityMetricHistory.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_average_quality_over_time(
        self,
        db: AsyncSession,
        mixing_config_id: uuid.UUID,
        days: int = 30,
    ) -> Dict[str, float]:
        """
        Get average quality metrics over time.

        Args:
            db: Database session
            mixing_config_id: Mixing configuration ID
            days: Number of days to look back

        Returns:
            Dictionary with average metrics
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        result = await db.execute(
            select(
                func.avg(QualityMetricHistory.pesq_score).label("avg_pesq"),
                func.avg(QualityMetricHistory.stoi_score).label("avg_stoi"),
                func.avg(QualityMetricHistory.mos_score).label("avg_mos"),
                func.avg(QualityMetricHistory.overall_score).label("avg_overall"),
                func.avg(QualityMetricHistory.avg_user_rating).label("avg_rating"),
                func.sum(QualityMetricHistory.sample_count).label("total_samples"),
            ).where(
                QualityMetricHistory.mixing_config_id == mixing_config_id,
                QualityMetricHistory.created_at >= cutoff_date,
            )
        )
        row = result.first()

        if row and row.total_samples:
            return {
                "avg_pesq": float(row.avg_pesq or 0),
                "avg_stoi": float(row.avg_stoi or 0),
                "avg_mos": float(row.avg_mos or 0),
                "avg_overall": float(row.avg_overall or 0),
                "avg_user_rating": float(row.avg_rating or 0),
                "total_samples": int(row.total_samples),
            }
        return {
            "avg_pesq": 0.0,
            "avg_stoi": 0.0,
            "avg_mos": 0.0,
            "avg_overall": 0.0,
            "avg_user_rating": 0.0,
            "total_samples": 0,
        }


class ParameterOptimizationService:
    """Service for optimizing mixing parameters based on feedback."""

    def __init__(self):
        """Initialize parameter optimization service."""
        self.config_storage = get_config_storage()
        logger.success("ParameterOptimizationService initialized")

    async def optimize_parameters(
        self,
        db: AsyncSession,
        mixing_config_id: uuid.UUID,
        feedback_service: FeedbackCollectionService,
    ) -> Optional[MixingConfiguration]:
        """
        Optimize mixing parameters based on feedback.

        Args:
            db: Database session
            mixing_config_id: Mixing configuration ID to optimize
            feedback_service: Feedback collection service

        Returns:
            Optimized MixingConfiguration or None if optimization not possible
        """
        logger.info(f"Optimizing parameters for config: {mixing_config_id}")

        # Get current configuration
        config = await self.config_storage.get_configuration(db, mixing_config_id)
        if not config:
            logger.warning(f"Configuration not found: {mixing_config_id}")
            return None

        # Get feedback
        avg_ratings = await feedback_service.get_average_ratings(db, mixing_config_id)
        if avg_ratings["feedback_count"] < 3:
            logger.info("Insufficient feedback for optimization (need at least 3)")
            return None

        # Optimize based on feedback
        optimized_settings = self._optimize_settings(config, avg_ratings)

        # Create optimized configuration
        optimized_config = await self.config_storage.save_configuration(
            db=db,
            config_type="optimized",
            eq_settings=optimized_settings["eq_settings"],
            compression_settings=optimized_settings["compression_settings"],
            stereo_width_settings=optimized_settings["stereo_width_settings"],
            reverb_settings=optimized_settings["reverb_settings"],
            delay_settings=optimized_settings["delay_settings"],
            sidechain_settings=optimized_settings["sidechain_settings"],
            user_id=config.user_id,
            genre=config.genre,
            name=f"Optimized: {config.name or 'Untitled'}",
            description=f"Optimized based on {avg_ratings['feedback_count']} feedback entries",
        )

        logger.success(f"Parameters optimized: {optimized_config.id}")
        return optimized_config

    def _optimize_settings(
        self, config: MixingConfiguration, avg_ratings: Dict[str, float]
    ) -> Dict:
        """
        Optimize settings based on average ratings.

        Args:
            config: Current configuration
            avg_ratings: Average ratings from feedback

        Returns:
            Dictionary with optimized settings
        """
        optimized = {
            "eq_settings": config.eq_settings.copy(),
            "compression_settings": config.compression_settings.copy(),
            "stereo_width_settings": config.stereo_width_settings.copy(),
            "reverb_settings": config.reverb_settings.copy(),
            "delay_settings": config.delay_settings.copy(),
            "sidechain_settings": config.sidechain_settings.copy(),
        }

        # Optimize EQ based on vocals clarity rating
        if avg_ratings["vocals_clarity"] < 3.5:
            # Boost mid frequencies for vocals
            if "vocals" in optimized["eq_settings"]:
                vocals_eq = optimized["eq_settings"]["vocals"]
                if "mid_db" not in vocals_eq:
                    vocals_eq["mid_db"] = 0
                vocals_eq["mid_db"] = min(vocals_eq["mid_db"] + 1.5, 3.0)

        # Optimize stereo width based on rating
        if avg_ratings["stereo_width"] < 3.5:
            if "vocals" in optimized["stereo_width_settings"]:
                optimized["stereo_width_settings"]["vocals"] = min(
                    optimized["stereo_width_settings"].get("vocals", 1.0) + 0.2, 2.0
                )

        # Optimize reverb based on rating
        if avg_ratings["reverb_quality"] < 3.5:
            if "vocals" in optimized["reverb_settings"]:
                reverb = optimized["reverb_settings"]["vocals"]
                if "wet_level" in reverb:
                    reverb["wet_level"] = max(reverb["wet_level"] - 0.1, 0.1)

        return optimized


class FeedbackLoopService:
    """Service for creating feedback-to-improvement loop."""

    def __init__(self):
        """Initialize feedback loop service."""
        self.feedback_service = FeedbackCollectionService()
        self.quality_tracking = QualityTrackingService()
        self.optimization_service = ParameterOptimizationService()
        logger.success("FeedbackLoopService initialized")

    async def process_feedback_and_optimize(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        song_id: Optional[uuid.UUID],
        mixing_config_id: uuid.UUID,
        feedback_data: Dict,
        quality_metrics: Optional[Dict] = None,
    ) -> Dict:
        """
        Process feedback and trigger optimization if needed.

        Args:
            db: Database session
            user_id: User ID
            song_id: Optional song ID
            mixing_config_id: Mixing configuration ID
            feedback_data: Dictionary with feedback data
            quality_metrics: Optional quality metrics from automated evaluation

        Returns:
            Dictionary with processing results
        """
        logger.info(f"Processing feedback for config: {mixing_config_id}")

        # Collect feedback
        feedback = await self.feedback_service.collect_feedback(
            db=db,
            user_id=user_id,
            song_id=song_id,
            mixing_config_id=mixing_config_id,
            **feedback_data,
            **(
                quality_metrics
                if quality_metrics
                else {
                    "pesq_score": None,
                    "stoi_score": None,
                    "mos_score": None,
                    "overall_quality_score": None,
                }
            ),
        )

        # Track quality metrics
        if quality_metrics:
            await self.quality_tracking.track_quality_metrics(
                db=db,
                mixing_config_id=mixing_config_id,
                song_id=song_id,
                **quality_metrics,
            )

        # Check if optimization is needed
        avg_ratings = await self.feedback_service.get_average_ratings(db, mixing_config_id)

        optimization_triggered = False
        optimized_config = None

        if avg_ratings["feedback_count"] >= 5 and avg_ratings["overall_mixing"] < 3.5:
            logger.info("Triggering parameter optimization due to low ratings")
            optimized_config = await self.optimization_service.optimize_parameters(
                db, mixing_config_id, self.feedback_service
            )
            optimization_triggered = optimized_config is not None

        return {
            "feedback_id": str(feedback.id),
            "avg_ratings": avg_ratings,
            "optimization_triggered": optimization_triggered,
            "optimized_config_id": str(optimized_config.id) if optimized_config else None,
        }


# Singleton instances
_feedback_collection_service: Optional[FeedbackCollectionService] = None
_quality_tracking_service: Optional[QualityTrackingService] = None
_parameter_optimization_service: Optional[ParameterOptimizationService] = None
_feedback_loop_service: Optional[FeedbackLoopService] = None


def get_feedback_collection() -> FeedbackCollectionService:
    """Get or create feedback collection service instance."""
    global _feedback_collection_service
    if _feedback_collection_service is None:
        _feedback_collection_service = FeedbackCollectionService()
    return _feedback_collection_service


def get_quality_tracking() -> QualityTrackingService:
    """Get or create quality tracking service instance."""
    global _quality_tracking_service
    if _quality_tracking_service is None:
        _quality_tracking_service = QualityTrackingService()
    return _quality_tracking_service


def get_parameter_optimization() -> ParameterOptimizationService:
    """Get or create parameter optimization service instance."""
    global _parameter_optimization_service
    if _parameter_optimization_service is None:
        _parameter_optimization_service = ParameterOptimizationService()
    return _parameter_optimization_service


def get_feedback_loop() -> FeedbackLoopService:
    """Get or create feedback loop service instance."""
    global _feedback_loop_service
    if _feedback_loop_service is None:
        _feedback_loop_service = FeedbackLoopService()
    return _feedback_loop_service
