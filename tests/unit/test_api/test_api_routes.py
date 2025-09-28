#!/usr/bin/env python3
"""Unit tests for API routes."""

import unittest
import sys
import os
import json

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))


class TestAPIRoutes(unittest.TestCase):
    """Test API route functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        try:
            from backend.app.main import app
            from fastapi.testclient import TestClient
            self.client = TestClient(app)
        except ImportError:
            self.skipTest("FastAPI not available")
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "healthy")
    
    def test_compile_endpoint(self):
        """Test OpenQASM compilation endpoint."""
        payload = {
            "source": "OPENQASM 3.0;\nqubit q;\nh q;",
            "backend": "statevector"
        }
        
        response = self.client.post("/api/compile", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("success", data)
        self.assertTrue(data["success"])
    
    def test_compile_endpoint_with_errors(self):
        """Test compilation endpoint with errors."""
        payload = {
            "source": "OPENQASM 3.0;\nint x = true;",  # Type error
            "backend": "statevector"
        }
        
        response = self.client.post("/api/compile", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("success", data)
        self.assertFalse(data["success"])
        self.assertIn("errors", data)
        self.assertGreater(len(data["errors"]), 0)
    
    def test_convert_endpoint(self):
        """Test framework conversion endpoint."""
        payload = {
            "source": "OPENQASM 3.0;\nqubit q;\nh q;",
            "target_framework": "qiskit"
        }
        
        response = self.client.post("/api/convert", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("success", data)
    
    def test_simulate_endpoint(self):
        """Test simulation endpoint."""
        payload = {
            "source": "OPENQASM 3.0;\nqubit q;\nh q;\nmeasure q -> c;",
            "backend": "statevector",
            "shots": 1000
        }
        
        response = self.client.post("/api/simulate", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("success", data)
        self.assertTrue(data["success"])
        self.assertIn("results", data)
    
    def test_validate_endpoint(self):
        """Test validation endpoint."""
        payload = {
            "source": "OPENQASM 3.0;\nqubit q;\nh q;"
        }
        
        response = self.client.post("/api/validate", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("valid", data)
        self.assertTrue(data["valid"])
    
    def test_validate_endpoint_with_errors(self):
        """Test validation endpoint with errors."""
        payload = {
            "source": "OPENQASM 3.0;\nint x = true;"  # Type error
        }
        
        response = self.client.post("/api/validate", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("valid", data)
        self.assertFalse(data["valid"])
        self.assertIn("errors", data)
    
    def test_get_supported_frameworks(self):
        """Test getting supported frameworks."""
        response = self.client.get("/api/frameworks")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("frameworks", data)
        self.assertIsInstance(data["frameworks"], list)
    
    def test_get_supported_backends(self):
        """Test getting supported backends."""
        response = self.client.get("/api/backends")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("backends", data)
        self.assertIsInstance(data["backends"], list)
    
    def test_invalid_endpoint(self):
        """Test invalid endpoint returns 404."""
        response = self.client.get("/api/invalid")
        self.assertEqual(response.status_code, 404)
    
    def test_malformed_json(self):
        """Test malformed JSON returns 422."""
        response = self.client.post("/api/compile", data="invalid json")
        self.assertEqual(response.status_code, 422)
    
    def test_missing_required_fields(self):
        """Test missing required fields returns 422."""
        payload = {}  # Missing required fields
        
        response = self.client.post("/api/compile", json=payload)
        self.assertEqual(response.status_code, 422)
    
    def test_large_program_compilation(self):
        """Test compilation of large program."""
        # Generate a large OpenQASM program
        source = "OPENQASM 3.0;\n"
        source += "qubit[20] q;\n"
        source += "bit[20] c;\n"
        
        for i in range(20):
            source += f"h q[{i}];\n"
        
        for i in range(0, 20, 2):
            source += f"cx q[{i}], q[{i+1}];\n"
        
        for i in range(20):
            source += f"measure q[{i}] -> c[{i}];\n"
        
        payload = {
            "source": source,
            "backend": "statevector"
        }
        
        response = self.client.post("/api/compile", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])


if __name__ == '__main__':
    unittest.main()
