"""
Base Agent Module

This module defines the base agent interface and common functionality
for all specialized agents in the multi-agent system.

Author: Umer Farooq, Hussain Waseem Syed, Muhammad Irtaza Khan
Email: umerfarooqcs0891@gmail.com

Purpose:
    - Define common agent interface and abstract methods
    - Provide shared functionality (logging, error handling)
    - Manage agent state and communication
    - Handle tool integration

Input:
    - Agent requests (messages, tasks)
    - Configuration parameters
    - Shared context

Output:
    - Agent responses (results, status)
    - Logs and metrics
    - Error messages (if any)

Dependencies:
    - RAG System: For context retrieval
    - Tools: For agent capabilities
    - Logging: For agent activity tracking

Links to other modules:
    - Base class for: DesignerAgent, OptimizerAgent, ValidatorAgent, EducationalAgent
    - Used by: Orchestrator, WorkflowManager
    - Uses: RAG system, Tools, Logging
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from ..cirq_rag_code_assistant.config import get_config
from ..cirq_rag_code_assistant.config.logging import get_logger

logger = get_logger(__name__)


class BaseAgent(ABC):
    """
    Base class for all agents in the multi-agent system.
    
    Provides common functionality including error handling, retry logic,
    and tool integration.
    """
    
    def __init__(
        self,
        name: str,
        max_retries: int = 3,
        timeout: Optional[int] = None,
    ):
        """
        Initialize the BaseAgent.
        
        Args:
            name: Agent name
            max_retries: Maximum number of retry attempts
            timeout: Timeout in seconds (None for no timeout)
        """
        self.name = name
        self.max_retries = max_retries
        config = get_config()
        self.timeout = timeout or config.get("agents.general.timeout_seconds", 300)
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "retry_count": 0,
        }
        
        logger.info(f"Initialized {self.name} agent")
    
    @abstractmethod
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an agent task.
        
        Args:
            task: Task dictionary with input parameters
            
        Returns:
            Result dictionary with output and metadata
        """
        pass
    
    def run(
        self,
        task: Dict[str, Any],
        retry: bool = True,
    ) -> Dict[str, Any]:
        """
        Run agent task with retry logic and error handling.
        
        Args:
            task: Task dictionary
            retry: Whether to retry on failure
            
        Returns:
            Result dictionary
        """
        self.stats["total_requests"] += 1
        
        attempt = 0
        last_error = None
        
        while attempt < (self.max_retries if retry else 1):
            try:
                result = self.execute(task)
                
                if result.get("success", False):
                    self.stats["successful_requests"] += 1
                    return result
                else:
                    last_error = result.get("error", "Unknown error")
                    
            except Exception as e:
                last_error = str(e)
                logger.error(f"{self.name} error on attempt {attempt + 1}: {e}")
            
            attempt += 1
            if retry and attempt < self.max_retries:
                self.stats["retry_count"] += 1
                logger.info(f"{self.name} retrying (attempt {attempt + 1}/{self.max_retries})")
        
        # All attempts failed
        self.stats["failed_requests"] += 1
        
        return {
            "success": False,
            "error": f"Failed after {attempt} attempts: {last_error}",
            "agent": self.name,
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return self.stats.copy()
    
    def reset_stats(self) -> None:
        """Reset agent statistics."""
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "retry_count": 0,
        }
