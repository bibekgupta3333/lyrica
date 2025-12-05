"""
Voice quality evaluation pipeline and A/B testing framework.

This module provides automated evaluation and A/B testing capabilities
for voice enhancement systems.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from loguru import logger

from app.services.voice.quality_metrics import get_quality_metrics


class EvaluationService:
    """
    Service for automated voice quality evaluation.

    Provides:
    - Automated evaluation pipeline
    - Comparison tools
    - Quality reporting
    """

    def __init__(self):
        """Initialize evaluation service."""
        self.metrics_service = get_quality_metrics()

    def evaluate_audio(
        self,
        audio_path: Path,
        reference_path: Optional[Path] = None,
        output_dir: Optional[Path] = None,
    ) -> dict:
        """
        Evaluate audio quality and generate report.

        Args:
            audio_path: Path to audio to evaluate
            reference_path: Optional reference audio for comparison
            output_dir: Optional directory to save report

        Returns:
            Dictionary with evaluation results:
            {
                "audio_path": "...",
                "metrics": {...},
                "timestamp": "...",
                "recommendations": [...]
            }
        """
        logger.info(f"Evaluating audio: {audio_path}")

        results = {
            "audio_path": str(audio_path),
            "timestamp": datetime.now().isoformat(),
            "metrics": {},
            "recommendations": [],
        }

        # Calculate metrics
        if reference_path:
            results["metrics"] = self.metrics_service.calculate_all_metrics(
                reference_path=reference_path, degraded_path=audio_path
            )
        else:
            results["metrics"] = self.metrics_service.calculate_all_metrics(audio_path=audio_path)

        # Generate recommendations
        results["recommendations"] = self._generate_recommendations(results["metrics"])

        # Save report if output directory specified
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            report_path = output_dir / f"evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path, "w") as f:
                json.dump(results, f, indent=2)
            results["report_path"] = str(report_path)
            logger.success(f"Evaluation report saved: {report_path}")

        return results

    def compare_audio(
        self,
        audio_a_path: Path,
        audio_b_path: Path,
        reference_path: Optional[Path] = None,
        output_dir: Optional[Path] = None,
    ) -> dict:
        """
        Compare two audio files and generate comparison report.

        Args:
            audio_a_path: Path to first audio
            audio_b_path: Path to second audio
            reference_path: Optional reference audio
            output_dir: Optional directory to save report

        Returns:
            Dictionary with comparison results
        """
        logger.info(f"Comparing audio files: {audio_a_path} vs {audio_b_path}")

        # Evaluate both
        eval_a = self.evaluate_audio(audio_a_path, reference_path)
        eval_b = self.evaluate_audio(audio_b_path, reference_path)

        # Compare metrics
        comparison = {
            "audio_a": {
                "path": str(audio_a_path),
                "metrics": eval_a["metrics"],
            },
            "audio_b": {
                "path": str(audio_b_path),
                "metrics": eval_b["metrics"],
            },
            "comparison": self._compare_metrics(eval_a["metrics"], eval_b["metrics"]),
            "winner": self._determine_winner(eval_a["metrics"], eval_b["metrics"]),
            "timestamp": datetime.now().isoformat(),
        }

        # Save report
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            report_path = output_dir / f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path, "w") as f:
                json.dump(comparison, f, indent=2)
            comparison["report_path"] = str(report_path)
            logger.success(f"Comparison report saved: {report_path}")

        return comparison

    def _compare_metrics(self, metrics_a: dict, metrics_b: dict) -> dict:
        """Compare two sets of metrics."""
        comparison = {}

        for key in set(metrics_a.keys()) | set(metrics_b.keys()):
            val_a = metrics_a.get(key, 0)
            val_b = metrics_b.get(key, 0)

            if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
                diff = val_b - val_a
                percent_change = (diff / val_a * 100) if val_a != 0 else 0
                comparison[key] = {
                    "audio_a": val_a,
                    "audio_b": val_b,
                    "difference": diff,
                    "percent_change": percent_change,
                    "improvement": diff > 0,
                }

        return comparison

    def _determine_winner(self, metrics_a: dict, metrics_b: dict) -> str:
        """Determine which audio has better quality."""
        score_a = metrics_a.get("overall", metrics_a.get("mos", 0))
        score_b = metrics_b.get("overall", metrics_b.get("mos", 0))

        if score_b > score_a * 1.05:  # 5% threshold
            return "audio_b"
        elif score_a > score_b * 1.05:
            return "audio_a"
        else:
            return "tie"

    def _generate_recommendations(self, metrics: dict) -> list[str]:
        """Generate recommendations based on metrics."""
        recommendations = []

        # Check PESQ
        if "pesq" in metrics:
            pesq = metrics["pesq"]
            if pesq < 2.0:
                recommendations.append("Low PESQ score: Consider noise reduction")
            elif pesq < 3.0:
                recommendations.append("Moderate PESQ: Apply audio enhancement")

        # Check STOI
        if "stoi" in metrics:
            stoi = metrics["stoi"]
            if stoi < 0.7:
                recommendations.append("Low intelligibility: Check audio clarity")
            elif stoi < 0.85:
                recommendations.append("Moderate intelligibility: Apply EQ enhancement")

        # Check MOS
        if "mos" in metrics:
            mos = metrics["mos"]
            if mos < 3.0:
                recommendations.append("Low quality: Apply comprehensive enhancement")
            elif mos < 4.0:
                recommendations.append("Good quality: Minor improvements possible")

        return recommendations


class ABTestingService:
    """
    Service for A/B testing voice enhancement methods.

    Provides:
    - A/B test execution
    - Statistical analysis
    - Results reporting
    """

    def __init__(self):
        """Initialize A/B testing service."""
        self.evaluation_service = EvaluationService()

    def run_ab_test(
        self,
        reference_path: Path,
        method_a: str,
        method_b: str,
        audio_a_path: Path,
        audio_b_path: Path,
        output_dir: Optional[Path] = None,
    ) -> dict:
        """
        Run A/B test comparing two enhancement methods.

        Args:
            reference_path: Path to reference audio
            method_a: Name of method A
            method_b: Name of method B
            audio_a_path: Path to audio processed with method A
            audio_b_path: Path to audio processed with method B
            output_dir: Optional directory to save results

        Returns:
            Dictionary with A/B test results:
            {
                "method_a": {...},
                "method_b": {...},
                "statistical_significance": {...},
                "recommendation": "...",
                "timestamp": "..."
            }
        """
        logger.info(f"Running A/B test: {method_a} vs {method_b}")

        # Evaluate both methods
        eval_a = self.evaluation_service.evaluate_audio(audio_a_path, reference_path)
        eval_b = self.evaluation_service.evaluate_audio(audio_b_path, reference_path)

        # Statistical analysis
        stats = self._statistical_analysis(eval_a["metrics"], eval_b["metrics"])

        # Determine recommendation
        recommendation = self._generate_recommendation(
            method_a, method_b, eval_a["metrics"], eval_b["metrics"], stats
        )

        results = {
            "method_a": {
                "name": method_a,
                "audio_path": str(audio_a_path),
                "metrics": eval_a["metrics"],
            },
            "method_b": {
                "name": method_b,
                "audio_path": str(audio_b_path),
                "metrics": eval_b["metrics"],
            },
            "statistical_significance": stats,
            "recommendation": recommendation,
            "timestamp": datetime.now().isoformat(),
        }

        # Save results
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            results_path = output_dir / f"ab_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_path, "w") as f:
                json.dump(results, f, indent=2)
            results["results_path"] = str(results_path)
            logger.success(f"A/B test results saved: {results_path}")

        return results

    def _statistical_analysis(self, metrics_a: dict, metrics_b: dict) -> dict:
        """Perform statistical analysis of metrics."""
        stats = {}

        for key in set(metrics_a.keys()) | set(metrics_b.keys()):
            val_a = metrics_a.get(key)
            val_b = metrics_b.get(key)

            if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
                # Calculate difference
                diff = val_b - val_a
                percent_change = (diff / val_a * 100) if val_a != 0 else 0

                # Simple significance test (can be enhanced)
                # For single samples, we use effect size
                if val_a != 0:
                    effect_size = abs(diff / val_a)
                    significant = effect_size > 0.1  # 10% threshold
                else:
                    effect_size = abs(diff)
                    significant = effect_size > 0.1

                stats[key] = {
                    "difference": float(diff),
                    "percent_change": float(percent_change),
                    "effect_size": float(effect_size),
                    "significant": significant,
                    "improvement": diff > 0,
                }

        return stats

    def _generate_recommendation(
        self,
        method_a: str,
        method_b: str,
        metrics_a: dict,
        metrics_b: dict,
        stats: dict,
    ) -> str:
        """Generate recommendation based on A/B test results."""
        score_a = metrics_a.get("overall", metrics_a.get("mos", 0))
        score_b = metrics_b.get("overall", metrics_b.get("mos", 0))

        # Count significant improvements
        significant_improvements = sum(
            1 for s in stats.values() if s.get("significant") and s.get("improvement")
        )
        significant_degradations = sum(
            1 for s in stats.values() if s.get("significant") and not s.get("improvement")
        )

        if score_b > score_a * 1.1 and significant_improvements > significant_degradations:
            return f"Recommend {method_b}: Significantly better quality ({significant_improvements} improvements)"
        elif score_a > score_b * 1.1 and significant_degradations > significant_improvements:
            return f"Recommend {method_a}: Significantly better quality"
        elif abs(score_b - score_a) < score_a * 0.05:
            return "Methods are equivalent: Both produce similar quality"
        else:
            return (
                f"Recommend {method_b if score_b > score_a else method_a}: Slight quality advantage"
            )


# Singleton instances
_evaluation_service: Optional[EvaluationService] = None
_ab_testing_service: Optional[ABTestingService] = None


def get_evaluation() -> EvaluationService:
    """Get or create evaluation service instance."""
    global _evaluation_service
    if _evaluation_service is None:
        _evaluation_service = EvaluationService()
    return _evaluation_service


def get_ab_testing() -> ABTestingService:
    """Get or create A/B testing service instance."""
    global _ab_testing_service
    if _ab_testing_service is None:
        _ab_testing_service = ABTestingService()
    return _ab_testing_service
