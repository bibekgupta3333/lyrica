#!/usr/bin/env python3
"""
Coverage Report Generation Script.

This script generates comprehensive coverage reports and identifies areas
needing additional test coverage to achieve >80% coverage target.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

from loguru import logger


def run_coverage_analysis() -> Dict:
    """
    Run coverage analysis and generate report.

    Returns:
        Dictionary with coverage statistics
    """
    logger.info("Running coverage analysis...")

    # Run pytest with coverage
    result = subprocess.run(
        ["pytest", "--cov=app", "--cov-report=json", "--cov-report=term"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        logger.warning("Some tests failed, but continuing with coverage analysis")

    # Parse coverage JSON
    coverage_file = Path("coverage.json")
    if not coverage_file.exists():
        logger.error("Coverage JSON file not found")
        return {}

    with open(coverage_file) as f:
        coverage_data = json.load(f)

    return coverage_data


def analyze_coverage(coverage_data: Dict) -> Dict:
    """
    Analyze coverage data and identify areas needing improvement.

    Args:
        coverage_data: Coverage data from coverage.json

    Returns:
        Dictionary with analysis results
    """
    logger.info("Analyzing coverage data...")

    files = coverage_data.get("files", {})
    total_statements = 0
    total_covered = 0
    low_coverage_files = []

    for file_path, file_data in files.items():
        statements = file_data.get("summary", {}).get("num_statements", 0)
        covered = file_data.get("summary", {}).get("covered_lines", 0)
        coverage_pct = file_data.get("summary", {}).get("percent_covered", 0)

        total_statements += statements
        total_covered += covered

        # Identify files with low coverage (< 80%)
        if coverage_pct < 80 and statements > 0:
            low_coverage_files.append(
                {
                    "file": file_path,
                    "coverage": coverage_pct,
                    "statements": statements,
                    "covered": covered,
                    "missing": statements - covered,
                }
            )

    overall_coverage = (total_covered / total_statements * 100) if total_statements > 0 else 0

    # Sort by coverage percentage (lowest first)
    low_coverage_files.sort(key=lambda x: x["coverage"])

    return {
        "overall_coverage": overall_coverage,
        "total_statements": total_statements,
        "total_covered": total_covered,
        "total_missing": total_statements - total_covered,
        "target_coverage": 80,
        "meets_target": overall_coverage >= 80,
        "low_coverage_files": low_coverage_files[:20],  # Top 20 lowest
    }


def generate_report(analysis: Dict, output_path: Path) -> None:
    """
    Generate coverage report.

    Args:
        analysis: Coverage analysis results
        output_path: Path to save report
    """
    logger.info(f"Generating coverage report: {output_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "summary": {
            "overall_coverage": analysis["overall_coverage"],
            "target_coverage": analysis["target_coverage"],
            "meets_target": analysis["meets_target"],
            "total_statements": analysis["total_statements"],
            "total_covered": analysis["total_covered"],
            "total_missing": analysis["total_missing"],
        },
        "low_coverage_files": analysis["low_coverage_files"],
        "recommendations": generate_recommendations(analysis),
    }

    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    logger.success(f"Coverage report saved: {output_path}")


def generate_recommendations(analysis: Dict) -> List[str]:
    """
    Generate recommendations for improving coverage.

    Args:
        analysis: Coverage analysis results

    Returns:
        List of recommendations
    """
    recommendations = []

    if not analysis["meets_target"]:
        gap = analysis["target_coverage"] - analysis["overall_coverage"]
        recommendations.append(
            f"Overall coverage is {analysis['overall_coverage']:.1f}%, "
            f"need {gap:.1f}% more to reach target of {analysis['target_coverage']}%"
        )

    if analysis["low_coverage_files"]:
        top_priority = analysis["low_coverage_files"][:5]
        recommendations.append(
            f"Focus on improving coverage for these files: "
            f"{', '.join([f['file'] for f in top_priority])}"
        )

    # Identify critical modules
    critical_modules = [
        f
        for f in analysis["low_coverage_files"]
        if any(
            keyword in f["file"] for keyword in ["api", "services", "agents", "production", "voice"]
        )
    ]

    if critical_modules:
        recommendations.append(
            f"Priority: Improve coverage for critical modules: "
            f"{', '.join([f['file'] for f in critical_modules[:5]])}"
        )

    return recommendations


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate coverage report")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/coverage_report.json"),
        help="Path to save coverage report",
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="Generate HTML coverage report",
    )

    args = parser.parse_args()

    try:
        # Run coverage analysis
        coverage_data = run_coverage_analysis()

        if not coverage_data:
            logger.error("Failed to generate coverage data")
            sys.exit(1)

        # Analyze coverage
        analysis = analyze_coverage(coverage_data)

        # Print summary
        print("\n" + "=" * 60)
        print("Coverage Analysis Summary")
        print("=" * 60)
        print(f"Overall Coverage: {analysis['overall_coverage']:.1f}%")
        print(f"Target Coverage: {analysis['target_coverage']}%")
        print(f"Meets Target: {'✅ YES' if analysis['meets_target'] else '❌ NO'}")
        print(f"Total Statements: {analysis['total_statements']}")
        print(f"Covered: {analysis['total_covered']}")
        print(f"Missing: {analysis['total_missing']}")
        print(f"\nLow Coverage Files (<80%): {len(analysis['low_coverage_files'])}")
        if analysis["low_coverage_files"]:
            print("\nTop 5 Lowest Coverage Files:")
            for i, file_info in enumerate(analysis["low_coverage_files"][:5], 1):
                print(
                    f"  {i}. {file_info['file']}: "
                    f"{file_info['coverage']:.1f}% "
                    f"({file_info['covered']}/{file_info['statements']} lines)"
                )
        print("=" * 60)

        # Generate report
        generate_report(analysis, args.output)

        # Generate HTML report if requested
        if args.html:
            logger.info("Generating HTML coverage report...")
            subprocess.run(["pytest", "--cov=app", "--cov-report=html"])

    except Exception as e:
        logger.error(f"Coverage analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
