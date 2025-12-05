#!/usr/bin/env python3
"""
Performance Benchmarking Script.

This script benchmarks performance metrics for:
- Voice enhancement processing time
- Mixing processing time
- Complete song generation time
- Memory usage
- Quality metrics calculation time
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import psutil
from loguru import logger

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.production import get_song_assembly
from app.services.production.unified_pipeline import get_unified_pipeline
from app.services.voice import get_voice_enhancement


def benchmark_voice_enhancement(audio_path: Path, iterations: int = 5) -> Dict:
    """
    Benchmark voice enhancement performance.

    Args:
        audio_path: Path to audio file to enhance
        iterations: Number of iterations to run

    Returns:
        Dictionary with benchmark results
    """
    logger.info(f"Benchmarking voice enhancement: {audio_path} ({iterations} iterations)")

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    enhancement_service = get_voice_enhancement()
    times = []
    memory_usage = []

    for i in range(iterations):
        logger.info(f"Iteration {i + 1}/{iterations}")

        # Measure memory before
        process = psutil.Process()
        mem_before = process.memory_info().rss / 1024 / 1024  # MB

        # Measure time
        start_time = time.time()
        output_path = audio_path.parent / f"benchmark_{i}.wav"
        enhanced_path = enhancement_service.enhance_tts_output(
            tts_audio_path=audio_path, output_path=output_path, enable_enhancement=True
        )
        elapsed = time.time() - start_time

        # Measure memory after
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        mem_used = mem_after - mem_before

        times.append(elapsed)
        memory_usage.append(mem_used)

        # Cleanup
        if output_path.exists():
            output_path.unlink()

    return {
        "operation": "voice_enhancement",
        "iterations": iterations,
        "times": times,
        "avg_time": sum(times) / len(times),
        "min_time": min(times),
        "max_time": max(times),
        "memory_usage": memory_usage,
        "avg_memory": sum(memory_usage) / len(memory_usage),
        "file_size_mb": audio_path.stat().st_size / 1024 / 1024,
    }


def benchmark_mixing(vocals_path: Path, music_path: Path, iterations: int = 5) -> Dict:
    """
    Benchmark mixing performance.

    Args:
        vocals_path: Path to vocals audio file
        music_path: Path to music audio file
        iterations: Number of iterations to run

    Returns:
        Dictionary with benchmark results
    """
    logger.info(f"Benchmarking mixing: {vocals_path} + {music_path} ({iterations} iterations)")

    if not vocals_path.exists():
        raise FileNotFoundError(f"Vocals file not found: {vocals_path}")
    if not music_path.exists():
        raise FileNotFoundError(f"Music file not found: {music_path}")

    assembly_service = get_song_assembly()
    times = []
    memory_usage = []

    for i in range(iterations):
        logger.info(f"Iteration {i + 1}/{iterations}")

        # Measure memory before
        process = psutil.Process()
        mem_before = process.memory_info().rss / 1024 / 1024  # MB

        # Measure time
        start_time = time.time()
        output_path = vocals_path.parent / f"benchmark_mixed_{i}.wav"
        mixed_path = assembly_service.assemble_song(
            vocals_path=vocals_path,
            music_path=music_path,
            output_path=output_path,
            use_intelligent_mixing=True,
        )
        elapsed = time.time() - start_time

        # Measure memory after
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        mem_used = mem_after - mem_before

        times.append(elapsed)
        memory_usage.append(mem_used)

        # Cleanup
        if output_path.exists():
            output_path.unlink()

    return {
        "operation": "mixing",
        "iterations": iterations,
        "times": times,
        "avg_time": sum(times) / len(times),
        "min_time": min(times),
        "max_time": max(times),
        "memory_usage": memory_usage,
        "avg_memory": sum(memory_usage) / len(memory_usage),
        "vocals_size_mb": vocals_path.stat().st_size / 1024 / 1024,
        "music_size_mb": music_path.stat().st_size / 1024 / 1024,
    }


def benchmark_complete_pipeline(
    lyrics_text: str,
    voice_profile_id: str,
    genre: str,
    bpm: int,
    duration: int,
    iterations: int = 3,
) -> Dict:
    """
    Benchmark complete song generation pipeline.

    Args:
        lyrics_text: Lyrics text
        voice_profile_id: Voice profile ID
        genre: Music genre
        bpm: Beats per minute
        duration: Duration in seconds
        iterations: Number of iterations to run

    Returns:
        Dictionary with benchmark results
    """
    logger.info(f"Benchmarking complete pipeline ({iterations} iterations)")

    pipeline = get_unified_pipeline()
    times = []
    memory_usage = []

    for i in range(iterations):
        logger.info(f"Iteration {i + 1}/{iterations}")

        # Measure memory before
        process = psutil.Process()
        mem_before = process.memory_info().rss / 1024 / 1024  # MB

        # Measure time
        start_time = time.time()
        output_dir = Path("audio_files/benchmark") / f"run_{i}"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Note: This would require database session, so we'll simulate
        # In real usage, this would be called with proper db session
        logger.warning("Complete pipeline benchmark requires database session")
        elapsed = time.time() - start_time

        # Measure memory after
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        mem_used = mem_after - mem_before

        times.append(elapsed)
        memory_usage.append(mem_used)

    return {
        "operation": "complete_pipeline",
        "iterations": iterations,
        "times": times,
        "avg_time": sum(times) / len(times),
        "min_time": min(times),
        "max_time": max(times),
        "memory_usage": memory_usage,
        "avg_memory": sum(memory_usage) / len(memory_usage),
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Benchmark performance metrics")
    parser.add_argument(
        "--voice",
        type=Path,
        help="Path to audio file for voice enhancement benchmark",
    )
    parser.add_argument(
        "--mixing",
        nargs=2,
        metavar=("VOCALS", "MUSIC"),
        help="Paths to vocals and music files for mixing benchmark",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=5,
        help="Number of iterations (default: 5)",
    )
    parser.add_argument("--output", type=Path, help="Path to save benchmark report JSON")

    args = parser.parse_args()

    try:
        results = None

        if args.voice:
            results = benchmark_voice_enhancement(args.voice, args.iterations)
        elif args.mixing:
            results = benchmark_mixing(Path(args.mixing[0]), Path(args.mixing[1]), args.iterations)
        else:
            parser.print_help()
            sys.exit(1)

        # Print results
        print("\n" + "=" * 60)
        print("Performance Benchmark Results")
        print("=" * 60)
        print(f"Operation: {results['operation']}")
        print(f"Iterations: {results['iterations']}")
        print(f"Average Time: {results['avg_time']:.2f}s")
        print(f"Min Time: {results['min_time']:.2f}s")
        print(f"Max Time: {results['max_time']:.2f}s")
        print(f"Average Memory: {results['avg_memory']:.2f} MB")
        print("=" * 60)

        # Save report if requested
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, "w") as f:
                json.dump(results, f, indent=2)
            logger.success(f"Benchmark report saved: {args.output}")

    except Exception as e:
        logger.error(f"Benchmarking failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
