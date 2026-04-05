"""
Metrics Collector Module

This module implements metrics collection for code generation quality.
"""

from typing import Dict, Any, List, Optional
from collections import defaultdict
from ..cirq_rag_code_assistant.config.logging import get_logger

logger = get_logger(__name__)


class MetricsCollector:
    """Collects and aggregates evaluation metrics."""
    
    def __init__(self):
        """Initialize the MetricsCollector."""
        self.metrics: Dict[str, List[Any]] = defaultdict(list)
        logger.info("Initialized MetricsCollector")
    
    def collect_code_quality(
        self,
        code: str,
        validation_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Collect code quality metrics.
        
        Args:
            code: Generated code
            validation_result: Validation result
            
        Returns:
            Quality metrics dictionary
        """
        metrics = {
            "code_length": len(code),
            "num_lines": len(code.split('\n')),
            "syntax_valid": validation_result.get("validation_passed", False),
            "compilation_success": validation_result.get("compilation", {}).get("success", False),
        }
        
        self.metrics["code_quality"].append(metrics)
        return metrics
    
    def collect_agent_performance(
        self,
        agent_name: str,
        stats: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Collect agent performance metrics.
        
        Args:
            agent_name: Agent name
            stats: Agent statistics
            
        Returns:
            Performance metrics dictionary
        """
        metrics = {
            "agent": agent_name,
            "total_requests": stats.get("total_requests", 0),
            "successful_requests": stats.get("successful_requests", 0),
            "failed_requests": stats.get("failed_requests", 0),
            "success_rate": (
                stats.get("successful_requests", 0) / stats.get("total_requests", 1)
                if stats.get("total_requests", 0) > 0 else 0
            ),
        }
        
        self.metrics["agent_performance"].append(metrics)
        return metrics
    
    def get_aggregated_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics across all collections."""
        aggregated = {}
        
        # Aggregate code quality
        if self.metrics["code_quality"]:
            quality_metrics = self.metrics["code_quality"]
            aggregated["code_quality"] = {
                "total_samples": len(quality_metrics),
                "avg_code_length": sum(m["code_length"] for m in quality_metrics) / len(quality_metrics),
                "syntax_valid_rate": sum(m["syntax_valid"] for m in quality_metrics) / len(quality_metrics),
                "compilation_success_rate": sum(m["compilation_success"] for m in quality_metrics) / len(quality_metrics),
            }
        
        # Aggregate agent performance
        if self.metrics["agent_performance"]:
            perf_metrics = self.metrics["agent_performance"]
            aggregated["agent_performance"] = {
                "total_agents": len(perf_metrics),
                "avg_success_rate": sum(m["success_rate"] for m in perf_metrics) / len(perf_metrics),
            }
        
        return aggregated
    
    def reset(self) -> None:
        """Reset all collected metrics."""
        self.metrics.clear()
