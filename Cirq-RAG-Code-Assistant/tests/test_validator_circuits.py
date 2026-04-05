"""
Validator Agent Test Suite (Cirq)

These tests validate that the ValidatorAgent can:
- compile/exec Cirq code and extract a `cirq.Circuit` named `circuit`
- detect missing measurements in comprehensive mode
- produce measurement counts via local simulation
"""

from __future__ import annotations

from src.agents.validator import ValidatorAgent
from src.rag.knowledge_base import KnowledgeBase
from src.rag.retriever import Retriever
from src.rag.embeddings import EmbeddingModel


def _make_validator() -> ValidatorAgent:
    # Force local embeddings so unit tests don't require AWS/boto3.
    kb = KnowledgeBase(
        embedding_model=EmbeddingModel(
            provider="local",
            model_name="BAAI/bge-base-en-v1.5",
        )
    )
    retriever = Retriever(kb)
    return ValidatorAgent(mode="local", retriever=retriever)


def test_validator_passes_simple_bell_state() -> None:
    validator = _make_validator()
    code = """
import cirq
q0, q1 = cirq.LineQubit.range(2)
circuit = cirq.Circuit(
    cirq.H(q0),
    cirq.CNOT(q0, q1),
    cirq.measure(q0, q1, key="m"),
)
"""
    result = validator.execute(
        {
            "code": code,
            "description": "Create and measure a Bell state.",
            "validation_level": "comprehensive",
            "require_measurements": True,
        }
    )
    assert result.get("success") is True
    assert result.get("validation_passed") is True
    assert isinstance(result.get("results", {}).get("counts", {}), dict)


def test_validator_fails_without_measurement_when_required() -> None:
    validator = _make_validator()
    code = """
import cirq
q0, q1 = cirq.LineQubit.range(2)
circuit = cirq.Circuit(
    cirq.H(q0),
    cirq.CNOT(q0, q1),
)
"""
    result = validator.execute(
        {
            "code": code,
            "description": "Bell state but missing measurement.",
            "validation_level": "comprehensive",
            "require_measurements": True,
        }
    )
    assert result.get("success") is False
    assert result.get("validation_passed") is False
    assert "measurement" in str(result.get("error", "")).lower()

