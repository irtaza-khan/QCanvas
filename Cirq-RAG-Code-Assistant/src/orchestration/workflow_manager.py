"""
Workflow Manager Module

This module implements workflow management for multi-step processes.
Supports defining and executing custom agent workflows with state management.

Author: Umer Farooq, Hussain Waseem Syed, Muhammad Irtaza Khan
Email: umerfarooqcs0891@gmail.com
"""

from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from ..cirq_rag_code_assistant.config import get_config
from ..cirq_rag_code_assistant.config.logging import get_logger

logger = get_logger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class WorkflowStep:
    """Represents a single step in a workflow."""
    
    def __init__(
        self,
        name: str,
        function: Callable,
        required: bool = True,
        timeout: Optional[int] = None,
    ):
        """
        Initialize a workflow step.
        
        Args:
            name: Step name for logging and tracking
            function: Function to execute (takes state dict, returns dict)
            required: If True, workflow fails if this step fails
            timeout: Step-specific timeout (overrides workflow default)
        """
        self.name = name
        self.function = function
        self.required = required
        self.timeout = timeout
        self.status = WorkflowStatus.PENDING
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None


class WorkflowManager:
    """
    Manages multi-step workflows with state management.
    
    Supports:
    - Sequential workflow execution
    - State passing between steps
    - Timeout handling
    - Retry logic
    - Error recovery
    """
    
    def __init__(self):
        """Initialize the WorkflowManager."""
        self.workflows: Dict[str, Dict[str, Any]] = {}
        
        # Load configuration
        config = get_config()
        general_config = config.get("agents", {}).get("general", {})
        
        self.default_timeout = general_config.get("timeout_seconds", 300)
        self.max_retries = general_config.get("max_retries", 3)
        self.parallel_execution = general_config.get("parallel_execution", True)
        
        logger.info(f"Initialized WorkflowManager (timeout={self.default_timeout}s, retries={self.max_retries})")
    
    def define_workflow(
        self,
        name: str,
        steps: List[Dict[str, Any]],
        description: Optional[str] = None,
    ) -> None:
        """
        Define a workflow.
        
        Args:
            name: Workflow name (unique identifier)
            steps: List of step definitions with keys:
                   - name: str
                   - function: Callable
                   - required: bool (optional, default True)
                   - timeout: int (optional)
            description: Optional workflow description
        """
        workflow_steps = []
        for step_def in steps:
            step = WorkflowStep(
                name=step_def.get("name", f"step_{len(workflow_steps)}"),
                function=step_def["function"],
                required=step_def.get("required", True),
                timeout=step_def.get("timeout"),
            )
            workflow_steps.append(step)
        
        self.workflows[name] = {
            "steps": workflow_steps,
            "description": description or f"Workflow '{name}'",
            "status": WorkflowStatus.PENDING,
            "state": {},
            "current_step": 0,
        }
        logger.info(f"Defined workflow: '{name}' with {len(workflow_steps)} steps")
    
    def execute_workflow(
        self,
        name: str,
        initial_state: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a workflow.
        
        Args:
            name: Workflow name
            initial_state: Initial workflow state (passed to first step)
            
        Returns:
            Execution result with:
                - success: bool
                - workflow: str
                - steps_completed: int
                - steps_total: int
                - state: dict (final state)
                - step_results: list
                - errors: list
        """
        if name not in self.workflows:
            raise ValueError(f"Workflow '{name}' not found. Available: {list(self.workflows.keys())}")
        
        workflow = self.workflows[name]
        workflow["status"] = WorkflowStatus.RUNNING
        workflow["state"] = initial_state.copy() if initial_state else {}
        workflow["current_step"] = 0
        
        result = {
            "success": False,
            "workflow": name,
            "description": workflow["description"],
            "steps_completed": 0,
            "steps_total": len(workflow["steps"]),
            "state": workflow["state"],
            "step_results": [],
            "errors": [],
        }
        
        logger.info(f"▶️ Starting workflow: '{name}' ({result['steps_total']} steps)")
        
        try:
            for i, step in enumerate(workflow["steps"]):
                workflow["current_step"] = i
                step_name = step.name
                
                logger.info(f"  [{i+1}/{result['steps_total']}] Executing step: {step_name}")
                step.status = WorkflowStatus.RUNNING
                
                try:
                    # Execute step with retry logic
                    step_result = self._execute_step_with_retry(step, workflow["state"])
                    
                    step.status = WorkflowStatus.COMPLETED
                    step.result = step_result
                    
                    # Update workflow state with step results
                    if step_result:
                        workflow["state"].update(step_result)
                    
                    result["steps_completed"] += 1
                    result["step_results"].append({
                        "step": step_name,
                        "success": True,
                        "result": step_result,
                    })
                    
                    logger.info(f"  ✅ Step '{step_name}' completed")
                    
                except Exception as e:
                    step.status = WorkflowStatus.FAILED
                    step.error = str(e)
                    
                    error_msg = f"Step '{step_name}' failed: {str(e)}"
                    result["errors"].append(error_msg)
                    result["step_results"].append({
                        "step": step_name,
                        "success": False,
                        "error": str(e),
                    })
                    
                    logger.error(f"  ❌ {error_msg}")
                    
                    if step.required:
                        workflow["status"] = WorkflowStatus.FAILED
                        logger.error(f"Workflow failed: required step '{step_name}' failed")
                        return result
                    else:
                        logger.warning(f"  Continuing workflow (step was optional)")
            
            workflow["status"] = WorkflowStatus.COMPLETED
            result["success"] = True
            result["state"] = workflow["state"]
            logger.info(f"✅ Workflow '{name}' completed successfully!")
            
        except Exception as e:
            workflow["status"] = WorkflowStatus.FAILED
            result["errors"].append(str(e))
            logger.error(f"Workflow '{name}' failed: {e}")
        
        return result
    
    def _execute_step_with_retry(
        self,
        step: WorkflowStep,
        state: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a step with retry logic.
        
        Args:
            step: WorkflowStep to execute
            state: Current workflow state
            
        Returns:
            Step result dictionary
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return step.function(state)
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    logger.warning(f"  Step '{step.name}' attempt {attempt + 1}/{self.max_retries} failed: {e}")
                    logger.info(f"  Retrying step '{step.name}'...")
        
        raise last_error
    
    def get_workflow_status(self, name: str) -> Dict[str, Any]:
        """
        Get the status of a workflow.
        
        Args:
            name: Workflow name
            
        Returns:
            Workflow status dictionary
        """
        if name not in self.workflows:
            raise ValueError(f"Workflow '{name}' not found")
        
        workflow = self.workflows[name]
        return {
            "name": name,
            "description": workflow["description"],
            "status": workflow["status"].value,
            "current_step": workflow["current_step"],
            "total_steps": len(workflow["steps"]),
            "steps": [
                {
                    "name": step.name,
                    "status": step.status.value,
                    "required": step.required,
                }
                for step in workflow["steps"]
            ],
        }
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """
        List all defined workflows.
        
        Returns:
            List of workflow summaries
        """
        return [
            {
                "name": name,
                "description": wf["description"],
                "status": wf["status"].value,
                "steps": len(wf["steps"]),
            }
            for name, wf in self.workflows.items()
        ]
    
    def reset_workflow(self, name: str) -> None:
        """
        Reset a workflow to its initial state.
        
        Args:
            name: Workflow name
        """
        if name not in self.workflows:
            raise ValueError(f"Workflow '{name}' not found")
        
        workflow = self.workflows[name]
        workflow["status"] = WorkflowStatus.PENDING
        workflow["state"] = {}
        workflow["current_step"] = 0
        
        for step in workflow["steps"]:
            step.status = WorkflowStatus.PENDING
            step.result = None
            step.error = None
        
        logger.info(f"Workflow '{name}' reset to initial state")
