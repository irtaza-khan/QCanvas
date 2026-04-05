"""
Benchmark Suite Module

This module implements the benchmark suite for evaluating the system.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from ..orchestration.orchestrator import Orchestrator
from .metrics import MetricsCollector
from ..cirq_rag_code_assistant.config.logging import get_logger

logger = get_logger(__name__)


class BenchmarkSuite:
    """Executes benchmarks on the system."""
    
    # Standard benchmark test cases
    STANDARD_BENCHMARKS = [
        {"query": "Create a 2-qubit Bell state circuit", "algorithm": "teleportation"},
        {"query": "Implement a 3-qubit Grover search algorithm", "algorithm": "grover"},
        {"query": "Create a simple VQE circuit for 2 qubits", "algorithm": "vqe"},
        {"query": "Implement a 2-qubit QAOA circuit", "algorithm": "qaoa"},
    ]
    
    def __init__(
        self,
        orchestrator: Orchestrator,
        metrics_collector: Optional[MetricsCollector] = None,
    ):
        """
        Initialize the BenchmarkSuite.
        
        Args:
            orchestrator: Orchestrator instance
            metrics_collector: Optional MetricsCollector instance
        """
        self.orchestrator = orchestrator
        self.metrics_collector = metrics_collector or MetricsCollector()
        logger.info("Initialized BenchmarkSuite")
    
    def run_benchmarks(
        self,
        test_cases: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Run benchmark test cases.
        
        Args:
            test_cases: Optional list of test cases (uses STANDARD_BENCHMARKS if None)
            
        Returns:
            Benchmark results dictionary
        """
        test_cases = test_cases or self.STANDARD_BENCHMARKS
        
        results = {
            "total_tests": len(test_cases),
            "passed": 0,
            "failed": 0,
            "test_results": [],
        }
        
        logger.info(f"Running {len(test_cases)} benchmark tests...")
        
        for i, test_case in enumerate(test_cases, 1):
            query = test_case.get("query", "")
            algorithm = test_case.get("algorithm")
            
            logger.info(f"Running benchmark {i}/{len(test_cases)}: {query[:50]}...")
            
            result = self.orchestrator.generate_code(
                query=query,
                algorithm=algorithm,
                optimize=True,
                validate=True,
                explain=False,
            )
            
            test_result = {
                "test_id": i,
                "query": query,
                "algorithm": algorithm,
                "success": result.get("success", False),
                "validation_passed": result.get("validation", {}).get("validation_passed", False),
                "errors": result.get("errors", []),
            }
            
            if test_result["success"] and test_result["validation_passed"]:
                results["passed"] += 1
            else:
                results["failed"] += 1
            
            results["test_results"].append(test_result)
            
            # Collect metrics
            if result.get("code"):
                self.metrics_collector.collect_code_quality(
                    result["code"],
                    result.get("validation", {}),
                )
        
        results["pass_rate"] = results["passed"] / results["total_tests"] if results["total_tests"] > 0 else 0
        
        logger.info(f"Benchmark completed: {results['passed']}/{results['total_tests']} passed")
        
        return results
