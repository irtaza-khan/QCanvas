# Circuit Visualization System Documentation

## Overview

The QCanvas circuit visualization system provides an interactive D3.js-based rendering of quantum circuits. It parses quantum code from Qiskit, Cirq, and PennyLane frameworks and displays them as visual circuit diagrams with full interactivity.

## Architecture

### Component Structure

```
┌─────────────────────────────────────────────────────────┐
│              EditorPane.tsx                             │
│  - Uses parseCircuit() to extract gates from code       │
│  - Passes gates to CircuitVisualization component      │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│         circuitParser.ts (lib/)                          │
│  - Framework detection (Qiskit/Cirq/PennyLane)         │
│  - Gate extraction using regex patterns                │
│  - Gate normalization to common format                 │
│  - Qubit count calculation                             │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│      CircuitVisualization.tsx                           │
│  - D3.js SVG rendering                                  │
│  - Interactive features (hover, click, zoom, pan)       │
│  - Gate drawing functions                               │
│  - Theme-aware styling                                  │
└─────────────────────────────────────────────────────────┘
```

## Parser Architecture

### Framework Detection

The parser automatically detects the quantum framework from source code:

```typescript
function detectFramework(code: string): Framework {
  // Checks for framework-specific imports and patterns
  // Returns: 'qiskit' | 'cirq' | 'pennylane' | 'unknown'
}
```

**Detection Patterns:**
- **Qiskit**: `from qiskit`, `import qiskit`, `.h(`, `.cx(`, `QuantumCircuit`
- **Cirq**: `import cirq`, `cirq.`, `LineQubit`, `circuit.append`
- **PennyLane**: `import pennylane`, `import qml`, `qml.`, `@qml.qnode`, `wires=`

### Parsing Strategy

The parser uses a **multi-pass regex-based approach**:

1. **Framework Detection**: Identify framework from imports/patterns
2. **Line-by-Line Parsing**: Extract gates using regex patterns
3. **Gate Normalization**: Convert all gates to common `ParsedGate` format
4. **Circuit Building**: Organize gates by time step and qubit

### Supported Gates

#### Qiskit Syntax
- **Single qubit**: `.h(qubit)`, `.x(qubit)`, `.y(qubit)`, `.z(qubit)`, `.s(qubit)`, `.t(qubit)`
- **Two qubit**: `.cx(control, target)`, `.cz(control, target)`, `.cy(control, target)`, `.swap(q1, q2)`
- **Parameterized**: `.rx(angle, qubit)`, `.ry(angle, qubit)`, `.rz(angle, qubit)`, `.p(angle, qubit)`
- **Multi-qubit**: `.ccx(c1, c2, target)`, `.cswap(control, t1, t2)`
- **Measurements**: `.measure(qubits, bits)`, `.measure_all()`

#### Cirq Syntax
- **Single qubit**: `cirq.H(qubit)`, `cirq.X(qubit)`, `cirq.Y(qubit)`, `cirq.Z(qubit)`
- **Two qubit**: `cirq.CNOT(control, target)`, `cirq.CZ(control, target)`, `cirq.SWAP(q1, q2)`
- **Parameterized**: `cirq.rx(angle)(qubit)`, `cirq.ry(angle)(qubit)`, `cirq.rz(angle)(qubit)`
- **Circuit append**: `circuit.append(cirq.H(q0))`
- **Measurements**: `cirq.measure(qubit, key='...')`

#### PennyLane Syntax
- **Single qubit**: `qml.Hadamard(wires=qubit)`, `qml.PauliX(wires=qubit)`, `qml.PauliY(wires=qubit)`, `qml.PauliZ(wires=qubit)`
- **Two qubit**: `qml.CNOT(wires=[control, target])`, `qml.CZ(wires=[control, target])`, `qml.SWAP(wires=[q1, q2])`
- **Parameterized**: `qml.RX(angle, wires=qubit)`, `qml.RY(angle, wires=qubit)`, `qml.RZ(angle, wires=qubit)`
- **Measurements**: `qml.measure(wires=qubit)`

### ParsedGate Interface

All gates are normalized to this common format:

```typescript
interface ParsedGate {
  type: string           // 'h', 'x', 'cx', 'ry', etc.
  qubit: number          // Primary qubit index
  control?: number       // For controlled gates
  target?: number        // For two-qubit gates
  angle?: number         // For parameterized gates (in radians)
  qubits?: number[]      // For multi-qubit gates
  name?: string          // Display name
  timestamp?: number     // For animation (line number)
}
```

### Angle Parsing

The parser handles various angle expressions:
- **Pi expressions**: `pi`, `2*pi`, `np.pi`, `math.pi`, `π`
- **Numeric values**: Direct numbers like `0.5`, `1.57`
- **Calculations**: `pi/2`, `3*pi/4`

Example: `cirq.rx(np.pi/2)(q0)` → `angle: 1.5707963267948966`

## Visualization Architecture

### D3.js Structure

The visualization uses D3.js for SVG rendering:

```typescript
SVG Container
  └── Main Group (with zoom transform)
      ├── Qubit Lines (horizontal lines for each qubit)
      ├── Qubit Labels (q0, q1, q2, ...)
      └── Gate Groups (one per gate)
          ├── Gate Elements (rect, circle, lines)
          └── Event Handlers (mouseenter, mouseleave, click)
```

### Layout System

**Spacing:**
- **Qubit spacing**: 60px vertical spacing between qubits
- **Gate spacing**: 80px horizontal spacing between gates
- **Margins**: 20px top/bottom, 60px left (for labels), 20px right

**Width Calculation:**
```typescript
const width = Math.max(600, gates.length * 80 + margin.left + margin.right)
```

**Height Calculation:**
```typescript
const height = qubits * 60 + margin.top + margin.bottom
```

### Gate Rendering Functions

Each gate type has a dedicated drawing function:

#### Single Qubit Gates

**Hadamard (H)**: Blue rounded rectangle with "H" label
```typescript
drawHGate(g, x, y, label, gate)
```

**Pauli-X (X)**: Red circle with "X" label
```typescript
drawXGate(g, x, y, gate)
```

**Pauli-Y (Y)**: Green circle with "Y" label
```typescript
drawYGate(g, x, y, gate)
```

**Pauli-Z (Z)**: Purple circle with "Z" label
```typescript
drawZGate(g, x, y, gate)
```

**S Gate**: Cyan rounded rectangle with "S" label
```typescript
drawSGate(g, x, y, gate)
```

**T Gate**: Teal rounded rectangle with "T" label
```typescript
drawTGate(g, x, y, gate)
```

#### Two Qubit Gates

**CNOT (CX)**: Control dot + connecting line + X target
```typescript
drawCNOTGate(g, x, controlY, targetY, gate)
```

**CZ**: Control dot + connecting line + Z target (filled dot)
```typescript
drawCZGate(g, x, controlY, targetY, gate)
```

**SWAP**: Two X symbols connected by a line
```typescript
drawSWAPGate(g, x, qubit1Y, qubit2Y, gate)
```

#### Parameterized Gates

**Rotation Gates (RX, RY, RZ)**: Orange rounded rectangle with gate name and angle
```typescript
drawRotationGate(g, x, y, label, angle, gate)
```

**Phase Gate (P)**: Orange rounded rectangle with "P" and angle
```typescript
drawPhaseGate(g, x, y, angle, gate)
```

#### Measurement

**Measurement**: Gray rounded rectangle with meter icon
```typescript
drawMeasurementGate(g, x, y, gate)
```

### Interactive Features

#### 1. Hover Tooltips

**Implementation:**
- D3 tooltip created on component mount
- Positioned dynamically based on mouse coordinates
- Shows gate type, qubits, and parameters

**Event Handler:**
```typescript
.on('mouseenter', function(event) {
  setHoveredGate(gate)
  // Highlight gate with thicker stroke
  d3.select(this).selectAll('rect, circle')
    .attr('stroke-width', 3)
    .attr('stroke', colors.hover)
  
  // Show tooltip with gate info
  tooltip.transition().duration(200).style('opacity', 0.95)
  tooltip.html(getGateInfo(gate))
    .style('left', (event.pageX + 10) + 'px')
    .style('top', (event.pageY - 10) + 'px')
})
```

**Tooltip Content:**
- Gate type (uppercase)
- Qubit indices (or control/target for two-qubit gates)
- Angle in radians and degrees (for parameterized gates)

#### 2. Click-to-Expand Details

**Implementation:**
- Click on any gate to select it
- Selected gate shows details panel in top-right corner
- Click again to deselect

**State Management:**
```typescript
const [selectedGate, setSelectedGate] = useState<Gate | null>(null)
```

**Details Panel:**
- Shows gate type, qubits, and angle information
- Positioned absolutely in top-right corner
- Styled to match editor theme

#### 3. Zoom and Pan

**Implementation:**
- D3 zoom behavior attached to SVG
- Mouse wheel for zoom (0.5x to 3x)
- Click and drag for panning

**Zoom Setup:**
```typescript
const zoom = d3.zoom<SVGSVGElement, unknown>()
  .scaleExtent([0.5, 3])
  .on('zoom', (event) => {
    mainGroup.attr('transform', 
      `translate(${margin.left + event.transform.x},${margin.top + event.transform.y}) scale(${event.transform.k})`
    )
  })

svg.call(zoom as any)
```

**Touch Support:**
- Pinch-to-zoom on touch devices
- Pan with touch drag

#### 4. Gate Highlighting

**Hover Highlight:**
- Blue stroke on hover
- Thicker stroke width (3px vs 2px)

**Selection Highlight:**
- Green stroke when selected
- Persists until deselected

**Animation:**
- Smooth transitions using D3 transitions
- 200ms duration for opacity changes

### Theme Support

**Dark/Light Mode:**
- Automatically detects theme from `document.documentElement.classList`
- Updates colors dynamically using MutationObserver
- Theme-aware colors for all elements

**Color Scheme:**
```typescript
const colors = {
  background: isDarkMode ? '#1e1e1e' : '#ffffff',
  qubitLine: isDarkMode ? '#4B5563' : '#9CA3AF',
  qubitLabel: isDarkMode ? '#9CA3AF' : '#6B7280',
  gateStroke: isDarkMode ? '#6B7280' : '#4B5563',
  text: isDarkMode ? '#ffffff' : '#1F2937',
  hover: isDarkMode ? '#3B82F6' : '#2563EB',
  selected: isDarkMode ? '#10B981' : '#059669',
}
```

**Gate Colors (Theme-independent):**
- H: Blue (#3B82F6)
- X: Red (#EF4444)
- Y: Green (#10B981)
- Z: Purple (#8B5CF6)
- S: Cyan (#06B6D4)
- T: Teal (#14B8A6)
- RX/RY/RZ/P: Orange (#F59E0B)
- Measure: Gray (#6B7280)

## Usage Examples

### Basic Usage

```typescript
import { parseCircuit, calculateQubitCount } from '@/lib/circuitParser'
import CircuitVisualization from '@/components/CircuitVisualization'

// Parse circuit from code
const gates = parseCircuit(sourceCode)
const qubits = calculateQubitCount(gates)

// Render visualization
<CircuitVisualization 
  gates={gates} 
  qubits={qubits} 
  className="h-32" 
/>
```

### Example: Bell State Circuit

**Qiskit Code:**
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
- Qubit 0: H gate → CNOT control
- Qubit 1: (empty) → CNOT target
- Horizontal lines connecting qubits
- Interactive gates with hover/click

### Example: Quantum Teleportation

**Cirq Code:**
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
- 3 qubits displayed vertically
- H gate on q0
- Two CNOT gates connecting qubits
- All gates interactive

## Performance Considerations

### Optimization Strategies

1. **Gate Grouping**: Each gate in its own `<g>` element for efficient selection
2. **Event Delegation**: Single event handlers on gate groups
3. **Conditional Rendering**: Only render when gates.length > 0
4. **Memoization**: Gates array passed as prop (parent manages updates)

### Scalability

- **Tested up to**: 20 qubits, 100+ gates
- **Performance**: Smooth rendering and interaction
- **Memory**: Efficient SVG rendering (no canvas overhead)

## Extending the System

### Adding New Gate Types

1. **Update Parser** (`circuitParser.ts`):
   - Add regex pattern for new gate syntax
   - Extract gate parameters
   - Return normalized `ParsedGate`

2. **Update Visualization** (`CircuitVisualization.tsx`):
   - Add case in switch statement
   - Create drawing function: `drawNewGate(g, x, y, gate)`
   - Add gate colors to `getGateColor()` function

**Example: Adding Toffoli Gate**

```typescript
// In parser (parseQiskit function)
const toffoliMatch = line.match(/\.ccx\((\d+),\s*(\d+),\s*(\d+)\)/)
if (toffoliMatch) {
  const [, c1, c2, target] = toffoliMatch
  gates.push({
    type: 'ccx',
    qubit: parseInt(c1),
    qubits: [parseInt(c1), parseInt(c2), parseInt(target)],
    control: parseInt(c1),
    target: parseInt(target),
    timestamp: i
  })
}

// In visualization (switch statement)
case 'ccx':
case 'toffoli':
  if (gate.qubits && gate.qubits.length === 3) {
    drawToffoliGate(gateGroup, x, gate.qubits[0] * qubitSpacing + 30, 
                    gate.qubits[1] * qubitSpacing + 30, 
                    gate.qubits[2] * qubitSpacing + 30, gate)
  }
  break

// New drawing function
function drawToffoliGate(g, x, c1Y, c2Y, targetY, gate) {
  // Draw two control dots
  // Draw connecting lines
  // Draw X target
}
```

### Adding New Frameworks

1. **Create Parser Function**:
   ```typescript
   function parseNewFramework(code: string): ParsedGate[] {
     // Extract gates using framework-specific patterns
     // Return normalized gates
   }
   ```

2. **Update Framework Detection**:
   ```typescript
   function detectFramework(code: string): Framework {
     if (code.includes('newframework')) return 'newframework'
     // ... existing detection
   }
   ```

3. **Add to Main Parser**:
   ```typescript
   switch (framework) {
     case 'newframework':
       return parseNewFramework(code)
     // ... existing cases
   }
   ```

## Testing

### Test Cases

The visualization has been tested with:

1. **Bell State** (2 qubits, 2 gates)
   - Qiskit: `.h(0)`, `.cx(0, 1)`
   - Cirq: `cirq.H(q0)`, `cirq.CNOT(q0, q1)`
   - PennyLane: `qml.Hadamard(wires=0)`, `qml.CNOT(wires=[0, 1])`

2. **Quantum Teleportation** (3 qubits, 5+ gates)
   - Multiple H and CNOT gates
   - Measurements

3. **Deutsch-Jozsa** (3 qubits, loops)
   - Loop-based gate application
   - Multiple Hadamard gates

4. **Grover's Search** (2 qubits, 10+ gates)
   - Complex multi-step algorithm
   - Oracle and diffusion operators

5. **QRNG** (8 qubits, 8 gates in loop)
   - Multiple Hadamard gates
   - Loop parsing

6. **XOR Demo** (2 qubits, parameterized gates)
   - RX, RY gates with angles
   - Parameter parsing

7. **QML XOR Classifier** (2 qubits, complex circuit)
   - Multiple parameterized gates
   - Variational circuit structure

## Troubleshooting

### Common Issues

**Issue**: Gates not appearing
- **Solution**: Check that parser is detecting framework correctly
- **Debug**: Log `parseCircuit()` output to console

**Issue**: Incorrect qubit indices
- **Solution**: Verify qubit variable extraction in parser
- **Debug**: Check `extractQubitIndex()` function

**Issue**: Zoom/pan not working
- **Solution**: Ensure SVG has proper dimensions
- **Debug**: Check D3 zoom behavior attachment

**Issue**: Tooltip not showing
- **Solution**: Check tooltip z-index and positioning
- **Debug**: Verify mouse event coordinates

**Issue**: Theme not updating
- **Solution**: Check MutationObserver setup
- **Debug**: Verify `document.documentElement.classList` changes

## Future Enhancements

### Planned Features

1. **Animation Support**:
   - Sequential gate highlighting
   - Step-through mode
   - Play/pause controls

2. **Export Options**:
   - Export as PNG/SVG
   - Copy circuit diagram

3. **Advanced Layout**:
   - Automatic circuit optimization
   - Gate alignment improvements
   - Better multi-qubit gate rendering

4. **Performance**:
   - Virtual scrolling for large circuits
   - Lazy rendering for off-screen gates
   - WebGL rendering option

## References

- **D3.js Documentation**: https://d3js.org/
- **OpenQASM 3.0 Specification**: https://openqasm.com/
- **Qiskit Documentation**: https://qiskit.org/
- **Cirq Documentation**: https://quantumai.google/cirq
- **PennyLane Documentation**: https://pennylane.ai/
