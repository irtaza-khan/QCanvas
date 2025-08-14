"""
QCanvas Circuit Converter API Routes

This module provides API endpoints for converting quantum circuits between
different frameworks (Cirq, Qiskit, PennyLane) using OpenQASM 3.0 as an
intermediate representation.

Author: QCanvas Team
Date: 2024
Version: 1.0.0
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field, validator

from app.config.settings import get_settings
from app.services.conversion_service import ConversionService
from app.utils.exceptions import QCanvasException

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize conversion service
conversion_service = ConversionService()


class ConversionRequest(BaseModel):
    """Request model for circuit conversion."""
    
    source_framework: str = Field(..., description="Source framework (cirq/qiskit/pennylane)")
    target_framework: str = Field(..., description="Target framework (cirq/qiskit/pennylane)")
    source_code: str = Field(..., description="Source code in the source framework")
    optimization_level: int = Field(default=1, description="Optimization level (0-3)")
    include_comments: bool = Field(default=False, description="Include comments in output")
    validate_circuit: bool = Field(default=True, description="Validate circuit before conversion")
    
    @validator("source_framework", "target_framework")
    def validate_framework(cls, v):
        """Validate framework names."""
        valid_frameworks = ["cirq", "qiskit", "pennylane"]
        if v.lower() not in valid_frameworks:
            raise ValueError(f"Framework must be one of {valid_frameworks}")
        return v.lower()
    
    @validator("optimization_level")
    def validate_optimization_level(cls, v):
        """Validate optimization level."""
        if not 0 <= v <= 3:
            raise ValueError("Optimization level must be between 0 and 3")
        return v


class ConversionResponse(BaseModel):
    """Response model for circuit conversion."""
    
    success: bool = Field(..., description="Conversion success status")
    source_framework: str = Field(..., description="Source framework")
    target_framework: str = Field(..., description="Target framework")
    converted_code: Optional[str] = Field(default=None, description="Converted code")
    qasm_code: Optional[str] = Field(default=None, description="Intermediate OpenQASM 3.0 code")
    stats: Optional[Dict[str, Any]] = Field(default=None, description="Conversion statistics")
    warnings: List[str] = Field(default_factory=list, description="Conversion warnings")
    errors: List[str] = Field(default_factory=list, description="Conversion errors")
    execution_time: float = Field(..., description="Conversion execution time in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Conversion timestamp")


class FrameworkInfo(BaseModel):
    """Framework information model."""
    
    name: str = Field(..., description="Framework name")
    version: str = Field(..., description="Framework version")
    supported_gates: List[str] = Field(..., description="List of supported gates")
    features: List[str] = Field(..., description="Framework features")
    limitations: List[str] = Field(default_factory=list, description="Framework limitations")


class ConversionStats(BaseModel):
    """Conversion statistics model."""
    
    total_conversions: int = Field(..., description="Total number of conversions")
    successful_conversions: int = Field(..., description="Number of successful conversions")
    failed_conversions: int = Field(..., description="Number of failed conversions")
    average_execution_time: float = Field(..., description="Average execution time in seconds")
    framework_stats: Dict[str, Dict[str, int]] = Field(..., description="Statistics by framework")


@router.post("/", response_model=ConversionResponse)
async def convert_circuit(request: ConversionRequest):
    """
    Convert a quantum circuit between different frameworks.
    
    This endpoint converts quantum circuits between Cirq, Qiskit, and PennyLane
    using OpenQASM 3.0 as an intermediate representation. The conversion process
    includes validation, optimization, and detailed statistics.
    
    Args:
        request: ConversionRequest containing source code and conversion parameters
        
    Returns:
        ConversionResponse: Conversion result with converted code and statistics
        
    Raises:
        HTTPException: If conversion fails or invalid parameters provided
    """
    logger.info(f"Starting circuit conversion: {request.source_framework} -> {request.target_framework}")
    
    try:
        # Validate request
        if request.source_framework == request.target_framework:
            raise HTTPException(
                status_code=400,
                detail="Source and target frameworks must be different"
            )
        
        # Perform conversion
        result = await conversion_service.convert_circuit(
            source_framework=request.source_framework,
            target_framework=request.target_framework,
            source_code=request.source_code,
            optimization_level=request.optimization_level,
            include_comments=request.include_comments,
            validate_circuit=request.validate_circuit
        )
        
        # Create response
        response = ConversionResponse(
            success=result.success,
            source_framework=request.source_framework,
            target_framework=request.target_framework,
            converted_code=result.converted_code,
            qasm_code=result.qasm_code,
            stats=result.stats,
            warnings=result.warnings,
            errors=result.errors,
            execution_time=result.execution_time,
            timestamp=datetime.utcnow()
        )
        
        logger.info(f"Circuit conversion completed successfully: {request.source_framework} -> {request.target_framework}")
        
        return response
        
    except QCanvasException as e:
        logger.error(f"Conversion failed: {str(e)}")
        raise HTTPException(
            status_code=e.status_code,
            detail={
                "error": e.error_type,
                "message": e.message,
                "details": e.details
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error during conversion: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/batch", response_model=List[ConversionResponse])
async def convert_circuits_batch(requests: List[ConversionRequest]):
    """
    Convert multiple quantum circuits in batch.
    
    This endpoint processes multiple circuit conversions in parallel,
    providing better performance for bulk operations.
    
    Args:
        requests: List of ConversionRequest objects
        
    Returns:
        List[ConversionResponse]: List of conversion results
        
    Raises:
        HTTPException: If batch processing fails
    """
    logger.info(f"Starting batch conversion of {len(requests)} circuits")
    
    try:
        # Validate batch size
        settings = get_settings()
        max_batch_size = 10  # TODO: Add to settings
        
        if len(requests) > max_batch_size:
            raise HTTPException(
                status_code=400,
                detail=f"Batch size exceeds maximum of {max_batch_size}"
            )
        
        # Process conversions in parallel
        results = await conversion_service.convert_circuits_batch(requests)
        
        logger.info(f"Batch conversion completed: {len(results)} circuits processed")
        
        return results
        
    except Exception as e:
        logger.error(f"Batch conversion failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch conversion failed: {str(e)}"
        )


@router.get("/frameworks", response_model=List[FrameworkInfo])
async def get_supported_frameworks():
    """
    Get information about supported quantum computing frameworks.
    
    This endpoint provides detailed information about each supported
    framework, including version, supported gates, features, and limitations.
    
    Returns:
        List[FrameworkInfo]: Information about supported frameworks
    """
    logger.debug("Retrieving supported frameworks information")
    
    try:
        frameworks = await conversion_service.get_supported_frameworks()
        return frameworks
    except Exception as e:
        logger.error(f"Failed to get framework information: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve framework information: {str(e)}"
        )


@router.get("/stats", response_model=ConversionStats)
async def get_conversion_stats():
    """
    Get conversion statistics and metrics.
    
    This endpoint provides comprehensive statistics about circuit conversions,
    including success rates, execution times, and framework-specific metrics.
    
    Returns:
        ConversionStats: Conversion statistics and metrics
    """
    logger.debug("Retrieving conversion statistics")
    
    try:
        stats = await conversion_service.get_conversion_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get conversion statistics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve conversion statistics: {str(e)}"
        )


@router.post("/validate")
async def validate_circuit(request: ConversionRequest):
    """
    Validate a quantum circuit without converting it.
    
    This endpoint validates the syntax and semantics of a quantum circuit
    in the specified framework without performing conversion.
    
    Args:
        request: ConversionRequest containing circuit to validate
        
    Returns:
        Dict: Validation result with details
    """
    logger.info(f"Validating circuit in {request.source_framework}")
    
    try:
        validation_result = await conversion_service.validate_circuit(
            framework=request.source_framework,
            source_code=request.source_code
        )
        
        return {
            "valid": validation_result.valid,
            "framework": request.source_framework,
            "warnings": validation_result.warnings,
            "errors": validation_result.errors,
            "stats": validation_result.stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Circuit validation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}"
        )


@router.get("/optimize")
async def get_optimization_options():
    """
    Get available optimization options for circuit conversion.
    
    This endpoint provides information about the different optimization
    levels and techniques available during circuit conversion.
    
    Returns:
        Dict: Optimization options and descriptions
    """
    logger.debug("Retrieving optimization options")
    
    return {
        "optimization_levels": {
            0: {
                "name": "No Optimization",
                "description": "Direct conversion without any optimizations",
                "use_cases": ["Debugging", "Exact representation", "Educational purposes"]
            },
            1: {
                "name": "Basic Optimization",
                "description": "Basic gate fusion and simplification",
                "use_cases": ["General use", "Balanced performance", "Most conversions"]
            },
            2: {
                "name": "Advanced Optimization",
                "description": "Advanced optimizations including circuit restructuring",
                "use_cases": ["Performance critical", "Large circuits", "Production use"]
            },
            3: {
                "name": "Maximum Optimization",
                "description": "Maximum possible optimizations, may change circuit structure",
                "use_cases": ["Ultra-performance", "Research", "Experimental"]
            }
        },
        "optimization_techniques": [
            "Gate fusion",
            "Circuit simplification",
            "Dead code elimination",
            "Constant folding",
            "Circuit restructuring",
            "Noise-aware optimization"
        ]
    }


@router.post("/compare")
async def compare_circuits(request: ConversionRequest):
    """
    Compare circuits before and after conversion.
    
    This endpoint converts a circuit and provides detailed comparison
    information including gate counts, circuit depth, and equivalence verification.
    
    Args:
        request: ConversionRequest containing circuit to compare
        
    Returns:
        Dict: Comparison results and analysis
    """
    logger.info(f"Comparing circuit conversion: {request.source_framework} -> {request.target_framework}")
    
    try:
        comparison_result = await conversion_service.compare_circuits(
            source_framework=request.source_framework,
            target_framework=request.target_framework,
            source_code=request.source_code,
            optimization_level=request.optimization_level
        )
        
        return {
            "source_stats": comparison_result.source_stats,
            "target_stats": comparison_result.target_stats,
            "equivalence": comparison_result.equivalence,
            "differences": comparison_result.differences,
            "optimization_impact": comparison_result.optimization_impact,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Circuit comparison failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Comparison failed: {str(e)}"
        )


@router.get("/examples/{framework}")
async def get_framework_examples(framework: str):
    """
    Get example circuits for a specific framework.
    
    This endpoint provides example quantum circuits in the specified
    framework for educational and testing purposes.
    
    Args:
        framework: Framework name (cirq/qiskit/pennylane)
        
    Returns:
        List[Dict]: Example circuits with descriptions
    """
    logger.debug(f"Retrieving examples for framework: {framework}")
    
    try:
        # Validate framework
        valid_frameworks = ["cirq", "qiskit", "pennylane"]
        if framework.lower() not in valid_frameworks:
            raise HTTPException(
                status_code=400,
                detail=f"Framework must be one of {valid_frameworks}"
            )
        
        examples = await conversion_service.get_framework_examples(framework.lower())
        return examples
        
    except Exception as e:
        logger.error(f"Failed to get examples for {framework}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve examples: {str(e)}"
        )
