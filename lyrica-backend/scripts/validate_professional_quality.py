#!/usr/bin/env python3
"""
PHASE 4: Professional Quality Validation Script.

This script validates that professional quality targets (90%) are met by:
- Comparing before/after quality metrics
- Testing across multiple genres
- Generating comprehensive quality reports
- Validating all professional processing features
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

from app.core.music_config import MusicGenre
from app.services.voice import get_quality_metrics


def validate_genre_quality(
    genre: MusicGenre,
    before_path: Optional[Path] = None,
    after_path: Optional[Path] = None,
    reference_path: Optional[Path] = None,
) -> Dict:
    """
    Validate quality improvements for a specific genre.

    Args:
        genre: Music genre to test
        before_path: Path to audio before professional processing
        after_path: Path to audio after professional processing
        reference_path: Optional reference audio for comparison

    Returns:
        Dictionary with validation results
    """
    logger.info(f"Validating quality for genre: {genre.value}")

    metrics_service = get_quality_metrics()

    results = {
        "genre": genre.value,
        "timestamp": datetime.now().isoformat(),
        "before_metrics": {},
        "after_metrics": {},
        "improvement": {},
        "target_met": False,
    }

    # Calculate metrics for before (if provided)
    if before_path and before_path.exists():
        results["before_metrics"] = metrics_service.calculate_all_metrics(audio_path=before_path)

    # Calculate metrics for after (if provided)
    if after_path and after_path.exists():
        if reference_path and reference_path.exists():
            results["after_metrics"] = metrics_service.calculate_all_metrics(
                reference_path=reference_path, degraded_path=after_path
            )
        else:
            results["after_metrics"] = metrics_service.calculate_all_metrics(audio_path=after_path)

    # Calculate improvement
    if results["before_metrics"] and results["after_metrics"]:
        for metric in ["mos", "overall"]:
            if metric in results["before_metrics"] and metric in results["after_metrics"]:
                before_val = results["before_metrics"][metric]
                after_val = results["after_metrics"][metric]
                improvement = ((after_val - before_val) / before_val) * 100 if before_val > 0 else 0
                results["improvement"][metric] = {
                    "before": before_val,
                    "after": after_val,
                    "improvement_percent": improvement,
                }

    # Check if target met (90% professional = MOS >= 4.0, overall >= 4.0)
    if "overall" in results["after_metrics"]:
        overall_score = results["after_metrics"]["overall"]
        results["target_met"] = overall_score >= 4.0  # 90% = 4.0/5.0
        results["target_score"] = 4.0
        results["actual_score"] = overall_score

    return results


def validate_across_genres(
    test_dir: Path,
    genres: Optional[List[MusicGenre]] = None,
    output_report: Optional[Path] = None,
) -> Dict:
    """
    Validate quality across multiple genres.

    Args:
        test_dir: Directory containing test audio files
        genres: List of genres to test (default: all genres)
        output_report: Optional path to save report JSON

    Returns:
        Dictionary with validation results for all genres
    """
    logger.info(f"Validating quality across genres: {test_dir}")

    if genres is None:
        genres = list(MusicGenre)

    results = {
        "timestamp": datetime.now().isoformat(),
        "test_directory": str(test_dir),
        "genres_tested": [],
        "overall_results": {},
        "genre_results": {},
    }

    # Test each genre
    for genre in genres:
        genre_name = genre.value.lower()

        # Look for test files
        before_path = test_dir / f"{genre_name}_before.wav"
        after_path = test_dir / f"{genre_name}_after.wav"
        reference_path = test_dir / f"{genre_name}_reference.wav"

        # Skip if no files found
        if not after_path.exists():
            logger.warning(f"No test files found for {genre_name}, skipping")
            continue

        # Validate genre
        genre_results = validate_genre_quality(
            genre=genre,
            before_path=before_path if before_path.exists() else None,
            after_path=after_path,
            reference_path=reference_path if reference_path.exists() else None,
        )

        results["genre_results"][genre_name] = genre_results
        results["genres_tested"].append(genre_name)

    # Calculate overall statistics
    if results["genre_results"]:
        target_met_count = sum(
            1 for r in results["genre_results"].values() if r.get("target_met", False)
        )
        total_count = len(results["genre_results"])

        avg_improvement = {}
        if results["genre_results"]:
            for metric in ["mos", "overall"]:
                improvements = [
                    r["improvement"].get(metric, {}).get("improvement_percent", 0)
                    for r in results["genre_results"].values()
                    if "improvement" in r and metric in r["improvement"]
                ]
                if improvements:
                    avg_improvement[metric] = sum(improvements) / len(improvements)

        results["overall_results"] = {
            "genres_tested": total_count,
            "targets_met": target_met_count,
            "target_met_percentage": (
                (target_met_count / total_count * 100) if total_count > 0 else 0
            ),
            "average_improvement": avg_improvement,
        }

    # Save report
    if output_report:
        output_report.parent.mkdir(parents=True, exist_ok=True)
        with open(output_report, "w") as f:
            json.dump(results, f, indent=2)
        logger.success(f"Quality validation report saved: {output_report}")

    return results


def generate_quality_report(results: Dict, output_path: Path) -> None:
    """
    Generate human-readable quality report.

    Args:
        results: Validation results dictionary
        output_path: Path to save report
    """
    logger.info(f"Generating quality report: {output_path}")

    report_lines = [
        "=" * 70,
        "PROFESSIONAL QUALITY VALIDATION REPORT",
        "=" * 70,
        f"\nGenerated: {results.get('timestamp', 'Unknown')}",
        f"Test Directory: {results.get('test_directory', 'Unknown')}",
        "",
    ]

    # Overall results
    if "overall_results" in results:
        overall = results["overall_results"]
        report_lines.extend(
            [
                "OVERALL RESULTS",
                "-" * 70,
                f"Genres Tested: {overall.get('genres_tested', 0)}",
                f"Targets Met: {overall.get('targets_met', 0)}",
                f"Target Met Percentage: {overall.get('target_met_percentage', 0):.1f}%",
                "",
            ]
        )

        if "average_improvement" in overall:
            avg_imp = overall["average_improvement"]
            report_lines.append("Average Improvement:")
            for metric, value in avg_imp.items():
                report_lines.append(f"  {metric.upper()}: {value:.1f}%")
            report_lines.append("")

    # Genre-specific results
    if "genre_results" in results:
        report_lines.extend(["GENRE-SPECIFIC RESULTS", "-" * 70, ""])

        for genre_name, genre_result in results["genre_results"].items():
            report_lines.extend(
                [
                    f"Genre: {genre_name.upper()}",
                    f"  Target Met: {'✅ YES' if genre_result.get('target_met') else '❌ NO'}",
                ]
            )

            if "actual_score" in genre_result:
                report_lines.append(
                    f"  Overall Score: {genre_result['actual_score']:.2f}/5.0 "
                    f"(Target: {genre_result.get('target_score', 4.0)}/5.0)"
                )

            if "improvement" in genre_result:
                report_lines.append("  Improvements:")
                for metric, imp_data in genre_result["improvement"].items():
                    if isinstance(imp_data, dict):
                        report_lines.append(
                            f"    {metric.upper()}: "
                            f"{imp_data.get('before', 0):.2f} → "
                            f"{imp_data.get('after', 0):.2f} "
                            f"({imp_data.get('improvement_percent', 0):+.1f}%)"
                        )

            report_lines.append("")

    report_lines.append("=" * 70)

    # Write report
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(report_lines))

    logger.success(f"Quality report saved: {output_path}")


def main():
    """Main function for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Validate professional quality targets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate quality with test directory
  python validate_professional_quality.py --test-dir audio_files/test_samples

  # Validate specific genres
  python validate_professional_quality.py --test-dir audio_files/test_samples --genres pop rock

  # Generate reports
  python validate_professional_quality.py --test-dir audio_files/test_samples \\
      --output-report quality_report.json \\
      --output-text-report quality_report.txt

Note: Test directory should contain audio files named like:
  - {genre}_before.wav (optional, for comparison)
  - {genre}_after.wav (required)
  - {genre}_reference.wav (optional, for reference comparison)
        """,
    )
    parser.add_argument(
        "--test-dir",
        type=Path,
        default=Path("audio_files/test_samples"),
        help="Directory containing test audio files (default: audio_files/test_samples)",
    )
    parser.add_argument(
        "--genres",
        nargs="+",
        choices=[g.value for g in MusicGenre],
        help="Genres to test (default: all)",
    )
    parser.add_argument(
        "--output-report",
        type=Path,
        help="Path to save JSON report",
    )
    parser.add_argument(
        "--output-text-report",
        type=Path,
        help="Path to save human-readable text report",
    )

    args = parser.parse_args()

    # Check if test directory exists
    if not args.test_dir.exists():
        logger.error(f"Test directory does not exist: {args.test_dir}")
        logger.info(
            "Please create the directory and add test audio files, "
            "or specify a different directory with --test-dir"
        )
        logger.info(
            "\nExpected file naming convention:\n"
            "  - {genre}_before.wav (optional, for comparison)\n"
            "  - {genre}_after.wav (required)\n"
            "  - {genre}_reference.wav (optional, for reference)\n"
            "\nExample: pop_after.wav, rock_after.wav, etc."
        )
        return 1

    # Convert genre strings to enums
    genres = None
    if args.genres:
        genres = [MusicGenre(g.lower()) for g in args.genres]

    # Validate quality
    try:
        results = validate_across_genres(
            test_dir=args.test_dir,
            genres=genres,
            output_report=args.output_report,
        )

        # Generate text report
        if args.output_text_report:
            generate_quality_report(results, args.output_text_report)

        # Print summary
        if "overall_results" in results:
            overall = results["overall_results"]
            print("\n" + "=" * 70)
            print("VALIDATION SUMMARY")
            print("=" * 70)
            print(f"Genres Tested: {overall.get('genres_tested', 0)}")
            print(f"Targets Met: {overall.get('targets_met', 0)}")
            print(f"Target Met Percentage: {overall.get('target_met_percentage', 0):.1f}%")
            print("=" * 70)

        target_met_pct = results.get("overall_results", {}).get("target_met_percentage", 0)
        return 0 if target_met_pct >= 80 else 1

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
