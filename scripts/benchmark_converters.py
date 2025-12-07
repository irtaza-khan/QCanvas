import sys
import os
import time
import asyncio
from typing import List, Dict

# Setup path to import backend modules
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(project_root, "backend"))

from app.services.conversion_service import ConversionService

def print_header(title):
    print("\n" + "="*60, flush=True)
    print(f" {title}", flush=True)
    print("="*60, flush=True)

async def measure_conversion(service: ConversionService, name: str, code: str, framework: str):
    """Measure single conversion time"""
    start_time = time.perf_counter()
    try:
        result = service.convert_to_qasm(code, framework)
        duration = (time.perf_counter() - start_time) * 1000  # ms
        
        status = "✅ OK" if result["success"] else f"❌ FAIL ({result.get('error')})"
        print(f"{framework:<10} | {name:<15} | {duration:>8.2f} ms | {status}", flush=True)
        return duration
    except Exception as e:
        print(f"{framework:<10} | {name:<15} | {'ERROR':>8}    | ❌ {str(e)}")
        return 0

async def main():
    service = ConversionService()
    
    print_header("Converting Frameworks -> OpenQASM 3.0")
    print(f"{'Framework':<10} | {'Circuit':<15} | {'Time':>8} | {'Status'}", flush=True)
    print("-" * 60, flush=True)

    # 1. Qiskit
    qiskit_code = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
"""
    await measure_conversion(service, "Bell State", qiskit_code, "qiskit")

    # 2. Cirq
    cirq_code = """
import cirq
q0, q1 = cirq.LineQubit.range(2)
circuit = cirq.Circuit(
    cirq.H(q0),
    cirq.CNOT(q0, q1),
    cirq.measure(q0, q1)
)
"""
    await measure_conversion(service, "Bell State", cirq_code, "cirq")

    # 3. PennyLane
    pennylane_code = """
import pennylane as qml
dev = qml.device('default.qubit', wires=2)
@qml.qnode(dev)
def circuit():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.probs(wires=[0, 1])
"""
    await measure_conversion(service, "Bell State", pennylane_code, "pennylane")
    
    # 4. Complex Qiskit (GHZ 5 qubits)
    qiskit_ghz = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(5)
qc.h(0)
for i in range(4):
    qc.cx(i, i+1)
"""
    await measure_conversion(service, "GHZ (5-qubit)", qiskit_ghz, "qiskit")

if __name__ == "__main__":
    asyncio.run(main())
