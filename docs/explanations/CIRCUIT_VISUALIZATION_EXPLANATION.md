# Circuit Visualization System - How It Works

## Introduction

The QCanvas circuit visualization system transforms quantum code written in Qiskit, Cirq, or PennyLane into interactive visual circuit diagrams. This document explains the complete workflow from code parsing to interactive rendering.

## System Workflow

```
┌─────────────────┐
│  Source Code    │  (Qiskit/Cirq/PennyLane)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Parser         │  (circuitParser.ts)
│  - Detect       │
│  - Extract      │
│  - Normalize    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Parsed Gates   │  (ParsedGate[])
│  - Type         │
│  - Qubits       │
│  - Parameters   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Visualization  │  (CircuitVisualization.tsx)
│  - D3.js SVG    │
│  - Interactive  │
│  - Theme-aware  │
└─────────────────┘
```

## Step-by-Step Process

### Step 1: Code Input

User writes quantum code in the Monaco editor:

```python
from qiskit import QuantumCircuit
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
```

### Step 2: Framework Detection

The parser analyzes the code to identify the framework:

```typescript
// Checks for framework-specific patterns
if (code.includes('from qiskit') || code.includes('.h(')) {
  return 'qiskit'
}
```

**Detection Logic:**
- Looks for imports: `from qiskit`, `import cirq`, `import pennylane`
- Checks for method calls: `.h(`, `cirq.`, `qml.`
- Identifies class names: `QuantumCircuit`, `LineQubit`, `@qml.qnode`

### Step 3: Gate Extraction

The appropriate parser function extracts gates line by line:

**Qiskit Example:**
```typescript
// Line: "qc.h(0)"
const match = line.match(/\.h\((\d+)\)/)
if (match) {
  gates.push({
    type: 'h',
    qubit: parseInt(match[1]),  // qubit: 0
    timestamp: lineIndex
  })
}
```

**Cirq Example:**
```typescript
// Line: "circuit.append(cirq.H(q0))"
const match = line.match(/cirq\.H\(([^)]+)\)/)
if (match) {
  const qubitRef = match[1]  // "q0"
  const qubit = extractQubitIndex(qubitRef, qubitVars, qubitCounter)
  gates.push({
    type: 'h',
    qubit: qubit,
    timestamp: lineIndex
  })
}
```

**PennyLane Example:**
```typescript
// Line: "qml.Hadamard(wires=0)"
const match = line.match(/qml\.Hadamard\(wires=(\d+)\)/)
if (match) {
  gates.push({
    type: 'h',
    qubit: parseInt(match[1]),  // qubit: 0
    timestamp: lineIndex
  })
}
```

### Step 4: Gate Normalization

All gates are converted to the common `ParsedGate` format:

```typescript
interface ParsedGate {
  type: string        // Normalized: 'h', 'x', 'cx', 'ry', etc.
  qubit: number       // Primary qubit index
  control?: number    // For controlled gates
  target?: number     // For two-qubit gates
  angle?: number      // For parameterized gates (radians)
  qubits?: number[]   // For multi-qubit gates
  name?: string       // Display name
  timestamp?: number  // Line number for ordering
}
```

**Normalization Examples:**
- `cirq.H(q0)` → `{ type: 'h', qubit: 0 }`
- `qml.PauliX(wires=1)` → `{ type: 'x', qubit: 1 }`
- `qc.ry(pi/2, 0)` → `{ type: 'ry', qubit: 0, angle: 1.5708 }`
- `qc.cx(0, 1)` → `{ type: 'cx', qubit: 0, control: 0, target: 1 }`

### Step 5: Qubit Count Calculation

The system calculates how many qubits are needed:

```typescript
function calculateQubitCount(gates: ParsedGate[]): number {
  let maxQubit = 0
  for (const gate of gates) {
    maxQubit = Math.max(maxQubit, gate.qubit)
    if (gate.control !== undefined) maxQubit = Math.max(maxQubit, gate.control)
    if (gate.target !== undefined) maxQubit = Math.max(maxQubit, gate.target)
  }
  return Math.max(2, maxQubit + 1)  // At least 2 qubits
}
```

### Step 6: SVG Rendering

D3.js creates the visual representation:

#### 6.1 Create SVG Container

```typescript
const svg = d3.select(svgRef.current)
svg.attr('width', width).attr('height', height)
```

#### 6.2 Draw Qubit Lines

```typescript
for (let i = 0; i < qubits; i++) {
  const y = i * qubitSpacing + 30
  mainGroup.append('line')
    .attr('x1', 0)
    .attr('y1', y)
    .attr('x2', width, y)
    .attr('stroke', colors.qubitLine)
}
```

#### 6.3 Draw Gates

For each gate, create a group and draw the appropriate symbol:

```typescript
gates.forEach((gate, gateIndex) => {
  const x = gateIndex * gateSpacing + 40
  const y = gate.qubit * qubitSpacing + 30
  
  const gateGroup = mainGroup.append('g')
    .attr('class', 'gate-group')
    .on('mouseenter', handleHover)
    .on('click', handleClick)
  
  // Draw gate based on type
  switch (gate.type) {
    case 'h': drawHGate(gateGroup, x, y, 'H', gate); break
    case 'cx': drawCNOTGate(gateGroup, x, controlY, targetY, gate); break
    // ... other gates
  }
})
```

### Step 7: Interactive Features

#### 7.1 Hover Tooltip

When user hovers over a gate:

```typescript
.on('mouseenter', function(event) {
  // Highlight gate
  d3.select(this).selectAll('rect, circle')
    .attr('stroke-width', 3)
    .attr('stroke', colors.hover)
  
  // Show tooltip
  tooltip.html(getGateInfo(gate))
    .style('left', (event.pageX + 10) + 'px')
    .style('top', (event.pageY - 10) + 'px')
    .style('opacity', 0.95)
})
```

**Tooltip Content:**
```
H
Qubit: q0
```

#### 7.2 Click Selection

When user clicks a gate:

```typescript
.on('click', function() {
  setSelectedGate(gate)
  // Update all gates to show selection
  mainGroup.selectAll('.gate-group').each(function() {
    const isSelected = gates[i] === selectedGate
    d3.select(this).selectAll('rect, circle')
      .attr('stroke', isSelected ? colors.selected : defaultStroke)
  })
})
```

**Details Panel Shows:**
```
Gate Details
Type: CX
Control: q0
Target: q1
```

#### 7.3 Zoom and Pan

D3 zoom behavior enables:

```typescript
const zoom = d3.zoom()
  .scaleExtent([0.5, 3])  // 0.5x to 3x zoom
  .on('zoom', (event) => {
    mainGroup.attr('transform', 
      `translate(${event.transform.x},${event.transform.y}) scale(${event.transform.k})`
    )
  })

svg.call(zoom)
```

**Controls:**
- **Mouse wheel**: Zoom in/out
- **Click + drag**: Pan circuit
- **Touch pinch**: Zoom on mobile
- **Touch drag**: Pan on mobile

## Gate Drawing Details

### Hadamard Gate (H)

**Visual**: Blue rounded rectangle with "H" label

```typescript
function drawHGate(g, x, y, label, gate) {
  g.append('rect')
    .attr('x', x - 15)
    .attr('y', y - 15)
    .attr('width', 30)
    .attr('height', 30)
    .attr('fill', '#3B82F6')  // Blue
    .attr('stroke', '#1D4ED8')
    .attr('rx', 4)  // Rounded corners
  
  g.append('text')
    .attr('x', x)
    .attr('y', y + 5)
    .text('H')
}
```

### CNOT Gate (CX)

**Visual**: Control dot + connecting line + X target

```typescript
function drawCNOTGate(g, x, controlY, targetY, gate) {
  // Control dot (filled circle)
  g.append('circle')
    .attr('cx', x)
    .attr('cy', controlY)
    .attr('r', 6)
    .attr('fill', colors.background)
    .attr('stroke', colors.gateStroke)
  
  // Connecting line
  g.append('line')
    .attr('x1', x)
    .attr('y1', controlY)
    .attr('x2', x)
    .attr('y2', targetY)
    .attr('stroke', colors.gateStroke)
  
  // Target (X symbol in circle)
  g.append('circle')
    .attr('cx', x)
    .attr('cy', targetY)
    .attr('r', 15)
    .attr('fill', 'none')
    .attr('stroke', colors.gateStroke)
  
  // X symbol (two crossing lines)
  g.append('line')
    .attr('x1', x - 8)
    .attr('y1', targetY - 8)
    .attr('x2', x + 8)
    .attr('y2', targetY + 8)
    .attr('stroke', colors.gateStroke)
  
  g.append('line')
    .attr('x1', x - 8)
    .attr('y1', targetY + 8)
    .attr('x2', x + 8)
    .attr('y2', targetY - 8)
    .attr('stroke', colors.gateStroke)
}
```

### Rotation Gate (RX/RY/RZ)

**Visual**: Orange rounded rectangle with gate name and angle

```typescript
function drawRotationGate(g, x, y, label, angle, gate) {
  g.append('rect')
    .attr('x', x - 20)
    .attr('y', y - 15)
    .attr('width', 40)
    .attr('height', 30)
    .attr('fill', '#F59E0B')  // Orange
    .attr('stroke', '#D97706')
    .attr('rx', 4)
  
  g.append('text')
    .attr('x', x)
    .attr('y', y + 2)
    .text(label)  // "RX", "RY", or "RZ"
  
  if (angle !== undefined) {
    g.append('text')
      .attr('x', x)
      .attr('y', y + 12)
      .attr('font-size', '8px')
      .text(`(${angle.toFixed(2)})`)  // Angle in radians
  }
}
```

## Algorithm Examples

### Bell State Circuit

**Code:**
```python
from qiskit import QuantumCircuit
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
```

**Parsed Gates:**
```typescript
[
  { type: 'h', qubit: 0, timestamp: 2 },
  { type: 'cx', qubit: 0, control: 0, target: 1, timestamp: 3 }
]
```

**Visualization:**
```
q0 ──[H]──●──
          │
q1 ───────X──
```

**Interactive Features:**
- Hover over H gate: Shows "H, Qubit: q0"
- Hover over CNOT: Shows "CX, Control: q0, Target: q1"
- Click to see detailed information
- Zoom/pan to adjust view

### Quantum Teleportation

**Code:**
```python
import cirq
q0, q1, q2 = cirq.LineQubit.range(3)
circuit = cirq.Circuit()
circuit.append(cirq.H(q0))
circuit.append(cirq.CNOT(q0, q1))
circuit.append(cirq.CNOT(q1, q2))
```

**Parsed Gates:**
```typescript
[
  { type: 'h', qubit: 0, timestamp: 4 },
  { type: 'cx', qubit: 0, control: 0, target: 1, timestamp: 5 },
  { type: 'cx', qubit: 1, control: 1, target: 2, timestamp: 6 }
]
```

**Visualization:**
```
q0 ──[H]──●────────────
          │
q1 ───────X──●────────
             │
q2 ──────────X────────
```

### Grover's Search

**Code:**
```python
from qiskit import QuantumCircuit
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.h(1)
qc.cz(0, 1)
qc.h(0)
qc.h(1)
qc.x(0)
qc.x(1)
qc.cz(0, 1)
qc.x(0)
qc.x(1)
qc.h(0)
qc.h(1)
```

**Parsed Gates:**
```typescript
[
  { type: 'h', qubit: 0 }, { type: 'h', qubit: 1 },
  { type: 'cz', qubit: 0, control: 0, target: 1 },
  { type: 'h', qubit: 0 }, { type: 'h', qubit: 1 },
  { type: 'x', qubit: 0 }, { type: 'x', qubit: 1 },
  { type: 'cz', qubit: 0, control: 0, target: 1 },
  { type: 'x', qubit: 0 }, { type: 'x', qubit: 1 },
  { type: 'h', qubit: 0 }, { type: 'h', qubit: 1 }
]
```

**Visualization:**
```
q0 ──[H]──[H]──●──[H]──[X]──●──[X]──[H]──
               │            │
q1 ──[H]───────●──[H]──[X]──●──[X]──[H]──
```

## Advanced Features

### Theme Support

The visualization automatically adapts to light/dark themes:

```typescript
// Detect theme changes
useEffect(() => {
  const checkTheme = () => {
    setIsDarkMode(!document.documentElement.classList.contains('light'))
  }
  const observer = new MutationObserver(checkTheme)
  observer.observe(document.documentElement, { 
    attributes: true, 
    attributeFilter: ['class'] 
  })
  return () => observer.disconnect()
}, [])
```

**Theme Colors:**
- **Dark mode**: Dark backgrounds, light text, muted qubit lines
- **Light mode**: Light backgrounds, dark text, visible qubit lines

### Performance Optimization

1. **Efficient Rendering**: Only re-renders when gates or qubits change
2. **Event Delegation**: Single event handlers on gate groups
3. **Conditional Rendering**: Skips rendering for empty circuits
4. **SVG Optimization**: Uses groups for efficient selection

### Error Handling

The parser gracefully handles:
- **Unknown frameworks**: Tries all parsers, returns best match
- **Invalid syntax**: Skips unrecognized lines, continues parsing
- **Missing qubits**: Infers qubit count from gate indices
- **Complex expressions**: Simplifies angle calculations

## Summary

The circuit visualization system provides:

1. **Comprehensive Parsing**: Supports Qiskit, Cirq, and PennyLane
2. **Rich Visualization**: D3.js-based interactive SVG rendering
3. **Full Interactivity**: Hover tooltips, click details, zoom/pan
4. **Theme Support**: Automatic dark/light mode adaptation
5. **Extensibility**: Easy to add new gates and frameworks

The system transforms quantum code into visual, interactive circuit diagrams that help users understand and debug their quantum algorithms.
