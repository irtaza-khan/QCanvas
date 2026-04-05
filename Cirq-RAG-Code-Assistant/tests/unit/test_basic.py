"""Basic unit tests for Cirq-RAG-Code-Assistant."""

import pytest
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestBasicFunctionality:
    """Test basic functionality and imports."""

    def test_python_version(self):
        """Test that we're using Python 3.11+."""
        assert sys.version_info >= (3, 11)

    def test_imports(self):
        """Test that basic imports work."""
        try:
            import torch
            import cirq
            import numpy as np
        except ImportError as e:
            pytest.fail(f"Failed to import required packages: {e}")

    def test_pytorch_cuda(self):
        """Test PyTorch CUDA availability."""
        import torch
        assert isinstance(torch.cuda.is_available(), bool)

    def test_cirq_basic(self):
        """Test basic Cirq functionality."""
        import cirq

        q0, q1 = cirq.LineQubit.range(2)
        circuit = cirq.Circuit(cirq.H(q0), cirq.CNOT(q0, q1), cirq.measure(q0, q1, key="m"))
        assert len(circuit) > 0

    def test_numpy_basic(self):
        """Test basic NumPy functionality."""
        import numpy as np

        arr = np.array([1, 2, 3, 4])
        assert arr.sum() == 10
        assert arr.mean() == pytest.approx(2.5)

    @pytest.mark.gpu
    def test_pytorch_cuda_operations(self):
        """Test PyTorch CUDA operations if available."""
        import torch

        if torch.cuda.is_available():
            device = torch.device("cuda:0")
            a = torch.tensor([1.0, 2.0, 3.0], device=device)
            b = torch.tensor([4.0, 5.0, 6.0], device=device)
            c = a + b
            assert torch.sum(c).item() == pytest.approx(21.0)
        else:
            pytest.skip("CUDA device not available")

    def test_project_structure(self, project_root):
        """Test that project structure is correct."""
        assert (project_root / "src").exists()
        assert (project_root / "tests").exists()
        assert (project_root / "docs").exists()
        assert (project_root / "memory-bank").exists()

        assert (project_root / "README.md").exists()
        assert (project_root / "requirements.txt").exists()
        assert (project_root / "pyproject.toml").exists()
        assert (project_root / "LICENSE").exists()

    def test_src_structure(self, src_path):
        """Test that src directory structure is correct."""
        expected_dirs = ["rag", "agents", "orchestration", "evaluation", "cli"]
        for dir_name in expected_dirs:
            assert (src_path / dir_name).exists(), f"Missing directory: {dir_name}"


if __name__ == "__main__":
    pytest.main([__file__])
