"""
Orchestration Module

This module implements the orchestration layer that coordinates
the multi-agent system and manages workflows.

Author: Umer Farooq, Hussain Waseem Syed, Muhammad Irtaza Khan
Email: umerfarooqcs0891@gmail.com
"""

# This file will export orchestration components
from .orchestrator import Orchestrator
from .workflow_manager import WorkflowManager

__all__ = [
    "Orchestrator",
    "WorkflowManager",
]

