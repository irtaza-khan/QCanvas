import React, { useState, useEffect, useRef } from "react";
import { cn } from "@/lib/utils";

export type Framework = "qiskit" | "cirq" | "braket";
export type Backend =
  | "qasm_simulator"
  | "statevector_simulator"
  | "aer_simulator";

interface CodeEditorProps {
  onRunCircuit: (
    code: string,
    shots: number,
    backend: Backend,
    framework: Framework,
  ) => Promise<void>;
  initialCode?: string;
  isRunning?: boolean;
  className?: string;
}

const EXAMPLE_CODES = {
  qiskit: `# Write your quantum program here...
# Example: Simple quantum circuit

from qiskit import QuantumCircuit, execute, Aer
from qiskit.visualization import plot_histogram

# Create a quantum circuit with 2 qubits
qc = QuantumCircuit(2, 2)

# Add quantum gates
qc.h(0)  # Hadamard gate on qubit 0
qc.cx(0, 1)  # CNOT gate

# Add measurements
qc.measure_all()

# Execute the circuit
backend = Aer.get_backend('qasm_simulator')
job = execute(qc, backend, shots=1024)
result = job.result()
counts = result.get_counts(qc)

print(counts)`,
  cirq: `# Write your quantum program here...
# Example: Simple quantum circuit

import cirq

# Create qubits
q0, q1 = cirq.LineQubit.range(2)

# Create circuit
circuit = cirq.Circuit()

# Add gates to create Bell state
circuit.append(cirq.H(q0))
circuit.append(cirq.CNOT(q0, q1))

# Add measurements
circuit.append(cirq.measure(q0, q1, key='result'))

print("Circuit:")
print(circuit)

# Simulate
simulator = cirq.Simulator()
result = simulator.run(circuit, repetitions=1024)
print("\\nResults:")
print(result.histogram(key='result'))`,
  braket: `# Write your quantum program here...
# Example: Simple quantum circuit

from braket.circuits import Circuit
from braket.devices import LocalSimulator

# Create circuit
circuit = Circuit()

# Create Bell state
circuit.h(0)
circuit.cnot(0, 1)

# Add measurements
circuit.measure([0, 1])

print("Circuit:")
print(circuit)

# Execute on local simulator
device = LocalSimulator()
task = device.run(circuit, shots=1024)
result = task.result()

print("\\nResults:")
print(result.measurement_counts)`,
};

export function CodeEditor({
  onRunCircuit,
  initialCode,
  isRunning = false,
  className,
}: CodeEditorProps) {
  const [code, setCode] = useState(initialCode || EXAMPLE_CODES.qiskit);
  const [framework, setFramework] = useState<Framework>("qiskit");
  const [shots, setShots] = useState(1024);
  const [backend, setBackend] = useState<Backend>("qasm_simulator");
  const [activeTab, setActiveTab] = useState("main.py");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!initialCode) {
      setCode(EXAMPLE_CODES[framework]);
    }
  }, [framework, initialCode]);

  const handleRunCircuit = async () => {
    if (onRunCircuit && !isRunning) {
      await onRunCircuit(code, shots, backend, framework);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      handleRunCircuit();
    }
  };

  return (
    <div
      className={cn(
        "quantum-glass rounded-2xl overflow-hidden shadow-[0_10px_30px_rgba(0,0,0,0.1)] flex flex-col",
        className,
      )}
    >
      {/* Workspace Header */}
      <div className="quantum-purple-gradient text-white p-4 md:px-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="flex gap-4">
          <div
            className={cn(
              "quantum-tab px-4 py-2 rounded-lg text-sm cursor-pointer",
              activeTab === "main.py" && "active",
            )}
          >
            main.py
          </div>
          <div className="quantum-tab px-4 py-2 rounded-lg text-sm cursor-pointer">
            + New
          </div>
        </div>

        <div className="flex items-center gap-4">
          <label className="text-white font-medium">Framework:</label>
          <select
            value={framework}
            onChange={(e) => setFramework(e.target.value as Framework)}
            className="bg-white/20 border-none text-white px-4 py-2 rounded-lg cursor-pointer outline-none"
          >
            <option
              value="qiskit"
              className="bg-quantum-purple-start text-white"
            >
              Qiskit
            </option>
            <option value="cirq" className="bg-quantum-purple-start text-white">
              Cirq
            </option>
            <option
              value="braket"
              className="bg-quantum-purple-start text-white"
            >
              AWS Braket
            </option>
          </select>
        </div>
      </div>

      {/* Code Editor */}
      <div className="flex-1 relative">
        <textarea
          ref={textareaRef}
          value={code}
          onChange={(e) => setCode(e.target.value)}
          onKeyDown={handleKeyDown}
          className="w-full h-full border-none p-6 font-mono text-sm leading-relaxed bg-editor-background text-editor-foreground resize-none outline-none"
          placeholder="# Write your quantum program here..."
        />
      </div>

      {/* Run Controls */}
      <div className="bg-gray-50 p-4 md:px-6 border-t border-gray-200 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="flex flex-col md:flex-row items-start md:items-center gap-4">
          <div className="flex items-center gap-2">
            <label className="font-medium text-gray-600">Shots:</label>
            <input
              type="number"
              value={shots}
              onChange={(e) => setShots(parseInt(e.target.value) || 1024)}
              min="1"
              max="10000"
              className="px-4 py-2 border border-gray-300 rounded-lg outline-none transition-colors focus:border-quantum-purple-start"
            />
          </div>

          <div className="flex items-center gap-2">
            <label className="font-medium text-gray-600">Backend:</label>
            <select
              value={backend}
              onChange={(e) => setBackend(e.target.value as Backend)}
              className="px-4 py-2 border border-gray-300 rounded-lg outline-none transition-colors focus:border-quantum-purple-start"
            >
              <option value="qasm_simulator">QASM Simulator</option>
              <option value="statevector_simulator">
                Statevector Simulator
              </option>
              <option value="aer_simulator">Aer Simulator</option>
            </select>
          </div>
        </div>

        <button
          onClick={handleRunCircuit}
          disabled={isRunning}
          className="quantum-run-btn px-8 py-3 font-semibold disabled:opacity-60 disabled:cursor-not-allowed disabled:transform-none"
        >
          {isRunning ? "⏳ Running..." : "🚀 Run Circuit"}
        </button>
      </div>
    </div>
  );
}
