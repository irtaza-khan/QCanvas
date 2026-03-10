/**
 * Static knowledge base for Quantum Explain It mode: hover tooltips for
 * Cirq, Qiskit, PennyLane, Python keywords, and common built-ins.
 * Used by the Monaco hover provider.
 */

export type SymbolKind = 'function' | 'class' | 'variable' | 'keyword'

export interface HoverSymbolEntry {
  kind: SymbolKind
  signature?: string
  description: string
  framework?: 'cirq' | 'qiskit' | 'pennylane'
}

/** Map: symbol key -> hover entry. Dotted keys (e.g. "cirq.H") take priority over bare keys. */
const SYMBOLS: Record<string, HoverSymbolEntry> = {

  // =====================================================================
  //  Cirq
  // =====================================================================
  cirq: {
    kind: 'variable',
    description: 'Google Cirq - Python library for creating, editing, and invoking Noisy Intermediate Scale Quantum (NISQ) circuits.',
    framework: 'cirq',
  },
  'cirq.Circuit': {
    kind: 'class',
    signature: 'class cirq.Circuit(*contents)',
    description: 'A mutable container for quantum operations (gates, measurements). Append gates and measurements, then run on a simulator or device.',
    framework: 'cirq',
  },
  Circuit: {
    kind: 'class',
    signature: 'class Circuit(*contents)',
    description: 'Quantum circuit - mutable container for operations. Use cirq.Circuit() or QuantumCircuit() depending on framework.',
  },
  'cirq.LineQubit': {
    kind: 'class',
    signature: 'class cirq.LineQubit(x: int)',
    description: 'A qubit on a 1D line identified by an integer index. Use LineQubit(i) or LineQubit.range(n).',
    framework: 'cirq',
  },
  LineQubit: {
    kind: 'class',
    signature: 'class LineQubit(x: int)',
    description: 'Cirq qubit on a 1D line. LineQubit(i) or LineQubit.range(n).',
    framework: 'cirq',
  },
  'cirq.GridQubit': {
    kind: 'class',
    signature: 'class cirq.GridQubit(row: int, col: int)',
    description: 'A qubit on a 2D grid identified by (row, col).',
    framework: 'cirq',
  },
  GridQubit: {
    kind: 'class',
    signature: 'class GridQubit(row: int, col: int)',
    description: 'Cirq qubit on a 2D grid.',
    framework: 'cirq',
  },
  'cirq.NamedQubit': {
    kind: 'class',
    signature: 'class cirq.NamedQubit(name: str)',
    description: 'A qubit identified by name rather than index.',
    framework: 'cirq',
  },
  NamedQubit: {
    kind: 'class',
    signature: 'class NamedQubit(name: str)',
    description: 'Cirq qubit identified by name.',
    framework: 'cirq',
  },

  // Cirq single-qubit gates
  'cirq.H': { kind: 'function', signature: 'cirq.H(qubit) -> ops.GateOperation', description: 'Hadamard gate - creates equal superposition of |0> and |1>.', framework: 'cirq' },
  'cirq.X': { kind: 'function', signature: 'cirq.X(qubit) -> ops.GateOperation', description: 'Pauli-X gate (bit flip). Maps |0> to |1> and |1> to |0>.', framework: 'cirq' },
  'cirq.Y': { kind: 'function', signature: 'cirq.Y(qubit) -> ops.GateOperation', description: 'Pauli-Y gate.', framework: 'cirq' },
  'cirq.Z': { kind: 'function', signature: 'cirq.Z(qubit) -> ops.GateOperation', description: 'Pauli-Z gate (phase flip). Maps |1> to -|1>.', framework: 'cirq' },
  'cirq.S': { kind: 'function', signature: 'cirq.S(qubit) -> ops.GateOperation', description: 'S gate (sqrt of Z). Applies a pi/2 phase.', framework: 'cirq' },
  'cirq.T': { kind: 'function', signature: 'cirq.T(qubit) -> ops.GateOperation', description: 'T gate (sqrt of S). Applies a pi/4 phase.', framework: 'cirq' },
  'cirq.rx': { kind: 'function', signature: 'cirq.rx(rads)(qubit)', description: 'Rotation around X axis by given angle in radians.', framework: 'cirq' },
  'cirq.ry': { kind: 'function', signature: 'cirq.ry(rads)(qubit)', description: 'Rotation around Y axis by given angle in radians.', framework: 'cirq' },
  'cirq.rz': { kind: 'function', signature: 'cirq.rz(rads)(qubit)', description: 'Rotation around Z axis by given angle in radians.', framework: 'cirq' },

  // Cirq multi-qubit gates
  'cirq.CNOT': { kind: 'function', signature: 'cirq.CNOT(control, target) -> ops.GateOperation', description: 'Controlled-NOT gate. Flips target qubit when control is |1>.', framework: 'cirq' },
  'cirq.CX': { kind: 'function', signature: 'cirq.CX(control, target)', description: 'Alias for CNOT (controlled-X).', framework: 'cirq' },
  'cirq.CZ': { kind: 'function', signature: 'cirq.CZ(q0, q1) -> ops.GateOperation', description: 'Controlled-Z gate. Applies Z to target when control is |1>.', framework: 'cirq' },
  'cirq.SWAP': { kind: 'function', signature: 'cirq.SWAP(q0, q1) -> ops.GateOperation', description: 'Swap gate - exchanges the states of two qubits.', framework: 'cirq' },
  'cirq.ISWAP': { kind: 'function', signature: 'cirq.ISWAP(q0, q1)', description: 'iSWAP gate - swap with an i phase.', framework: 'cirq' },
  'cirq.CCX': { kind: 'function', signature: 'cirq.CCX(c0, c1, target)', description: 'Toffoli (double-controlled X) gate.', framework: 'cirq' },
  'cirq.CCZ': { kind: 'function', signature: 'cirq.CCZ(c0, c1, c2)', description: 'Double-controlled Z gate.', framework: 'cirq' },
  'cirq.CSWAP': { kind: 'function', signature: 'cirq.CSWAP(control, t0, t1)', description: 'Fredkin (controlled swap) gate.', framework: 'cirq' },
  'cirq.XX': { kind: 'function', signature: 'cirq.XX(q0, q1)', description: 'Ising XX coupling gate.', framework: 'cirq' },
  'cirq.YY': { kind: 'function', signature: 'cirq.YY(q0, q1)', description: 'Ising YY coupling gate.', framework: 'cirq' },
  'cirq.ZZ': { kind: 'function', signature: 'cirq.ZZ(q0, q1)', description: 'Ising ZZ coupling gate.', framework: 'cirq' },

  // Cirq operations
  'cirq.measure': { kind: 'function', signature: 'cirq.measure(*qubits, key: str = None) -> MeasurementGate', description: 'Measure one or more qubits. Results stored under the optional key.', framework: 'cirq' },
  'cirq.measure_each': { kind: 'function', signature: 'cirq.measure_each(*qubits, key_func=None)', description: 'Measure each qubit individually with separate keys.', framework: 'cirq' },
  'cirq.reset': { kind: 'function', signature: 'cirq.reset(qubit)', description: 'Reset a qubit to the |0> state.', framework: 'cirq' },
  'cirq.I': { kind: 'function', signature: 'cirq.I(qubit)', description: 'Identity gate - does nothing (useful as placeholder).', framework: 'cirq' },
  'cirq.append': { kind: 'function', signature: 'circuit.append(op_or_ops)', description: 'Append operations to the circuit.', framework: 'cirq' },

  // Cirq simulators
  'cirq.Simulator': { kind: 'class', signature: 'class cirq.Simulator', description: 'Pure state-vector simulator. Use .run() or .simulate() to execute circuits.', framework: 'cirq' },
  Simulator: { kind: 'class', signature: 'class Simulator', description: 'Cirq state-vector simulator.', framework: 'cirq' },
  'cirq.DensityMatrixSimulator': { kind: 'class', signature: 'class cirq.DensityMatrixSimulator', description: 'Density matrix simulator - supports mixed states and noise.', framework: 'cirq' },
  DensityMatrixSimulator: { kind: 'class', signature: 'class DensityMatrixSimulator', description: 'Cirq density matrix simulator.', framework: 'cirq' },

  // =====================================================================
  //  Qiskit
  // =====================================================================
  QuantumCircuit: {
    kind: 'class',
    signature: 'QuantumCircuit(num_qubits: int, num_clbits: int = 0, name: str = None)',
    description: 'Qiskit quantum circuit. Add gates with .h(), .cx(), .x(), etc. Measure with .measure() or .measure_all().',
    framework: 'qiskit',
  },
  qc: {
    kind: 'variable',
    signature: 'qc: QuantumCircuit',
    description: 'Common variable name for a Qiskit QuantumCircuit instance.',
    framework: 'qiskit',
  },
  execute: {
    kind: 'function',
    signature: 'execute(circuit, backend, shots=1024, ...) -> Job',
    description: 'Run a circuit on a backend. Returns a Job; call job.result() to get results.',
    framework: 'qiskit',
  },
  Aer: {
    kind: 'class',
    signature: 'Aer',
    description: 'Qiskit Aer provider: high-performance simulators (qasm_simulator, statevector_simulator, etc.).',
    framework: 'qiskit',
  },
  get_backend: {
    kind: 'function',
    signature: 'Aer.get_backend(name: str) -> Backend',
    description: 'Get a simulator backend by name (e.g. "qasm_simulator", "statevector_simulator").',
    framework: 'qiskit',
  },
  measure_all: {
    kind: 'function',
    signature: 'qc.measure_all(add_bits: bool = True)',
    description: 'Measure all qubits. Adds classical register if needed.',
    framework: 'qiskit',
  },
  measure: {
    kind: 'function',
    signature: 'qc.measure(qubit, cbit) | cirq.measure(*qubits) | qml.measure(wires)',
    description: 'Measure a qubit, collapsing its superposition. Syntax varies by framework.',
  },

  // Qiskit single-qubit gates
  h: { kind: 'function', signature: 'qc.h(qubit: int)', description: 'Hadamard gate on qubit.', framework: 'qiskit' },
  x: { kind: 'function', signature: 'qc.x(qubit: int)', description: 'Pauli-X (bit flip) gate.', framework: 'qiskit' },
  y: { kind: 'function', signature: 'qc.y(qubit: int)', description: 'Pauli-Y gate.', framework: 'qiskit' },
  z: { kind: 'function', signature: 'qc.z(qubit: int)', description: 'Pauli-Z (phase flip) gate.', framework: 'qiskit' },
  s: { kind: 'function', signature: 'qc.s(qubit: int)', description: 'S gate (sqrt of Z).', framework: 'qiskit' },
  sdg: { kind: 'function', signature: 'qc.sdg(qubit: int)', description: 'S-dagger gate (inverse of S).', framework: 'qiskit' },
  t: { kind: 'function', signature: 'qc.t(qubit: int)', description: 'T gate (sqrt of S).', framework: 'qiskit' },
  tdg: { kind: 'function', signature: 'qc.tdg(qubit: int)', description: 'T-dagger gate (inverse of T).', framework: 'qiskit' },
  rx: { kind: 'function', signature: 'qc.rx(theta: float, qubit: int)', description: 'Rotation around X axis by angle theta.', framework: 'qiskit' },
  ry: { kind: 'function', signature: 'qc.ry(theta: float, qubit: int)', description: 'Rotation around Y axis by angle theta.', framework: 'qiskit' },
  rz: { kind: 'function', signature: 'qc.rz(theta: float, qubit: int)', description: 'Rotation around Z axis by angle theta.', framework: 'qiskit' },
  p: { kind: 'function', signature: 'qc.p(theta: float, qubit: int)', description: 'Phase gate - applies phase of theta.', framework: 'qiskit' },
  u: { kind: 'function', signature: 'qc.u(theta, phi, lam, qubit)', description: 'General single-qubit unitary (3 Euler angles).', framework: 'qiskit' },

  // Qiskit multi-qubit gates
  cx: { kind: 'function', signature: 'qc.cx(control: int, target: int)', description: 'CNOT (controlled-X) gate.', framework: 'qiskit' },
  cz: { kind: 'function', signature: 'qc.cz(control: int, target: int)', description: 'Controlled-Z gate.', framework: 'qiskit' },
  cy: { kind: 'function', signature: 'qc.cy(control: int, target: int)', description: 'Controlled-Y gate.', framework: 'qiskit' },
  ch: { kind: 'function', signature: 'qc.ch(control: int, target: int)', description: 'Controlled-Hadamard gate.', framework: 'qiskit' },
  swap: { kind: 'function', signature: 'qc.swap(q0: int, q1: int)', description: 'SWAP gate - exchange two qubit states.', framework: 'qiskit' },
  ccx: { kind: 'function', signature: 'qc.ccx(c0: int, c1: int, target: int)', description: 'Toffoli (double-controlled X) gate.', framework: 'qiskit' },
  cswap: { kind: 'function', signature: 'qc.cswap(control: int, t0: int, t1: int)', description: 'Fredkin (controlled SWAP) gate.', framework: 'qiskit' },
  barrier: { kind: 'function', signature: 'qc.barrier(*qubits)', description: 'Insert a barrier to prevent gate optimizations across it.', framework: 'qiskit' },

  // Qiskit results
  get_counts: { kind: 'function', signature: 'result.get_counts(circuit=None) -> dict', description: 'Get measurement counts (e.g. {"00": 512, "11": 512}).', framework: 'qiskit' },
  result: { kind: 'variable', signature: 'result: Result', description: 'Qiskit job result. Use .get_counts() to read measurement outcomes.', framework: 'qiskit' },
  job: { kind: 'variable', signature: 'job: Job', description: 'Qiskit job handle. Call .result() to wait for and retrieve results.', framework: 'qiskit' },
  counts: { kind: 'variable', signature: 'counts: dict[str, int]', description: 'Dictionary of measurement outcomes to their counts.' },
  backend: { kind: 'variable', signature: 'backend: Backend', description: 'Qiskit simulation or hardware backend.', framework: 'qiskit' },
  shots: { kind: 'variable', signature: 'shots: int', description: 'Number of times to repeat the circuit execution.' },

  // =====================================================================
  //  PennyLane
  // =====================================================================
  qml: {
    kind: 'variable',
    description: 'PennyLane - library for quantum ML and differentiable quantum computing. Typically imported as: import pennylane as qml.',
    framework: 'pennylane',
  },
  pennylane: {
    kind: 'variable',
    description: 'PennyLane - library for quantum ML and differentiable quantum circuits.',
    framework: 'pennylane',
  },
  'qml.device': { kind: 'function', signature: 'qml.device(name: str, wires: int, shots: int = None)', description: 'Create a PennyLane device (e.g. "default.qubit").', framework: 'pennylane' },
  device: { kind: 'function', signature: 'qml.device(name: str, wires: int, shots: int = None)', description: 'Create a PennyLane device.', framework: 'pennylane' },
  dev: { kind: 'variable', signature: 'dev: qml.Device', description: 'Common variable for a PennyLane device instance.', framework: 'pennylane' },
  QNode: { kind: 'class', signature: 'QNode(func, device, interface=None)', description: 'PennyLane quantum node: wraps a circuit function for execution.', framework: 'pennylane' },
  'qml.qnode': { kind: 'function', signature: '@qml.qnode(dev)', description: 'Decorator to turn a function into a QNode that runs on the given device.', framework: 'pennylane' },
  qnode: { kind: 'function', signature: '@qml.qnode(dev)', description: 'Decorator to create a PennyLane QNode.', framework: 'pennylane' },

  // PennyLane single-qubit gates
  'qml.Hadamard': { kind: 'function', signature: 'qml.Hadamard(wires: int)', description: 'Hadamard gate.', framework: 'pennylane' },
  Hadamard: { kind: 'function', signature: 'qml.Hadamard(wires)', description: 'PennyLane Hadamard gate.', framework: 'pennylane' },
  'qml.PauliX': { kind: 'function', signature: 'qml.PauliX(wires: int)', description: 'Pauli-X (bit flip) gate.', framework: 'pennylane' },
  PauliX: { kind: 'function', signature: 'qml.PauliX(wires)', description: 'PennyLane Pauli-X gate.', framework: 'pennylane' },
  'qml.PauliY': { kind: 'function', signature: 'qml.PauliY(wires: int)', description: 'Pauli-Y gate.', framework: 'pennylane' },
  PauliY: { kind: 'function', signature: 'qml.PauliY(wires)', description: 'PennyLane Pauli-Y gate.', framework: 'pennylane' },
  'qml.PauliZ': { kind: 'function', signature: 'qml.PauliZ(wires: int)', description: 'Pauli-Z (phase flip) gate.', framework: 'pennylane' },
  PauliZ: { kind: 'function', signature: 'qml.PauliZ(wires)', description: 'PennyLane Pauli-Z gate.', framework: 'pennylane' },
  'qml.S': { kind: 'function', signature: 'qml.S(wires: int)', description: 'S gate (sqrt of Z).', framework: 'pennylane' },
  'qml.T': { kind: 'function', signature: 'qml.T(wires: int)', description: 'T gate (sqrt of S).', framework: 'pennylane' },
  'qml.RX': { kind: 'function', signature: 'qml.RX(phi: float, wires: int)', description: 'Rotation around X axis.', framework: 'pennylane' },
  RX: { kind: 'function', signature: 'qml.RX(phi, wires)', description: 'PennyLane X-rotation gate.', framework: 'pennylane' },
  'qml.RY': { kind: 'function', signature: 'qml.RY(phi: float, wires: int)', description: 'Rotation around Y axis.', framework: 'pennylane' },
  RY: { kind: 'function', signature: 'qml.RY(phi, wires)', description: 'PennyLane Y-rotation gate.', framework: 'pennylane' },
  'qml.RZ': { kind: 'function', signature: 'qml.RZ(phi: float, wires: int)', description: 'Rotation around Z axis.', framework: 'pennylane' },
  RZ: { kind: 'function', signature: 'qml.RZ(phi, wires)', description: 'PennyLane Z-rotation gate.', framework: 'pennylane' },
  'qml.PhaseShift': { kind: 'function', signature: 'qml.PhaseShift(phi, wires)', description: 'Phase shift gate.', framework: 'pennylane' },
  'qml.Rot': { kind: 'function', signature: 'qml.Rot(phi, theta, omega, wires)', description: 'General single-qubit rotation (3 Euler angles).', framework: 'pennylane' },
  'qml.SX': { kind: 'function', signature: 'qml.SX(wires)', description: 'Sqrt-X gate.', framework: 'pennylane' },

  // PennyLane multi-qubit gates
  'qml.CNOT': { kind: 'function', signature: 'qml.CNOT(wires=[control, target])', description: 'Controlled-NOT gate.', framework: 'pennylane' },
  'qml.CZ': { kind: 'function', signature: 'qml.CZ(wires=[control, target])', description: 'Controlled-Z gate.', framework: 'pennylane' },
  CZ: { kind: 'function', signature: 'qml.CZ(wires=[c, t])', description: 'PennyLane CZ gate.', framework: 'pennylane' },
  'qml.CY': { kind: 'function', signature: 'qml.CY(wires=[control, target])', description: 'Controlled-Y gate.', framework: 'pennylane' },
  'qml.SWAP': { kind: 'function', signature: 'qml.SWAP(wires=[q0, q1])', description: 'SWAP gate - exchange two qubit states.', framework: 'pennylane' },
  SWAP: { kind: 'function', signature: 'qml.SWAP(wires=[q0, q1]) | cirq.SWAP(q0, q1)', description: 'Swap two qubit states.' },
  'qml.Toffoli': { kind: 'function', signature: 'qml.Toffoli(wires=[c0, c1, target])', description: 'Toffoli (double-controlled X) gate.', framework: 'pennylane' },
  Toffoli: { kind: 'function', signature: 'qml.Toffoli(wires=[c0, c1, target])', description: 'Toffoli gate.', framework: 'pennylane' },
  'qml.CSWAP': { kind: 'function', signature: 'qml.CSWAP(wires=[control, t0, t1])', description: 'Fredkin (controlled SWAP) gate.', framework: 'pennylane' },
  'qml.CRX': { kind: 'function', signature: 'qml.CRX(phi, wires=[c, t])', description: 'Controlled RX rotation.', framework: 'pennylane' },
  'qml.CRY': { kind: 'function', signature: 'qml.CRY(phi, wires=[c, t])', description: 'Controlled RY rotation.', framework: 'pennylane' },
  'qml.CRZ': { kind: 'function', signature: 'qml.CRZ(phi, wires=[c, t])', description: 'Controlled RZ rotation.', framework: 'pennylane' },
  'qml.IsingXX': { kind: 'function', signature: 'qml.IsingXX(phi, wires)', description: 'Ising XX coupling gate.', framework: 'pennylane' },
  'qml.IsingYY': { kind: 'function', signature: 'qml.IsingYY(phi, wires)', description: 'Ising YY coupling gate.', framework: 'pennylane' },
  'qml.IsingZZ': { kind: 'function', signature: 'qml.IsingZZ(phi, wires)', description: 'Ising ZZ coupling gate.', framework: 'pennylane' },
  'qml.MultiControlledX': { kind: 'function', signature: 'qml.MultiControlledX(wires)', description: 'Multi-controlled X gate.', framework: 'pennylane' },

  // PennyLane measurements
  'qml.expval': { kind: 'function', signature: 'qml.expval(observable) -> float', description: 'Expectation value of an observable.', framework: 'pennylane' },
  expval: { kind: 'function', signature: 'qml.expval(observable)', description: 'PennyLane: expectation value.', framework: 'pennylane' },
  'qml.var': { kind: 'function', signature: 'qml.var(observable) -> float', description: 'Variance of an observable.', framework: 'pennylane' },
  'qml.probs': { kind: 'function', signature: 'qml.probs(wires) -> array', description: 'Probability distribution over computational basis states.', framework: 'pennylane' },
  probs: { kind: 'function', signature: 'qml.probs(wires)', description: 'PennyLane: measurement probabilities.', framework: 'pennylane' },
  'qml.sample': { kind: 'function', signature: 'qml.sample(observable=None, wires=None)', description: 'Sample from the circuit. Returns raw samples.', framework: 'pennylane' },
  sample: { kind: 'function', signature: 'qml.sample(observable)', description: 'PennyLane: sample measurements.', framework: 'pennylane' },
  'qml.counts': { kind: 'function', signature: 'qml.counts(observable=None, wires=None)', description: 'Count occurrences of each outcome.', framework: 'pennylane' },
  'qml.state': { kind: 'function', signature: 'qml.state() -> array', description: 'Return the full quantum state vector.', framework: 'pennylane' },
  'qml.density_matrix': { kind: 'function', signature: 'qml.density_matrix(wires) -> array', description: 'Return the density matrix of specified wires.', framework: 'pennylane' },
  'qml.measure': { kind: 'function', signature: 'qml.measure(wires: int) -> MeasurementValue', description: 'Mid-circuit measurement.', framework: 'pennylane' },
  'qml.adjoint': { kind: 'function', signature: 'qml.adjoint(fn)', description: 'Apply the adjoint (inverse) of an operation or template.', framework: 'pennylane' },
  adjoint: { kind: 'function', signature: 'qml.adjoint(fn)', description: 'PennyLane adjoint (inverse).', framework: 'pennylane' },

  wires: { kind: 'variable', signature: 'wires: int | Sequence[int]', description: 'Qubit indices in PennyLane.' },

  // =====================================================================
  //  QCanvas / QSim (hybrid execution)
  // =====================================================================
  compile: { kind: 'function', signature: 'compile(circuit, framework: str) -> str', description: 'QCanvas: compile a framework circuit to OpenQASM 3.0.', },
  qcanvas: { kind: 'variable', description: 'QCanvas module. Use compile() to convert circuits to OpenQASM 3.0.', },
  qsim: { kind: 'variable', description: 'QSim module. Use qsim.run(qasm, shots, backend) to execute OpenQASM circuits.', },
  run: { kind: 'function', signature: 'qsim.run(qasm: str, shots: int = 1024, backend: str = "cirq")', description: 'Execute compiled QASM; returns object with .counts and .probabilities.', },
  probabilities: { kind: 'variable', signature: 'probabilities: dict[str, float]', description: 'Probability distribution over measurement outcomes.' },
  qasm: { kind: 'variable', signature: 'qasm: str', description: 'OpenQASM 3.0 source string.' },

  // =====================================================================
  //  Common quantum variable names
  // =====================================================================
  n_qubits: { kind: 'variable', signature: 'n_qubits: int', description: 'Number of qubits in the circuit.' },
  n_bits: { kind: 'variable', signature: 'n_bits: int', description: 'Number of classical bits (measurement results).' },
  num_qubits: { kind: 'variable', signature: 'num_qubits: int', description: 'Number of qubits.' },
  qubits: { kind: 'variable', signature: 'qubits: Sequence[Qubit]', description: 'Sequence of qubit objects.' },
  circuit: { kind: 'variable', signature: 'circuit: Circuit', description: 'Quantum circuit instance.' },
  q: { kind: 'variable', signature: 'q: Qubit | list[Qubit]', description: 'Qubit or list of qubits.' },
  q0: { kind: 'variable', signature: 'q0: Qubit', description: 'First qubit (index 0).' },
  q1: { kind: 'variable', signature: 'q1: Qubit', description: 'Second qubit (index 1).' },
  q2: { kind: 'variable', signature: 'q2: Qubit', description: 'Third qubit (index 2).' },
  key: { kind: 'variable', signature: 'key: str', description: 'Measurement key string (Cirq).' },
  theta: { kind: 'variable', signature: 'theta: float', description: 'Rotation angle parameter (radians).' },
  phi: { kind: 'variable', signature: 'phi: float', description: 'Phase angle parameter (radians).' },
  params: { kind: 'variable', signature: 'params: array', description: 'Variational parameters for quantum circuits.' },
  np: { kind: 'variable', description: 'NumPy - numerical computing library. Typically imported as: import numpy as np.' },
  numpy: { kind: 'variable', description: 'NumPy - fundamental package for scientific computing with Python.' },
  math: { kind: 'variable', description: 'Python math module - mathematical functions (sin, cos, pi, sqrt, etc.).' },
  pi: { kind: 'variable', signature: 'pi: float = 3.14159...', description: 'Mathematical constant pi.' },

  // =====================================================================
  //  Python keywords
  // =====================================================================
  for: { kind: 'keyword', signature: 'for variable in iterable:', description: 'Iterate over items in a sequence (list, range, etc.).' },
  in: { kind: 'keyword', description: 'Membership test (x in seq) or iteration target (for x in seq).' },
  if: { kind: 'keyword', signature: 'if condition:', description: 'Conditional execution - run block when condition is true.' },
  else: { kind: 'keyword', signature: 'else:', description: 'Alternative branch when the if condition is false.' },
  elif: { kind: 'keyword', signature: 'elif condition:', description: 'Else-if: chain another condition after if.' },
  while: { kind: 'keyword', signature: 'while condition:', description: 'Repeat block while condition remains true.' },
  break: { kind: 'keyword', description: 'Exit the innermost for or while loop immediately.' },
  continue: { kind: 'keyword', description: 'Skip to the next iteration of the loop.' },
  pass: { kind: 'keyword', description: 'No-op placeholder where a statement is syntactically required.' },
  return: { kind: 'keyword', signature: 'return [value]', description: 'Exit function and optionally return a value.' },
  yield: { kind: 'keyword', signature: 'yield value', description: 'Produce a value from a generator; execution pauses until next().' },
  def: { kind: 'keyword', signature: 'def name(params):', description: 'Define a function.' },
  lambda: { kind: 'keyword', signature: 'lambda args: expression', description: 'Create an anonymous inline function.' },
  with: { kind: 'keyword', signature: 'with expr as name:', description: 'Context manager for automatic setup/teardown.' },
  as: { kind: 'keyword', description: 'Alias name in imports (import x as y) or with statements.' },
  is: { kind: 'keyword', description: 'Identity test - True if two variables reference the same object.' },
  try: { kind: 'keyword', signature: 'try:', description: 'Begin a block that may raise exceptions.' },
  except: { kind: 'keyword', signature: 'except [ExceptionType]:', description: 'Handle exceptions from the try block.' },
  finally: { kind: 'keyword', signature: 'finally:', description: 'Block that always runs after try/except.' },
  raise: { kind: 'keyword', signature: 'raise [Exception]', description: 'Raise an exception.' },
  assert: { kind: 'keyword', signature: 'assert condition [, message]', description: 'Raise AssertionError if condition is false.' },
  import: { kind: 'keyword', signature: 'import module [as alias]', description: 'Import a module.' },
  from: { kind: 'keyword', signature: 'from module import name', description: 'Import specific names from a module.' },
  and: { kind: 'keyword', description: 'Logical AND - true only when both operands are true.' },
  or: { kind: 'keyword', description: 'Logical OR - true when at least one operand is true.' },
  not: { kind: 'keyword', description: 'Logical NOT - invert a boolean value.' },
  True: { kind: 'keyword', signature: 'True: bool', description: 'Boolean true literal.' },
  False: { kind: 'keyword', signature: 'False: bool', description: 'Boolean false literal.' },
  None: { kind: 'keyword', signature: 'None: NoneType', description: 'Singleton representing absence of a value.' },
  global: { kind: 'keyword', signature: 'global name', description: 'Declare a global variable inside a function.' },
  nonlocal: { kind: 'keyword', signature: 'nonlocal name', description: 'Reference a variable from the nearest enclosing scope.' },
  del: { kind: 'keyword', signature: 'del name', description: 'Delete a variable, item, or attribute.' },
  async: { kind: 'keyword', signature: 'async def func():', description: 'Define an asynchronous coroutine function.' },
  await: { kind: 'keyword', signature: 'await coroutine', description: 'Wait for an async operation to complete.' },

  // =====================================================================
  //  Python built-in functions
  // =====================================================================
  range: { kind: 'function', signature: 'range(stop) -> range\nrange(start, stop[, step]) -> range', description: 'Immutable sequence of integers. Commonly used in for loops.' },
  print: { kind: 'function', signature: String.raw`print(*objects, sep=" ", end="\n", file=sys.stdout)`, description: 'Print objects to the text stream.' },
  len: { kind: 'function', signature: 'len(obj: Sized) -> int', description: 'Return the number of items in a container.' },
  type: { kind: 'function', signature: 'type(object) -> type', description: 'Return the type of an object.' },
  int: { kind: 'class', signature: 'int(x=0) -> int', description: 'Integer type. Convert a number or string to an integer.' },
  float: { kind: 'class', signature: 'float(x=0) -> float', description: 'Floating-point type. Convert a number or string to float.' },
  str: { kind: 'class', signature: 'str(object="") -> str', description: 'String type. Convert an object to its string representation.' },
  bool: { kind: 'class', signature: 'bool(x=False) -> bool', description: 'Boolean type. Returns True or False.' },
  list: { kind: 'class', signature: 'list(iterable=()) -> list', description: 'Mutable ordered sequence. Create from an iterable or [].' },
  dict: { kind: 'class', signature: 'dict(**kwargs) -> dict', description: 'Mutable key-value mapping. Create with {} or dict().' },
  tuple: { kind: 'class', signature: 'tuple(iterable=()) -> tuple', description: 'Immutable ordered sequence.' },
  set: { kind: 'class', signature: 'set(iterable=()) -> set', description: 'Mutable unordered collection of unique elements.' },
  frozenset: { kind: 'class', signature: 'frozenset(iterable=()) -> frozenset', description: 'Immutable set.' },
  bytes: { kind: 'class', signature: 'bytes(source=b"") -> bytes', description: 'Immutable sequence of bytes.' },
  bytearray: { kind: 'class', signature: 'bytearray(source=b"") -> bytearray', description: 'Mutable sequence of bytes.' },
  complex: { kind: 'class', signature: 'complex(real=0, imag=0) -> complex', description: 'Complex number type.' },
  abs: { kind: 'function', signature: 'abs(x) -> number', description: 'Return the absolute value of a number.' },
  min: { kind: 'function', signature: 'min(iterable, *[, key, default])', description: 'Return the smallest item.' },
  max: { kind: 'function', signature: 'max(iterable, *[, key, default])', description: 'Return the largest item.' },
  sum: { kind: 'function', signature: 'sum(iterable, start=0)', description: 'Sum items of an iterable.' },
  round: { kind: 'function', signature: 'round(number, ndigits=None)', description: 'Round a number to ndigits decimal places.' },
  sorted: { kind: 'function', signature: 'sorted(iterable, *, key=None, reverse=False) -> list', description: 'Return a new sorted list.' },
  reversed: { kind: 'function', signature: 'reversed(seq) -> iterator', description: 'Return a reverse iterator.' },
  enumerate: { kind: 'function', signature: 'enumerate(iterable, start=0) -> iterator', description: 'Yield (index, item) pairs.' },
  zip: { kind: 'function', signature: 'zip(*iterables) -> iterator', description: 'Aggregate elements from multiple iterables.' },
  map: { kind: 'function', signature: 'map(func, *iterables) -> iterator', description: 'Apply func to every item of iterables.' },
  filter: { kind: 'function', signature: 'filter(func, iterable) -> iterator', description: 'Return items for which func returns true.' },
  any: { kind: 'function', signature: 'any(iterable) -> bool', description: 'True if any element is truthy.' },
  all: { kind: 'function', signature: 'all(iterable) -> bool', description: 'True if all elements are truthy.' },
  isinstance: { kind: 'function', signature: 'isinstance(obj, classinfo) -> bool', description: 'Check if obj is an instance of classinfo.' },
  issubclass: { kind: 'function', signature: 'issubclass(cls, classinfo) -> bool', description: 'Check if cls is a subclass of classinfo.' },
  hasattr: { kind: 'function', signature: 'hasattr(obj, name: str) -> bool', description: 'Check if obj has the named attribute.' },
  getattr: { kind: 'function', signature: 'getattr(obj, name[, default])', description: 'Get attribute value, with optional default.' },
  setattr: { kind: 'function', signature: 'setattr(obj, name: str, value)', description: 'Set attribute on an object.' },
  delattr: { kind: 'function', signature: 'delattr(obj, name: str)', description: 'Delete a named attribute.' },
  property: { kind: 'function', signature: 'property(fget=None, fset=None, fdel=None, doc=None)', description: 'Create a managed attribute (descriptor).' },
  staticmethod: { kind: 'function', signature: '@staticmethod', description: 'Define a method that does not receive an implicit first argument.' },
  classmethod: { kind: 'function', signature: '@classmethod', description: 'Define a method that receives the class as first argument.' },
  super: { kind: 'function', signature: 'super() -> proxy', description: 'Return a proxy to delegate method calls to a parent class.' },
  open: { kind: 'function', signature: 'open(file, mode="r", ...) -> file object', description: 'Open a file and return a file object.' },
  input: { kind: 'function', signature: 'input(prompt="") -> str', description: 'Read a line of text from standard input.' },
  format: { kind: 'function', signature: 'format(value, format_spec="")', description: 'Format a value using a format specification.' },
  repr: { kind: 'function', signature: 'repr(obj) -> str', description: 'Return a printable representation of an object.' },
  id: { kind: 'function', signature: 'id(obj) -> int', description: 'Return the identity (memory address) of an object.' },
  hash: { kind: 'function', signature: 'hash(obj) -> int', description: 'Return the hash value of an object.' },
  callable: { kind: 'function', signature: 'callable(obj) -> bool', description: 'Check if an object is callable.' },
  iter: { kind: 'function', signature: 'iter(iterable) -> iterator', description: 'Return an iterator for the object.' },
  next: { kind: 'function', signature: 'next(iterator[, default])', description: 'Get the next item from an iterator.' },
  object: { kind: 'class', signature: 'class object', description: 'Base class for all Python classes.' },
  Exception: { kind: 'class', signature: 'class Exception(BaseException)', description: 'Base class for all built-in, non-system-exiting exceptions.' },
  ValueError: { kind: 'class', signature: 'class ValueError(Exception)', description: 'Raised when an operation receives an argument with the right type but wrong value.' },
  TypeError: { kind: 'class', signature: 'class TypeError(Exception)', description: 'Raised when an operation is applied to an object of inappropriate type.' },
  IndexError: { kind: 'class', signature: 'class IndexError(LookupError)', description: 'Raised when a sequence index is out of range.' },
  KeyError: { kind: 'class', signature: 'class KeyError(LookupError)', description: 'Raised when a dictionary key is not found.' },
  AttributeError: { kind: 'class', signature: 'class AttributeError(Exception)', description: 'Raised when an attribute reference or assignment fails.' },
  ImportError: { kind: 'class', signature: 'class ImportError(Exception)', description: 'Raised when an import statement fails.' },
  RuntimeError: { kind: 'class', signature: 'class RuntimeError(Exception)', description: 'Raised when an error does not fall into other categories.' },
  StopIteration: { kind: 'class', signature: 'class StopIteration(Exception)', description: 'Raised by next() when the iterator is exhausted.' },
  ZeroDivisionError: { kind: 'class', signature: 'class ZeroDivisionError(ArithmeticError)', description: 'Raised when dividing by zero.' },
  FileNotFoundError: { kind: 'class', signature: 'class FileNotFoundError(OSError)', description: 'Raised when a file or directory is not found.' },

  // Common methods that appear as bare words after a dot
  append: { kind: 'function', signature: '.append(item)', description: 'Add an item to the end of a list, or append operations to a circuit.' },
  extend: { kind: 'function', signature: '.extend(iterable)', description: 'Extend a list by appending elements from an iterable.' },
  keys: { kind: 'function', signature: '.keys() -> dict_keys', description: 'Return view of dictionary keys.' },
  values: { kind: 'function', signature: '.values() -> dict_values', description: 'Return view of dictionary values.' },
  items: { kind: 'function', signature: '.items() -> dict_items', description: 'Return view of dictionary (key, value) pairs.' },
  join: { kind: 'function', signature: 'str.join(iterable) -> str', description: 'Join elements of an iterable with the string as separator.' },
  split: { kind: 'function', signature: 'str.split(sep=None, maxsplit=-1) -> list', description: 'Split a string by separator.' },
  strip: { kind: 'function', signature: 'str.strip(chars=None) -> str', description: 'Remove leading and trailing whitespace (or specified chars).' },
  replace: { kind: 'function', signature: 'str.replace(old, new[, count]) -> str', description: 'Return a copy with all occurrences of old replaced by new.' },
  startswith: { kind: 'function', signature: 'str.startswith(prefix) -> bool', description: 'Check if string starts with prefix.' },
  endswith: { kind: 'function', signature: 'str.endswith(suffix) -> bool', description: 'Check if string ends with suffix.' },
  upper: { kind: 'function', signature: 'str.upper() -> str', description: 'Return uppercased copy of the string.' },
  lower: { kind: 'function', signature: 'str.lower() -> str', description: 'Return lowercased copy of the string.' },
}

/**
 * Resolve hover content. Tries full dotted name first, then bare word.
 */
export function getHoverForSymbol(
  word: string,
  dottedPrefix?: string
): HoverSymbolEntry | null {
  if (!word || word.length === 0) return null
  const fullKey = dottedPrefix ? `${dottedPrefix}.${word}` : word
  return SYMBOLS[fullKey] ?? SYMBOLS[word] ?? null
}

/**
 * Format a hover entry as Markdown for Monaco's hover widget.
 */
export function formatHoverMarkdown(entry: HoverSymbolEntry): string {
  let kindLabel: string
  if (entry.kind === 'function') kindLabel = '(function)'
  else if (entry.kind === 'class') kindLabel = '(class)'
  else if (entry.kind === 'keyword') kindLabel = '(keyword)'
  else kindLabel = '(variable)'
  const parts: string[] = [kindLabel]
  if (entry.signature) {
    parts.push('```python\n' + entry.signature + '\n```')
  }
  parts.push(entry.description)
  if (entry.framework) {
    parts.push(`\n*Framework: ${entry.framework}*`)
  }
  return parts.join('\n\n')
}
