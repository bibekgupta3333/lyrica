#!/usr/bin/env python3
"""
Quality Improvement Validation Script.

This script validates quality improvements in voice enhancement and mixing:
- Compares before/after audio quality metrics
- Validates enhancement effectiveness
- Generates quality improvement reports
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

from loguru import logger

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.voice.quality_metrics import get_quality_metrics


def validate_voice_enhancement(
    original_path: Path, enhanced_path: Path, output_report: Optional[Path] = None
) -> Dict:
    """
    Validate voice enhancement quality improvements.

    Args:
        original_path: Path to original audio file
        enhanced_path: Path to enhanced audio file
        output_report: Optional path to save report JSON

    Returns:
        Dictionary with validation results
    """
    logger.info(f"Validating voice enhancement: {original_path} -> {enhanced_path}")

    if not original_path.exists():
        raise FileNotFoundError(f"Original audio not found: {original_path}")
    if not enhanced_path.exists():
        raise FileNotFoundError(f"Enhanced audio not found: {enhanced_path}")

    metrics_service = get_quality_metrics()

    # Calculate metrics for both files
    original_metrics = metrics_service.calculate_all_metrics(audio_path=original_path)
    enhanced_metrics = metrics_service.calculate_all_metrics(audio_path=enhanced_path)

    # Calculate improvements
    improvements = {}
    for key in ["mos", "overall"]:
        if key in original_metrics and key in enhanced_metrics:
            original_val = original_metrics[key]
            enhanced_val = enhanced_metrics[key]
            if original_val > 0:
                improvement_pct = ((enhanced_val - original_val) / original_val) * 100
                improvements[key] = {
                    "original": original_val,
                    "enhanced": enhanced_val,
                    "improvement": enhanced_val - original_val,
                    "improvement_percent": improvement_pct,
                }

    # Determine if improvement is significant (>10%)
    significant_improvement = any(
        abs(imp["improvement_percent"]) > 10 for imp in improvements.values()
    )

    results = {
        "original_metrics": original_metrics,
        "enhanced_metrics": enhanced_metrics,
        "improvements": improvements,
        "significant_improvement": significant_improvement,
        "validation_passed": significant_improvement,
    }

    # Save report if requested
    if output_report:
        output_report.parent.mkdir(parents=True, exist_ok=True)
        with open(output_report, "w") as f:
            json.dump(results, f, indent=2)
        logger.success(f"Report saved: {output_report}")

    return results


def validate_mixing_improvements(
    before_path: Path,
    after_path: Path,
    genre: Optional[str] = None,
    output_report: Optional[Path] = None,
) -> Dict:
    """
    Validate mixing quality improvements.

    Args:
        before_path: Path to audio before mixing enhancement
        after_path: Path to audio after mixing enhancement
        genre: Optional genre for context
        output_report: Optional path to save report JSON

    Returns:
        Dictionary with validation results
    """
    logger.info(f"Validating mixing improvements: {before_path} -> {after_path}")

    if not before_path.exists():
        raise FileNotFoundError(f"Before audio not found: {before_path}")
    if not after_path.exists():
        raise FileNotFoundError(f"After audio not found: {after_path}")

    metrics_service = get_quality_metrics()

    # Calculate metrics for both files
    before_metrics = metrics_service.calculate_all_metrics(audio_path=before_path)
    after_metrics = metrics_service.calculate_all_metrics(audio_path=after_path)

    # Calculate improvements
    improvements = {}
    for key in ["mos", "overall"]:
        if key in before_metrics and key in after_metrics:
            before_val = before_metrics[key]
            after_val = after_metrics[key]
            if before_val > 0:
                improvement_pct = ((after_val - before_val) / before_val) * 100
                improvements[key] = {
                    "before": before_val,
                    "after": after_val,
                    "improvement": after_val - before_val,
                    "improvement_percent": improvement_pct,
                }

    # Determine if improvement is significant (>5% for mixing)
    significant_improvement = any(
        abs(imp["improvement_percent"]) > 5 for imp in improvements.values()
    )

    results = {
        "genre": genre,
        "before_metrics": before_metrics,
        "after_metrics": after_metrics,
        "improvements": improvements,
        "significant_improvement": significant_improvement,
        "validation_passed": significant_improvement,
    }

    # Save report if requested
    if output_report:
        output_report.parent.mkdir(parents=True, exist_ok=True)
        with open(output_report, "w") as f:
            json.dump(results, f, indent=2)
        logger.success(f"Report saved: {output_report}")

    return results


def validate_batch_quality(test_cases: List[Dict], output_report: Optional[Path] = None) -> Dict:
    """
    Validate quality improvements for multiple test cases.

    Args:
        test_cases: List of test case dictionaries with 'original', 'enhanced', 'type'
        output_report: Optional path to save report JSON

    Returns:
        Dictionary with batch validation results
    """
    logger.info(f"Validating batch quality for {len(test_cases)} test cases")

    results = []
    passed = 0
    failed = 0

    for i, test_case in enumerate(test_cases):
        logger.info(f"Processing test case {i + 1}/{len(test_cases)}")
        try:
            if test_case["type"] == "voice":
                result = validate_voice_enhancement(
                    Path(test_case["original"]), Path(test_case["enhanced"])
                )
            elif test_case["type"] == "mixing":
                result = validate_mixing_improvements(
                    Path(test_case["before"]),
                    Path(test_case["after"]),
                    genre=test_case.get("genre"),
                )
            else:
                logger.warning(f"Unknown test type: {test_case['type']}")
                continue

            result["test_case"] = test_case
            results.append(result)

            if result["validation_passed"]:
                passed += 1
            else:
                failed += 1

        except Exception as e:
            logger.error(f"Test case {i + 1} failed: {e}")
            failed += 1
            results.append({"test_case": test_case, "error": str(e)})

    summary = {
        "total": len(test_cases),
        "passed": passed,
        "failed": failed,
        "pass_rate": (passed / len(test_cases) * 100) if test_cases else 0,
        "results": results,
    }

    # Save report if requested
    if output_report:
        output_report.parent.mkdir(parents=True, exist_ok=True)
        with open(output_report, "w") as f:
            json.dump(summary, f, indent=2)
        logger.success(f"Batch report saved: {output_report}")

    return summary


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate quality improvements")
    parser.add_argument(
        "--voice",
        nargs=2,
        metavar=("ORIGINAL", "ENHANCED"),
        help="Validate voice enhancement (original, enhanced)",
    )
    parser.add_argument(
        "--mixing",
        nargs=2,
        metavar=("BEFORE", "AFTER"),
        help="Validate mixing improvements (before, after)",
    )
    parser.add_argument("--genre", help="Genre for mixing validation")
    parser.add_argument("--batch", type=Path, help="Path to JSON file with batch test cases")
    parser.add_argument("--output", type=Path, help="Path to save validation report")

    args = parser.parse_args()

    try:
        if args.voice:
            results = validate_voice_enhancement(
                Path(args.voice[0]), Path(args.voice[1]), args.output
            )
            print("\n" + "=" * 60)
            print("Voice Enhancement Validation Results")
            print("=" * 60)
            print(f"Original MOS: {results['original_metrics'].get('mos', 'N/A')}")
            print(f"Enhanced MOS: {results['enhanced_metrics'].get('mos', 'N/A')}")
            if "mos" in results["improvements"]:
                imp = results["improvements"]["mos"]
                print(f"Improvement: {imp['improvement']:.2f} ({imp['improvement_percent']:.1f}%)")
            print(f"Validation: {'✅ PASSED' if results['validation_passed'] else '❌ FAILED'}")

        elif args.mixing:
            results = validate_mixing_improvements(
                Path(args.mixing[0]), Path(args.mixing[1]), args.genre, args.output
            )
            print("\n" + "=" * 60)
            print("Mixing Enhancement Validation Results")
            print("=" * 60)
            print(f"Before MOS: {results['before_metrics'].get('mos', 'N/A')}")
            print(f"After MOS: {results['after_metrics'].get('mos', 'N/A')}")
            if "mos" in results["improvements"]:
                imp = results["improvements"]["mos"]
                print(f"Improvement: {imp['improvement']:.2f} ({imp['improvement_percent']:.1f}%)")
            print(f"Validation: {'✅ PASSED' if results['validation_passed'] else '❌ FAILED'}")

        elif args.batch:
            with open(args.batch) as f:
                test_cases = json.load(f)
            summary = validate_batch_quality(test_cases, args.output)
            print("\n" + "=" * 60)
            print("Batch Quality Validation Results")
            print("=" * 60)
            print(f"Total: {summary['total']}")
            print(f"Passed: {summary['passed']}")
            print(f"Failed: {summary['failed']}")
            print(f"Pass Rate: {summary['pass_rate']:.1f}%")
            print("=" * 60)

        else:
            parser.print_help()
            sys.exit(1)

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
