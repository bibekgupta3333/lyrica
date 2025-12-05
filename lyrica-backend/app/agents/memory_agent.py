"""
Memory Agent for Learning and Recommending Mixing Configurations.

This agent learns from successful mixing configurations and reference tracks,
providing intelligent recommendations for mixing based on genre, mood, and
user preferences.
"""

import uuid
from typing import Dict, Optional

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.state import AgentState, AgentStatus, WorkflowStatus
from app.core.music_config import MusicGenre
from app.services.memory import get_config_storage, get_reference_storage
from app.services.production.genre_mixing import (
    get_genre_classification,
    get_genre_mixing_presets,
    get_reference_analysis,
)


class MemoryAgent:
    """
    Memory Agent responsible for learning and recommending mixing configurations.

    This agent:
    1. Learns from successful mixing configurations
    2. Analyzes reference tracks to extract mixing patterns
    3. Provides mixing recommendations based on genre, mood, and context
    4. Stores learned patterns in the memory system
    """

    def __init__(self, llm_provider: str = None):
        """
        Initialize the memory agent.

        Args:
            llm_provider: LLM provider to use (optional, for future LLM-based learning)
        """
        self.name = "Memory"
        self.config_storage = get_config_storage()
        self.reference_storage = get_reference_storage()
        self.genre_classifier = get_genre_classification()
        self.genre_presets = get_genre_mixing_presets()
        self.reference_analysis = get_reference_analysis()
        logger.info(f"Initialized {self.name} agent")

    async def run(self, state: AgentState, db: Optional[AsyncSession] = None) -> Dict:
        """
        Execute the memory agent.

        Args:
            state: Current agent state
            db: Optional database session for storing learned configurations

        Returns:
            Dictionary with state updates including mixing recommendations
        """
        logger.info(f"{self.name} agent starting for user {state.user_id}")
        state.mark_agent_running(self.name)

        try:
            # Get genre (classify if not provided)
            genre = state.genre
            if not genre:
                # Classify genre from prompt/context (simplified)
                genre = self._infer_genre_from_context(state)

            # Get mixing recommendations
            recommendations = await self._get_mixing_recommendations(state, genre, db)

            # Store learned patterns if database session provided
            if db:
                await self._learn_from_state(state, genre, recommendations, db)

            state.mark_agent_completed(self.name)

            return {
                "memory_status": AgentStatus.COMPLETED,
                "mixing_recommendations": recommendations,
                "learned_genre": genre,
            }

        except Exception as e:
            logger.error(f"{self.name} agent failed: {str(e)}")
            state.mark_agent_failed(self.name, str(e))
            return {
                "memory_status": AgentStatus.FAILED,
                "errors": [f"Memory agent failed: {str(e)}"],
            }

    async def _get_mixing_recommendations(
        self, state: AgentState, genre: str, db: Optional[AsyncSession]
    ) -> Dict:
        """
        Get mixing recommendations based on state and genre.

        Args:
            state: Current agent state
            genre: Detected or specified genre
            db: Optional database session

        Returns:
            Dictionary with mixing recommendations
        """
        recommendations = {}

        # Get genre-specific preset
        try:
            genre_enum = MusicGenre(genre.lower())
            preset = self.genre_presets.get_mixing_preset(genre_enum)
            recommendations["genre_preset"] = preset
        except ValueError:
            # Default to pop if genre not recognized
            preset = self.genre_presets.get_mixing_preset(MusicGenre.POP)
            recommendations["genre_preset"] = preset

        # Get learned configurations from database
        if db:
            try:
                learned_configs = await self.config_storage.get_configurations_by_genre(
                    db, genre, user_id=uuid.UUID(int=state.user_id) if state.user_id else None
                )

                if learned_configs:
                    # Use most frequently used configuration
                    best_config = max(learned_configs, key=lambda c: c.usage_count)
                    recommendations["learned_config"] = {
                        "id": str(best_config.id),
                        "eq_settings": best_config.eq_settings,
                        "compression_settings": best_config.compression_settings,
                        "stereo_width_settings": best_config.stereo_width_settings,
                        "reverb_settings": best_config.reverb_settings,
                        "delay_settings": best_config.delay_settings,
                        "sidechain_settings": best_config.sidechain_settings,
                        "usage_count": best_config.usage_count,
                    }
            except Exception as e:
                logger.warning(f"Failed to retrieve learned configurations: {e}")

        # Get reference track recommendations
        if db:
            try:
                reference_tracks = await self.reference_storage.get_reference_tracks_by_genre(
                    db, genre, user_id=uuid.UUID(int=state.user_id) if state.user_id else None
                )

                if reference_tracks:
                    # Use most frequently used reference track
                    best_reference = max(reference_tracks, key=lambda r: r.usage_count)
                    recommendations["reference_track"] = {
                        "id": str(best_reference.id),
                        "title": best_reference.title,
                        "artist": best_reference.artist,
                        "recommendations": best_reference.recommendations,
                        "eq_profile": best_reference.eq_profile,
                    }
            except Exception as e:
                logger.warning(f"Failed to retrieve reference tracks: {e}")

        return recommendations

    async def _learn_from_state(
        self,
        state: AgentState,
        genre: str,
        recommendations: Dict,
        db: AsyncSession,
    ) -> None:
        """
        Learn from the current state and store patterns.

        Args:
            state: Current agent state
            genre: Detected genre
            recommendations: Mixing recommendations
            db: Database session
        """
        # This would be called after successful song generation
        # to learn from successful configurations
        logger.debug(f"Learning from state for genre: {genre}")

        # Store successful configuration if available in metadata
        if "mixing_config" in state.metadata:
            config_data = state.metadata["mixing_config"]
            try:
                await self.config_storage.save_configuration(
                    db=db,
                    config_type="learned",
                    eq_settings=config_data.get("eq_settings", {}),
                    compression_settings=config_data.get("compression_settings", {}),
                    stereo_width_settings=config_data.get("stereo_width_settings", {}),
                    reverb_settings=config_data.get("reverb_settings", {}),
                    delay_settings=config_data.get("delay_settings", {}),
                    sidechain_settings=config_data.get("sidechain_settings", {}),
                    user_id=uuid.UUID(int=state.user_id) if state.user_id else None,
                    genre=genre,
                    name=f"Learned config for {genre}",
                )
            except Exception as e:
                logger.warning(f"Failed to store learned configuration: {e}")

    def _infer_genre_from_context(self, state: AgentState) -> str:
        """
        Infer genre from context (prompt, mood, theme).

        Args:
            state: Current agent state

        Returns:
            Inferred genre string
        """
        # Simple heuristic-based genre inference
        prompt_lower = state.prompt.lower()
        mood_lower = (state.mood or "").lower()
        theme_lower = (state.theme or "").lower()

        context = f"{prompt_lower} {mood_lower} {theme_lower}"

        # Genre keywords
        genre_keywords = {
            "rock": ["rock", "guitar", "electric", "power", "aggressive"],
            "pop": ["pop", "catchy", "radio", "mainstream"],
            "hiphop": ["hip", "hop", "rap", "beat", "urban"],
            "electronic": ["electronic", "edm", "dance", "synth", "techno"],
            "jazz": ["jazz", "smooth", "saxophone", "swing"],
            "country": ["country", "cowboy", "ranch", "western"],
            "rnb": ["rnb", "r&b", "soul", "smooth"],
        }

        for genre, keywords in genre_keywords.items():
            if any(keyword in context for keyword in keywords):
                return genre

        # Default to pop
        return "pop"

    async def recommend_mixing_for_song(
        self,
        state: AgentState,
        song_id: Optional[uuid.UUID],
        db: AsyncSession,
    ) -> Dict:
        """
        Recommend mixing configuration for a completed song.

        Args:
            state: Current agent state
            song_id: Optional song ID
            db: Database session

        Returns:
            Dictionary with mixing recommendations
        """
        genre = state.genre or self._infer_genre_from_context(state)
        recommendations = await self._get_mixing_recommendations(state, genre, db)

        # Store recommendation in state metadata
        if "mixing_recommendations" not in state.metadata:
            state.metadata["mixing_recommendations"] = recommendations

        return recommendations
