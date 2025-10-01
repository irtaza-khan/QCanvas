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
