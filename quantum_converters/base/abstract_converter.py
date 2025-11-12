"""
Abstract Converter Base Class

WHAT THIS FILE DOES:
    Defines the abstract base class (ABC) that all framework-to-OpenQASM 3.0 converters
    must inherit from. This enforces a consistent interface across all converter implementations
    (Qiskit, Cirq, PennyLane) using the Strategy design pattern.

HOW IT LINKS TO OTHER FILES:
    - Used by: All converter classes in quantum_converters/converters/ (qiskit_to_qasm.py,
               cirq_to_qasm.py, pennylane_to_qasm.py)
    - Imports: ConversionResult from .ConversionResult (defines return type)
    - Part of: Base module providing core abstractions for the converter system

INPUT:
    - source (Any): Framework-specific input (typically string source code or circuit object)
    - Used in: convert() method (abstract, must be implemented by subclasses)

OUTPUT:
    - ConversionResult: Contains OpenQASM 3.0 code string and conversion statistics
    - Returned by: convert() method (abstract)

STAGE OF USE:
    - Design Stage: Defines the contract for all converters
    - Runtime Stage: Base class instantiated by concrete converter implementations
    - Used throughout: The entire conversion pipeline relies on this interface

TOOLS USED:
    - abc.ABC: Python's Abstract Base Class mechanism
    - abc.abstractmethod: Decorator to enforce method implementation
    - typing.Any: Type hinting for flexible input types
    - dataclasses: ConversionResult uses dataclass (imported from ConversionResult)

ARCHITECTURE ROLE:
    Implements the Strategy Pattern from systemPatterns.md, allowing polymorphic
    converter usage while maintaining a consistent interface across frameworks.

Author: QCanvas Team
Date: 2025-08-01
Version: 1.0.0
"""

from abc import ABC, abstractmethod
from typing import Any

from .ConversionResult import ConversionResult


class AbstractConverter(ABC):
	"""Abstract base class for framework-to-OpenQASM converters."""

	@abstractmethod
	def convert(self, source: Any) -> ConversionResult:
		"""Convert source input into an OpenQASM 3.0 program and stats."""
		raise NotImplementedError

	def validate(self, source: Any) -> bool:
		"""Optional: validate the input before conversion. Default: True."""
		return True

	def get_supported_gates(self) -> list[str]:
		"""Optional: return a list of supported gate names."""
		return []
