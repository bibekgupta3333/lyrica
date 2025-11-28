#!/usr/bin/env python3
"""
Test Script for Multi-Agent Song Generation Workflow.

This script tests the complete agent workflow including Planning,
Generation, Refinement, and Evaluation agents.

Usage:
    python scripts/test_agent_workflow.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

from app.agents import get_orchestrator
from app.agents.state import WorkflowStatus


async def test_simple_song():
    """Test a simple song generation."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 1: Simple Song Generation")
    logger.info("=" * 80 + "\n")

    orchestrator = get_orchestrator(
        llm_provider="ollama",
        quality_threshold=5.0,  # Lower threshold for testing
        max_refinement_iterations=1,
    )

    result = await orchestrator.generate_song(
        user_id=1,
        prompt="A happy song about sunshine and good times",
        genre="pop",
        mood="upbeat",
        length="short",
        use_rag=False,  # Disable RAG for faster testing
        max_retries=1,
    )

    # Print results
    logger.info(f"\n{'=' * 80}")
    logger.info(f"WORKFLOW STATUS: {result.workflow_status}")
    logger.info(f"{'=' * 80}\n")

    if result.title:
        logger.info(f"📝 TITLE: {result.title}\n")

    if result.song_structure:
        logger.info(f"📋 STRUCTURE ({result.song_structure.structure_type}):")
        for section in result.song_structure.sections:
            logger.info(f"  {section.order}. {section.type.upper()} ({section.length} lines)")
        logger.info("")

    if result.final_lyrics:
        logger.info(f"🎵 FINAL LYRICS:\n{result.final_lyrics}\n")

    if result.evaluation_score:
        logger.info(f"⭐ EVALUATION SCORES:")
        logger.info(f"  Overall: {result.evaluation_score.overall:.1f}/10")
        logger.info(f"  Creativity: {result.evaluation_score.creativity:.1f}/10")
        logger.info(f"  Coherence: {result.evaluation_score.coherence:.1f}/10")
        logger.info(f"  Rhyme Quality: {result.evaluation_score.rhyme_quality:.1f}/10")
        logger.info(f"  Emotional Impact: {result.evaluation_score.emotional_impact:.1f}/10")
        logger.info(f"  Genre Fit: {result.evaluation_score.genre_fit:.1f}/10")
        logger.info(f"\n  Feedback: {result.evaluation_score.feedback}\n")

    logger.info(f"📊 METADATA:")
    logger.info(f"  Refinement iterations: {result.refinement_iterations}")
    logger.info(f"  Retry count: {result.retry_count}")
    logger.info(f"  Total messages: {len(result.messages)}")
    logger.info(f"  Errors: {len(result.errors)}\n")

    if result.errors:
        logger.warning(f"⚠️  ERRORS:")
        for error in result.errors:
            logger.warning(f"  - {error}")
        logger.info("")

    # Return success status
    return result.workflow_status == WorkflowStatus.COMPLETED


async def test_complex_song_with_rag():
    """Test a complex song generation with RAG."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: Complex Song with RAG")
    logger.info("=" * 80 + "\n")

    orchestrator = get_orchestrator(
        llm_provider="ollama",
        quality_threshold=6.0,
        max_refinement_iterations=2,
    )

    result = await orchestrator.generate_song(
        user_id=1,
        prompt="A melancholic ballad about losing someone you love and the memories that remain",
        genre="ballad",
        mood="melancholic",
        theme="lost love",
        length="medium",
        style_references=["Adele", "Sam Smith"],
        use_rag=True,  # Enable RAG for context
        max_retries=2,
    )

    # Print results (abbreviated)
    logger.info(f"\n{'=' * 80}")
    logger.info(f"WORKFLOW STATUS: {result.workflow_status}")
    logger.info(f"{'=' * 80}\n")

    if result.title:
        logger.info(f"📝 TITLE: {result.title}\n")

    if result.final_lyrics:
        # Print first 500 characters
        preview = result.final_lyrics[:500]
        if len(result.final_lyrics) > 500:
            preview += "...\n(truncated)"
        logger.info(f"🎵 LYRICS PREVIEW:\n{preview}\n")

    if result.evaluation_score:
        logger.info(f"⭐ OVERALL SCORE: {result.evaluation_score.overall:.2f}/10\n")

    logger.info(f"📊 METADATA:")
    logger.info(
        f"  Structure: {result.song_structure.structure_type if result.song_structure else 'N/A'}"
    )
    logger.info(
        f"  Sections: {result.song_structure.total_sections if result.song_structure else 0}"
    )
    logger.info(f"  RAG contexts used: {len(result.rag_context)}")
    logger.info(f"  Refinement iterations: {result.refinement_iterations}")
    logger.info(f"  Retry count: {result.retry_count}")

    # Duration
    if result.workflow_end_time and result.workflow_start_time:
        duration = (result.workflow_end_time - result.workflow_start_time).total_seconds()
        logger.info(f"  Duration: {duration:.2f}s\n")

    # Return success status
    return result.workflow_status == WorkflowStatus.COMPLETED


async def test_agent_messages():
    """Test agent message tracking."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: Agent Message Tracking")
    logger.info("=" * 80 + "\n")

    orchestrator = get_orchestrator(
        llm_provider="ollama",
        quality_threshold=5.0,
        max_refinement_iterations=1,
    )

    result = await orchestrator.generate_song(
        user_id=1,
        prompt="A short song about cats",
        genre="folk",
        length="short",
        use_rag=False,
        max_retries=1,
    )

    # Print agent messages
    logger.info(f"📨 AGENT MESSAGES ({len(result.messages)} total):\n")
    for msg in result.messages:
        level_emoji = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
        }.get(msg.level, "📝")

        logger.info(f"{level_emoji} [{msg.agent}] {msg.message}")

    logger.info("")

    return result.workflow_status == WorkflowStatus.COMPLETED


async def main():
    """Run all tests."""
    logger.info("\n" + "=" * 80)
    logger.info("MULTI-AGENT SONG GENERATION WORKFLOW TEST SUITE")
    logger.info("=" * 80 + "\n")

    logger.info("Testing the LangGraph-orchestrated multi-agent system for song generation.")
    logger.info("This will test: Planning, Generation, Refinement, and Evaluation agents.\n")

    results = []

    # Test 1: Simple song
    try:
        success = await test_simple_song()
        results.append(("Simple Song", success))
    except Exception as e:
        logger.error(f"Test 1 failed: {str(e)}")
        results.append(("Simple Song", False))

    # Test 2: Complex song with RAG
    try:
        success = await test_complex_song_with_rag()
        results.append(("Complex Song with RAG", success))
    except Exception as e:
        logger.error(f"Test 2 failed: {str(e)}")
        results.append(("Complex Song with RAG", False))

    # Test 3: Message tracking
    try:
        success = await test_agent_messages()
        results.append(("Agent Messages", success))
    except Exception as e:
        logger.error(f"Test 3 failed: {str(e)}")
        results.append(("Agent Messages", False))

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80 + "\n")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"{status}: {test_name}")

    logger.info(f"\n{'=' * 80}")
    logger.info(f"FINAL RESULT: {passed}/{total} tests passed")
    logger.info(f"{'=' * 80}\n")

    # Exit with appropriate code
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    asyncio.run(main())
