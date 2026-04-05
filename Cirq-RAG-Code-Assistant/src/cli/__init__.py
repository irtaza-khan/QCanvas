"""
CLI (Command-Line Interface) Module

This module implements the command-line interface for interacting
with the Cirq-RAG-Code-Assistant system.

Author: Umer Farooq, Hussain Waseem Syed, Muhammad Irtaza Khan
Email: umerfarooqcs0891@gmail.com
"""

# This file will export CLI components
from .main import main, cli
from .commands import *

__all__ = [
    "main",
    "cli",
]

