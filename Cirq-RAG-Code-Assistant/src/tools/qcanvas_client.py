"""
QCanvas Backend API Client

HTTP client for communicating with the QCanvas backend API
for code conversion and quantum simulation.

Author: Umer Farooq, Hussain Waseem Syed, Muhammad Irtaza Khan
Email: umerfarooqcs0891@gmail.com
"""

import requests
from typing import Dict, Any, Optional
from ..cirq_rag_code_assistant.config import get_config
from ..cirq_rag_code_assistant.config.logging import get_logger

logger = get_logger(__name__)


class QCanvasClient:
    """
    Client for QCanvas Backend API.
    
    Uses "compile mode" (two-step flow):
    1. Convert Cirq code to OpenQASM via /api/converter/convert
    2. Execute QASM via /api/simulator/execute-qsim
    """
    
    def __init__(self, base_url: Optional[str] = None):
        """Initialize the QCanvasClient."""
        config = get_config()
        self.base_url = base_url or config.get("agents.qcanvas.backend_url", "http://localhost:8000")
        self.timeout = config.get("agents.qcanvas.timeout_seconds", 30)
        logger.info(f"QCanvasClient initialized with URL: {self.base_url}")
    
    def convert_to_qasm(
        self, 
        code: str, 
        framework: str = "cirq",
        style: str = "classic"
    ) -> Dict[str, Any]:
        """
        Convert quantum code to OpenQASM 3.0.
        Uses POST /api/converter/convert endpoint.
        """
        try:
            logger.debug(f"Converting code: {code[:100]}... Framework: {framework}")
            
            response = requests.post(
                f"{self.base_url}/api/converter/convert",
                json={
                    "code": code,
                    "framework": framework,
                    "style": style
                },
                timeout=self.timeout
            )
            result = response.json()
            logger.debug(f"Conversion Response: {result}")
            
            if result.get("success"):
                logger.info(f"Code converted successfully to QASM")
            else:
                logger.warning(f"Conversion failed: {result.get('error')}")
            
            return result
            
        except Exception as e:
            error_msg = f"Conversion error: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def execute_qasm(
        self, 
        qasm_code: str, 
        backend: str = "cirq",
        shots: int = 1024
    ) -> Dict[str, Any]:
        """
        Execute OpenQASM code using /api/simulator/execute-qsim.
        """
        try:
            logger.debug(f"Executing QASM: {qasm_code[:100]}... Backend: {backend}")
            
            response = requests.post(
                f"{self.base_url}/api/simulator/execute-qsim",
                json={
                    "qasm_input": qasm_code,
                    "backend": backend,
                    "shots": shots
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"Execution Response: {data}")
                if data.get("success"):
                    logger.info(f"QASM executed successfully. Counts: {data.get('results', {}).get('counts', {})}")
                    return data
                else:
                    logger.warning(f"Simulation failed: {data.get('error')}")
                    return {
                        "success": False,
                        "error": data.get("error", "Unknown simulation error"),
                        "stage": "simulation_failed"
                    }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "stage": "api_error"
                }
                
        except Exception as e:
            logger.error(f"QASM execution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "stage": "request_error"
            }
    
    def validate_and_execute(
        self, 
        code: str, 
        framework: str = "cirq",
        shots: int = 1024,
        backend: str = "cirq"
    ) -> Dict[str, Any]:
        """
        Full "compile mode" pipeline: Convert code to QASM then execute.
        """
        conv_result = self.convert_to_qasm(code, framework=framework)
        
        if not conv_result.get("success"):
            return {
                "success": False,
                "stage": "conversion",
                "error": conv_result.get("error", "Conversion failed"),
                "conversion_result": conv_result
            }
        
        qasm_code = conv_result.get("qasm_code", "")
        
        sim_result = self.execute_qasm(qasm_code, backend=backend, shots=shots)
        
        return {
            "success": sim_result.get("success", False),
            "stage": "simulation" if sim_result.get("success") else "simulation_failed",
            "qasm_code": qasm_code,
            "results": sim_result.get("results", {}),
            "backend": sim_result.get("backend", backend),
            "shots": sim_result.get("shots", shots),
            "error": sim_result.get("error"),
            "conversion_stats": conv_result.get("conversion_stats", {})
        }
    
    def check_health(self) -> bool:
        """Check if the QCanvas backend is available."""
        try:
            response = requests.get(
                f"{self.base_url}/api/health",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False
    
    def get_supported_frameworks(self) -> list:
        """Get list of supported quantum frameworks."""
        try:
            response = requests.get(
                f"{self.base_url}/api/converter/frameworks",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            logger.warning(f"Failed to get frameworks: {e}")
            return []
