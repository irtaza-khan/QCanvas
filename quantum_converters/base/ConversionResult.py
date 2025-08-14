"""
Conversion Result Classes

This module defines the data structures for representing conversion results
from quantum circuit conversions between different frameworks. It includes
statistics, metadata, and detailed information about the conversion process.

Author: QCanvas Team
Date: 2024
Version: 1.0.0
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ConversionStats:
    """
    Statistics about a quantum circuit conversion.
    
    This class contains detailed statistics about the conversion process,
    including circuit properties, gate counts, and performance metrics.
    """
    
    # Circuit properties
    n_qubits: int = field(default=0, description="Number of qubits in the circuit")
    depth: Optional[int] = field(default=None, description="Circuit depth (number of layers)")
    n_moments: Optional[int] = field(default=None, description="Number of moments in the circuit")
    
    # Gate statistics
    gate_counts: Optional[Dict[str, int]] = field(default=None, description="Count of each gate type")
    total_gates: int = field(default=0, description="Total number of gates")
    
    # Circuit features
    has_measurements: bool = field(default=False, description="Whether circuit contains measurements")
    has_parameters: bool = field(default=False, description="Whether circuit contains parameters")
    has_conditional_operations: bool = field(default=False, description="Whether circuit has conditional operations")
    
    # Conversion metrics
    conversion_time: Optional[float] = field(default=None, description="Conversion time in seconds")
    optimization_time: Optional[float] = field(default=None, description="Optimization time in seconds")
    validation_time: Optional[float] = field(default=None, description="Validation time in seconds")
    
    # Framework-specific information
    source_framework: Optional[str] = field(default=None, description="Source framework name")
    target_framework: Optional[str] = field(default=None, description="Target framework name")
    framework_version: Optional[str] = field(default=None, description="Framework version used")
    
    # Quality metrics
    fidelity_estimate: Optional[float] = field(default=None, description="Estimated conversion fidelity")
    complexity_score: Optional[float] = field(default=None, description="Circuit complexity score")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert stats to dictionary representation.
        
        Returns:
            Dict containing all statistics
        """
        return {
            "n_qubits": self.n_qubits,
            "depth": self.depth,
            "n_moments": self.n_moments,
            "gate_counts": self.gate_counts,
            "total_gates": self.total_gates,
            "has_measurements": self.has_measurements,
            "has_parameters": self.has_parameters,
            "has_conditional_operations": self.has_conditional_operations,
            "conversion_time": self.conversion_time,
            "optimization_time": self.optimization_time,
            "validation_time": self.validation_time,
            "source_framework": self.source_framework,
            "target_framework": self.target_framework,
            "framework_version": self.framework_version,
            "fidelity_estimate": self.fidelity_estimate,
            "complexity_score": self.complexity_score
        }
    
    def print_stats(self) -> None:
        """Print circuit statistics in a formatted way."""
        print(f"\n{'='*50}")
        print("Circuit Conversion Statistics")
        print(f"{'='*50}")
        
        print(f"Qubits: {self.n_qubits}")
        if self.depth is not None:
            print(f"Depth: {self.depth}")
        if self.n_moments is not None:
            print(f"Moments: {self.n_moments}")
        
        print(f"Total Gates: {self.total_gates}")
        
        if self.gate_counts:
            print("\nGate Distribution:")
            for gate, count in sorted(self.gate_counts.items()):
                print(f"  {gate}: {count}")
        
        print(f"\nFeatures:")
        print(f"  Measurements: {'Yes' if self.has_measurements else 'No'}")
        print(f"  Parameters: {'Yes' if self.has_parameters else 'No'}")
        print(f"  Conditional Operations: {'Yes' if self.has_conditional_operations else 'No'}")
        
        if self.conversion_time is not None:
            print(f"\nPerformance:")
            print(f"  Conversion Time: {self.conversion_time:.3f}s")
            if self.optimization_time is not None:
                print(f"  Optimization Time: {self.optimization_time:.3f}s")
            if self.validation_time is not None:
                print(f"  Validation Time: {self.validation_time:.3f}s")
        
        if self.fidelity_estimate is not None:
            print(f"  Estimated Fidelity: {self.fidelity_estimate:.3f}")
        
        if self.complexity_score is not None:
            print(f"  Complexity Score: {self.complexity_score:.3f}")
        
        print(f"{'='*50}")


@dataclass
class ConversionResult:
    """
    Result of a quantum circuit conversion operation.
    
    This class represents the complete result of converting a quantum circuit
    from one framework to another, including the converted code, intermediate
    representation, statistics, and metadata.
    """
    
    # Core conversion results
    qasm_code: str = field(..., description="OpenQASM 3.0 intermediate representation")
    converted_code: Optional[str] = field(default=None, description="Code in target framework")
    
    # Statistics and metadata
    stats: ConversionStats = field(default_factory=ConversionStats, description="Conversion statistics")
    
    # Status and error information
    success: bool = field(default=True, description="Whether conversion was successful")
    warnings: List[str] = field(default_factory=list, description="Conversion warnings")
    errors: List[str] = field(default_factory=list, description="Conversion errors")
    
    # Timing information
    start_time: Optional[datetime] = field(default=None, description="Conversion start time")
    end_time: Optional[datetime] = field(default=None, description="Conversion end time")
    execution_time: Optional[float] = field(default=None, description="Total execution time in seconds")
    
    # Framework information
    source_framework: Optional[str] = field(default=None, description="Source framework")
    target_framework: Optional[str] = field(default=None, description="Target framework")
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict, description="Additional metadata")
    
    def __post_init__(self):
        """Post-initialization processing."""
        # Calculate execution time if start and end times are provided
        if self.start_time and self.end_time:
            self.execution_time = (self.end_time - self.start_time).total_seconds()
        
        # Set execution time in stats if available
        if self.execution_time is not None:
            self.stats.conversion_time = self.execution_time
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary representation.
        
        Returns:
            Dict containing all result data
        """
        return {
            "success": self.success,
            "qasm_code": self.qasm_code,
            "converted_code": self.converted_code,
            "stats": self.stats.to_dict(),
            "warnings": self.warnings,
            "errors": self.errors,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "execution_time": self.execution_time,
            "source_framework": self.source_framework,
            "target_framework": self.target_framework,
            "metadata": self.metadata
        }
    
    def is_successful(self) -> bool:
        """
        Check if conversion was successful.
        
        Returns:
            bool: True if conversion was successful
        """
        return self.success and len(self.errors) == 0
    
    def has_warnings(self) -> bool:
        """
        Check if conversion has warnings.
        
        Returns:
            bool: True if conversion has warnings
        """
        return len(self.warnings) > 0
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the conversion result.
        
        Returns:
            Dict containing summary information
        """
        return {
            "success": self.success,
            "source_framework": self.source_framework,
            "target_framework": self.target_framework,
            "n_qubits": self.stats.n_qubits,
            "total_gates": self.stats.total_gates,
            "execution_time": self.execution_time,
            "warnings_count": len(self.warnings),
            "errors_count": len(self.errors)
        }
    
    def print_summary(self) -> None:
        """Print a summary of the conversion result."""
        print(f"\n{'='*60}")
        print("Conversion Summary")
        print(f"{'='*60}")
        
        print(f"Status: {'✓ Success' if self.is_successful() else '✗ Failed'}")
        print(f"Source Framework: {self.source_framework or 'Unknown'}")
        print(f"Target Framework: {self.target_framework or 'Unknown'}")
        
        if self.execution_time is not None:
            print(f"Execution Time: {self.execution_time:.3f}s")
        
        print(f"Qubits: {self.stats.n_qubits}")
        print(f"Total Gates: {self.stats.total_gates}")
        
        if self.warnings:
            print(f"\nWarnings ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        
        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        print(f"{'='*60}")
    
    def add_warning(self, warning: str) -> None:
        """
        Add a warning to the result.
        
        Args:
            warning: Warning message to add
        """
        self.warnings.append(warning)
    
    def add_error(self, error: str) -> None:
        """
        Add an error to the result.
        
        Args:
            error: Error message to add
        """
        self.errors.append(error)
        self.success = False
    
    def set_frameworks(self, source: str, target: str) -> None:
        """
        Set source and target framework information.
        
        Args:
            source: Source framework name
            target: Target framework name
        """
        self.source_framework = source
        self.target_framework = target
        self.stats.source_framework = source
        self.stats.target_framework = target
    
    def set_timing(self, start_time: datetime, end_time: datetime) -> None:
        """
        Set timing information for the conversion.
        
        Args:
            start_time: Conversion start time
            end_time: Conversion end time
        """
        self.start_time = start_time
        self.end_time = end_time
        self.execution_time = (end_time - start_time).total_seconds()
        self.stats.conversion_time = self.execution_time


@dataclass
class ValidationResult:
    """
    Result of circuit validation.
    
    This class represents the result of validating a quantum circuit,
    including validation status, errors, and warnings.
    """
    
    valid: bool = field(..., description="Whether circuit is valid")
    errors: List[str] = field(default_factory=list, description="Validation errors")
    warnings: List[str] = field(default_factory=list, description="Validation warnings")
    stats: Optional[ConversionStats] = field(default=None, description="Circuit statistics")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert validation result to dictionary.
        
        Returns:
            Dict containing validation result
        """
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "stats": self.stats.to_dict() if self.stats else None
        }


@dataclass
class OptimizationResult:
    """
    Result of circuit optimization.
    
    This class represents the result of optimizing a quantum circuit,
    including the optimized circuit and optimization metrics.
    """
    
    original_circuit: str = field(..., description="Original circuit code")
    optimized_circuit: str = field(..., description="Optimized circuit code")
    optimization_level: int = field(..., description="Optimization level used")
    metrics: Dict[str, Any] = field(default_factory=dict, description="Optimization metrics")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert optimization result to dictionary.
        
        Returns:
            Dict containing optimization result
        """
        return {
            "original_circuit": self.original_circuit,
            "optimized_circuit": self.optimized_circuit,
            "optimization_level": self.optimization_level,
            "metrics": self.metrics
        }