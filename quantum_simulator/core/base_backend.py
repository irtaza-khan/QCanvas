"""Shared helpers for legacy simulator backends."""

from __future__ import annotations

from abc import ABC
from typing import Any, Dict

import numpy as np


class BaseBackend(ABC):
    """Compatibility base class that mimics the older simulator API."""

    def simulate(self, circuit: dict[str, Any]) -> Dict[str, Any]:
        state = self._simulate_state(circuit)
        probabilities = self._state_probabilities(state)
        return {
            "state": state,
            "probabilities": probabilities,
        }

    def get_state(self, circuit: dict[str, Any]) -> Any:
        return self._simulate_state(circuit)

    def measure(self, circuit: dict[str, Any]) -> Dict[str, Any]:
        state = self._simulate_state(circuit)
        probabilities = self._state_probabilities(state)
        bitstring = max(probabilities, key=probabilities.get) if probabilities else ""
        return {"result": bitstring, "probabilities": probabilities, "state": state}

    def _simulate_state(self, circuit: dict[str, Any]) -> Any:
        num_qubits = int(circuit.get("num_qubits", 0) or 0)
        if num_qubits < 0:
            raise ValueError("num_qubits must be non-negative")

        state = np.zeros(2**num_qubits, dtype=complex)
        state[0] = 1.0

        for gate in circuit.get("gates", []):
            gate_type = gate.get("type")
            qubits = gate.get("qubits", [])
            if gate_type == "h":
                state = self._apply_single_qubit_gate(
                    state,
                    qubits[0],
                    np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2),
                )
            elif gate_type == "x":
                state = self._apply_single_qubit_gate(
                    state,
                    qubits[0],
                    np.array([[0, 1], [1, 0]], dtype=complex),
                )
            elif gate_type == "z":
                state = self._apply_single_qubit_gate(
                    state,
                    qubits[0],
                    np.array([[1, 0], [0, -1]], dtype=complex),
                )
            elif gate_type == "cx":
                state = self._apply_cx(state, qubits[0], qubits[1])
            elif gate_type == "measure":
                continue
            else:
                raise ValueError(f"Unsupported gate: {gate_type}")

        return state

    def _state_probabilities(self, state: Any) -> Dict[str, float]:
        probabilities: Dict[str, float] = {}
        width = max(1, len(state).bit_length() - 1)
        for index, amplitude in enumerate(state):
            probability = float(np.abs(amplitude) ** 2)
            if probability > 1e-12:
                probabilities[format(index, f"0{width}b")] = probability
        return probabilities

    def _apply_single_qubit_gate(self, state: np.ndarray, target: int, gate: np.ndarray) -> np.ndarray:
        result = state.copy()
        step = 1 << target
        period = step << 1
        for start in range(0, len(state), period):
            for offset in range(step):
                zero_index = start + offset
                one_index = zero_index + step
                zero_amp = state[zero_index]
                one_amp = state[one_index]
                result[zero_index] = gate[0, 0] * zero_amp + gate[0, 1] * one_amp
                result[one_index] = gate[1, 0] * zero_amp + gate[1, 1] * one_amp
        return result

    def _apply_cx(self, state: np.ndarray, control: int, target: int) -> np.ndarray:
        result = state.copy()
        control_mask = 1 << control
        target_mask = 1 << target
        for index in range(len(state)):
            if index & control_mask and not index & target_mask:
                partner = index | target_mask
                result[index] = state[partner]
                result[partner] = state[index]
        return result