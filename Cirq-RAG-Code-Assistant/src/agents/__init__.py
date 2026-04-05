"""
Multi-Agent System Module

This module implements the multi-agent architecture for the
Cirq-RAG-Code-Assistant. It includes specialized agents for
code generation, optimization, validation, and education.

Author: Umer Farooq, Hussain Waseem Syed, Muhammad Irtaza Khan
Email: umerfarooqcs0891@gmail.com
"""

from .base_agent import BaseAgent
from .designer import DesignerAgent
from .optimizer import OptimizerAgent
from .validator import ValidatorAgent
from .educational import EducationalAgent

__all__ = [
    "BaseAgent",
    "DesignerAgent",
    "OptimizerAgent",
    "ValidatorAgent",
    "EducationalAgent",
]
