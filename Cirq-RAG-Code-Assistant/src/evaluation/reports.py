"""
Report Generator Module

This module implements report generation for evaluation results.
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from .metrics import MetricsCollector
from .benchmark import BenchmarkSuite
from ..cirq_rag_code_assistant.config.logging import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """Generates evaluation reports."""
    
    def __init__(
        self,
        output_dir: Optional[Path] = None,
    ):
        """
        Initialize the ReportGenerator.
        
        Args:
            output_dir: Output directory for reports
        """
        self.output_dir = Path(output_dir) if output_dir else Path("outputs/reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized ReportGenerator with output dir: {self.output_dir}")
    
    def generate_report(
        self,
        metrics: Optional[MetricsCollector] = None,
        benchmark_results: Optional[Dict[str, Any]] = None,
        format: str = "json",
    ) -> Path:
        """
        Generate an evaluation report.
        
        Args:
            metrics: Optional MetricsCollector instance
            benchmark_results: Optional benchmark results
            format: Report format ("json", "text")
            
        Returns:
            Path to generated report file
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics.get_aggregated_metrics() if metrics else {},
            "benchmark_results": benchmark_results or {},
        }
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evaluation_report_{timestamp}.{format}"
        filepath = self.output_dir / filename
        
        # Write report
        if format == "json":
            with open(filepath, "w") as f:
                json.dump(report, f, indent=2)
        else:
            with open(filepath, "w") as f:
                f.write(self._format_text_report(report))
        
        logger.info(f"Generated report: {filepath}")
        return filepath
    
    def _format_text_report(self, report: Dict[str, Any]) -> str:
        """Format report as text."""
        lines = [
            "=" * 60,
            "Evaluation Report",
            "=" * 60,
            f"Timestamp: {report['timestamp']}",
            "",
        ]
        
        # Metrics section
        if report.get("metrics"):
            lines.extend([
                "Metrics:",
                "-" * 60,
            ])
            metrics = report["metrics"]
            if "code_quality" in metrics:
                qm = metrics["code_quality"]
                lines.extend([
                    f"  Code Quality:",
                    f"    Total Samples: {qm.get('total_samples', 0)}",
                    f"    Avg Code Length: {qm.get('avg_code_length', 0):.0f}",
                    f"    Syntax Valid Rate: {qm.get('syntax_valid_rate', 0):.1%}",
                    f"    Compilation Success Rate: {qm.get('compilation_success_rate', 0):.1%}",
                ])
            lines.append("")
        
        # Benchmark section
        if report.get("benchmark_results"):
            lines.extend([
                "Benchmark Results:",
                "-" * 60,
            ])
            br = report["benchmark_results"]
            lines.extend([
                f"  Total Tests: {br.get('total_tests', 0)}",
                f"  Passed: {br.get('passed', 0)}",
                f"  Failed: {br.get('failed', 0)}",
                f"  Pass Rate: {br.get('pass_rate', 0):.1%}",
            ])
        
        lines.append("=" * 60)
        return "\n".join(lines)
