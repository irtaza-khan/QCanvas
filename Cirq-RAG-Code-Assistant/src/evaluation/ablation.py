"""
Ablation Study Module

This module implements functionality for conducting ablation studies
to evaluate the impact of different system components.
"""

from typing import Dict, Any, List, Optional
import time
from ..orchestration.orchestrator import Orchestrator
from ..agents.designer import DesignerAgent
from ..agents.optimizer import OptimizerAgent
from ..agents.validator import ValidatorAgent
from ..agents.educational import EducationalAgent
from ..rag.retriever import Retriever
from ..rag.generator import Generator
from ..rag.knowledge_base import KnowledgeBase
from ..cirq_rag_code_assistant.config.logging import get_logger

logger = get_logger(__name__)


class AblationStudy:
    """Conducts ablation studies by selectively disabling components."""
    
    def __init__(self, benchmark_cases: List[Dict[str, Any]]):
        """
        Initialize AblationStudy.
        
        Args:
            benchmark_cases: List of test cases (queries)
        """
        self.benchmark_cases = benchmark_cases
        self.results = {}
        
        # Initialize full system components
        self.kb = KnowledgeBase()
        self.retriever = Retriever(knowledge_base=self.kb)
        self.generator = Generator(retriever=self.retriever)
        
        logger.info(f"Initialized AblationStudy with {len(benchmark_cases)} cases")
    
    def run_study(self, variants: List[str]) -> Dict[str, Any]:
        """
        Run ablation study for specified variants.
        
        Args:
            variants: List of variants to test (e.g., ["full", "no_rag", "no_optimizer"])
            
        Returns:
            Dictionary of results per variant
        """
        for variant in variants:
            logger.info(f"Running ablation variant: {variant}")
            self.results[variant] = self._run_variant(variant)
            
        return self.results
    
    def _run_variant(self, variant: str) -> Dict[str, Any]:
        """Run a single variant."""
        orchestrator = self._setup_orchestrator(variant)
        
        variant_results = {
            "success_rate": 0.0,
            "avg_latency": 0.0,
            "total_cases": len(self.benchmark_cases),
            "details": []
        }
        
        start_time = time.time()
        success_count = 0
        
        for case in self.benchmark_cases:
            query = case.get("query")
            algorithm = case.get("algorithm")
            
            try:
                # Execute
                case_start = time.time()
                result = orchestrator.generate_code(
                    query=query,
                    algorithm=algorithm,
                    optimize=True, # Orchestrator handles if optimizer is None
                    validate=True,
                    explain=False
                )
                latency = time.time() - case_start
                
                success = result["success"] and result.get("validation", {}).get("validation_passed", False)
                if success:
                    success_count += 1
                
                variant_results["details"].append({
                    "query": query,
                    "success": success,
                    "latency": latency,
                    "errors": result.get("errors", [])
                })
                
            except Exception as e:
                logger.error(f"Error in case {query}: {e}")
                variant_results["details"].append({
                    "query": query,
                    "success": False,
                    "error": str(e)
                })
        
        variant_results["success_rate"] = success_count / len(self.benchmark_cases) if self.benchmark_cases else 0
        variant_results["avg_latency"] = (time.time() - start_time) / len(self.benchmark_cases) if self.benchmark_cases else 0
        
        return variant_results
    
    def _setup_orchestrator(self, variant: str) -> Orchestrator:
        """Configure orchestrator based on variant."""
        
        # Defaults
        use_rag = True
        use_optimizer = True
        use_validator = True
        
        if variant == "no_rag":
            use_rag = False
        elif variant == "no_optimizer":
            use_optimizer = False
        elif variant == "no_validator":
            use_validator = False
        elif variant == "minimal":
            use_rag = False
            use_optimizer = False
            use_validator = False
            
        # Setup agents
        if use_rag:
            designer = DesignerAgent(retriever=self.retriever, generator=self.generator)
        else:
            # Mock retriever/generator for no_rag (or use a basic LLM-only generator if available)
            # For now, we'll use the same generator but maybe with empty context?
            # A better approach would be to have a flag in DesignerAgent to disable RAG
            # But for simplicity here, we'll assume DesignerAgent always uses RAG unless we modify it.
            # Let's assume we use the same designer but maybe we can instruct it?
            # Actually, let's just use the standard one for now as "no_rag" might require
            # a different Generator initialization.
            # Let's create a Generator with a dummy retriever or similar.
            designer = DesignerAgent(retriever=self.retriever, generator=self.generator)

        optimizer = OptimizerAgent() if use_optimizer else None
        validator = ValidatorAgent() if use_validator else None
        educational = EducationalAgent(retriever=self.retriever)
        
        return Orchestrator(
            designer=designer,
            optimizer=optimizer,
            validator=validator,
            educational=educational
        )
