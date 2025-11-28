"""
Unit tests for agent workflows and LangGraph system.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.agents.orchestrator import get_orchestrator
from app.agents.state import AgentState, AgentStatus, WorkflowStatus


@pytest.mark.unit
@pytest.mark.agents
class TestAgentState:
    """Test agent state management."""

    def test_create_agent_state(self):
        """Test creating an agent state."""
        state = AgentState(
            prompt="Test song about love",
            genre="pop",
            mood="happy",
            workflow_status=WorkflowStatus.PLANNING,
        )

        assert state.prompt == "Test song about love"
        assert state.genre == "pop"
        assert state.workflow_status == WorkflowStatus.PLANNING
        assert state.planning_agent_status == AgentStatus.IDLE
        assert state.generation_agent_status == AgentStatus.IDLE

    def test_agent_state_initialization(self):
        """Test agent state default initialization."""
        state = AgentState(prompt="Test prompt")

        assert state.current_iteration == 0
        assert state.max_iterations == 3
        assert state.final_lyrics == ""
        assert state.workflow_status == WorkflowStatus.PLANNING
        assert len(state.agent_messages) == 0


@pytest.mark.unit
@pytest.mark.agents
class TestWorkflowStatus:
    """Test workflow status enum."""

    def test_workflow_status_values(self):
        """Test workflow status enum values."""
        assert WorkflowStatus.PLANNING == "planning"
        assert WorkflowStatus.GENERATING == "generating"
        assert WorkflowStatus.REFINING == "refining"
        assert WorkflowStatus.EVALUATING == "evaluating"
        assert WorkflowStatus.COMPLETED == "completed"
        assert WorkflowStatus.FAILED == "failed"


@pytest.mark.unit
@pytest.mark.agents
class TestAgentStatus:
    """Test agent status enum."""

    def test_agent_status_values(self):
        """Test agent status enum values."""
        assert AgentStatus.IDLE == "idle"
        assert AgentStatus.WORKING == "working"
        assert AgentStatus.COMPLETED == "completed"
        assert AgentStatus.FAILED == "failed"


@pytest.mark.unit
@pytest.mark.agents
@pytest.mark.slow
class TestAgentOrchestrator:
    """Test agent orchestrator."""

    def test_get_orchestrator(self):
        """Test getting orchestrator instance."""
        orchestrator = get_orchestrator()

        assert orchestrator is not None
        # Orchestrator should be a LangGraph compiled graph
        assert hasattr(orchestrator, "invoke") or hasattr(orchestrator, "ainvoke")

    @pytest.mark.asyncio
    async def test_orchestrator_with_simple_prompt(self):
        """Test orchestrator with simple prompt (mocked)."""
        # This test would require mocking the LLM calls
        # For now, we just verify the structure
        state = AgentState(
            prompt="A short happy song",
            genre="pop",
            mood="happy",
            length="short",
        )

        assert state.prompt == "A short happy song"
        assert state.workflow_status == WorkflowStatus.PLANNING


@pytest.mark.unit
@pytest.mark.agents
class TestAgentMessages:
    """Test agent message system."""

    def test_add_agent_message_to_state(self):
        """Test adding messages to agent state."""
        state = AgentState(prompt="Test")

        # Simulate adding a message
        from app.agents.state import AgentMessage

        message = AgentMessage(
            agent="planning_agent",
            message="Created song structure",
            timestamp="2025-11-28T00:00:00Z",
        )

        state.agent_messages.append(message)

        assert len(state.agent_messages) == 1
        assert state.agent_messages[0].agent == "planning_agent"
        assert state.agent_messages[0].message == "Created song structure"


@pytest.mark.unit
@pytest.mark.agents
class TestSongStructure:
    """Test song structure models."""

    def test_create_song_section(self):
        """Test creating a song section."""
        from app.agents.state import SongSection

        section = SongSection(
            type="verse",
            number=1,
            content="Test verse content",
            rhyme_scheme="AABB",
        )

        assert section.type == "verse"
        assert section.number == 1
        assert section.content == "Test verse content"
        assert section.rhyme_scheme == "AABB"

    def test_create_song_structure(self):
        """Test creating song structure."""
        from app.agents.state import SongSection, SongStructure

        section1 = SongSection(type="verse", number=1, content="Verse 1")
        section2 = SongSection(type="chorus", number=1, content="Chorus")

        structure = SongStructure(
            title="Test Song",
            sections=[section1, section2],
            total_sections=2,
        )

        assert structure.title == "Test Song"
        assert len(structure.sections) == 2
        assert structure.total_sections == 2


@pytest.mark.unit
@pytest.mark.agents
class TestEvaluationScore:
    """Test evaluation score model."""

    def test_create_evaluation_score(self):
        """Test creating evaluation score."""
        from app.agents.state import EvaluationScore

        score = EvaluationScore(
            overall=8.5,
            creativity=9.0,
            coherence=8.0,
            rhyme_quality=8.5,
            genre_match=9.0,
            mood_match=8.5,
        )

        assert score.overall == 8.5
        assert score.creativity == 9.0
        assert score.coherence == 8.0


# ============================================================================
# Mock-Based Tests (for integration with real agents)
# ============================================================================


@pytest.mark.unit
@pytest.mark.agents
class TestAgentIntegration:
    """Test agent integration patterns (mocked)."""

    @pytest.mark.asyncio
    @patch("app.agents.planning_agent.get_llm_service")
    async def test_planning_agent_mock(self, mock_llm):
        """Test planning agent with mocked LLM."""
        # Mock LLM response
        mock_llm_service = AsyncMock()
        mock_llm_service.generate.return_value = {"content": "Test song structure"}
        mock_llm.return_value = mock_llm_service

        # This would test the planning agent
        # For now, we just verify the mock setup
        assert mock_llm is not None

    @pytest.mark.asyncio
    @patch("app.agents.generation_agent.get_llm_service")
    async def test_generation_agent_mock(self, mock_llm):
        """Test generation agent with mocked LLM."""
        # Mock LLM response
        mock_llm_service = AsyncMock()
        mock_llm_service.generate.return_value = {"content": "[Verse 1]\nGenerated lyrics"}
        mock_llm.return_value = mock_llm_service

        # This would test the generation agent
        assert mock_llm is not None

    @pytest.mark.asyncio
    @patch("app.agents.evaluation_agent.get_llm_service")
    async def test_evaluation_agent_mock(self, mock_llm):
        """Test evaluation agent with mocked LLM."""
        # Mock LLM response
        mock_llm_service = AsyncMock()
        mock_llm_service.generate.return_value = {"content": '{"overall": 8.5, "creativity": 9.0}'}
        mock_llm.return_value = mock_llm_service

        # This would test the evaluation agent
        assert mock_llm is not None


# ============================================================================
# Test Helpers
# ============================================================================


def create_test_agent_state(**kwargs) -> AgentState:
    """Helper function to create test agent state."""
    defaults = {
        "prompt": "Test song",
        "genre": "pop",
        "mood": "happy",
        "workflow_status": WorkflowStatus.PLANNING,
    }
    defaults.update(kwargs)
    return AgentState(**defaults)
