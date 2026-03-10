# QCanvas — Complete Quantum Code Quality & Benchmarking Specification

> **Date:** February 16, 2026 | **Project:** QCanvas FYP-2

---

## Table of Contents

1. [Circuit Structural Quality Metrics](#1-circuit-structural-quality-metrics)
2. [Conversion Quality & Correctness](#2-conversion-quality--correctness)
3. [Simulation Benchmarking](#3-simulation-benchmarking)
4. [Cross-Framework Comparison](#4-cross-framework-comparison)
5. [Composite Quality Score](#5-composite-quality-score)
6. [Reference Benchmark Circuits](#6-reference-benchmark-circuits)
7. [Database Schema](#7-database-schema)
8. [Backend Implementation](#8-backend-implementation)
9. [API Endpoints](#9-api-endpoints)
10. [Frontend Dashboard](#10-frontend-dashboard-specifications)

---

## 1. Circuit Structural Quality Metrics

### 1.1 Gate Counts

| Metric | Formula | Description |
|--------|---------|-------------|
| **Total Gate Count** | `Σ gate_counts.values()` | Total operations in the circuit |
| **Single-Qubit Gates** | Count of `{H, X, Y, Z, S, Sdg, T, Tdg, Rx, Ry, Rz, U, U1, U2, U3, Phase, SX, ID}` | Low-noise operations |
| **Two-Qubit Gates** | Count of `{CNOT/CX, CZ, CY, SWAP, CH, CRX, CRY, CRZ, CP, iSWAP}` | Higher noise on real QPUs |
| **Multi-Qubit Gates** | Count of `{CCX/Toffoli, CSWAP/Fredkin, CCZ, MCX}` | Most expensive operations |
| **Measurement Gates** | Count of `{measure, measure_all}` | Readout operations |
| **Classical Gates** | Count of `{if, while, barrier, reset}` | Classical control flow |
| **T-Gate Count** | Count of `{T, Tdg}` | Key metric for fault-tolerant QC cost |

#### Gate Classification Code:

```python
SINGLE_QUBIT = {'h', 'x', 'y', 'z', 's', 'sdg', 't', 'tdg', 'rx', 'ry', 'rz',
                'u', 'u1', 'u2', 'u3', 'phase', 'sx', 'id'}
TWO_QUBIT = {'cx', 'cnot', 'cz', 'cy', 'swap', 'ch', 'crx', 'cry', 'crz', 'cp', 'iswap'}
MULTI_QUBIT = {'ccx', 'toffoli', 'cswap', 'fredkin', 'ccz', 'mcx'}
MEASURE = {'measure', 'measure_all'}

def classify_gates(gate_counts: dict) -> dict:
    return {
        "single_qubit": sum(v for k, v in gate_counts.items() if k.lower() in SINGLE_QUBIT),
        "two_qubit": sum(v for k, v in gate_counts.items() if k.lower() in TWO_QUBIT),
        "multi_qubit": sum(v for k, v in gate_counts.items() if k.lower() in MULTI_QUBIT),
        "measurement": sum(v for k, v in gate_counts.items() if k.lower() in MEASURE),
        "total": sum(gate_counts.values()),
        "unique_types": len(gate_counts),
    }
```

### 1.2 Ratio Metrics

| Metric | Formula | Ideal Value | Interpretation |
|--------|---------|-------------|----------------|
| **Gate-to-Qubit Ratio** | `total_gates / n_qubits` | 1–5 for simple circuits | Higher = more operations per qubit |
| **Depth-to-Qubit Ratio** | `depth / n_qubits` | ≤ 2 = highly parallel | Lower = better parallelism |
| **Two-Qubit Gate Ratio** | `two_qubit_gates / total_gates` | < 0.3 | Lower = less noise on real hardware |
| **Entanglement Ratio** | `(two_qubit + multi_qubit) / total_gates` | Context-dependent | Higher = more "quantum" behavior |
| **Gate Diversity Index** | `unique_gate_types / total_gates` | 0.1–0.3 typical | Higher = more varied operations |
| **Measurement Density** | `measurement_gates / total_gates` | < 0.2 | Low = mostly computation |
| **Spacetime Volume** | `n_qubits × depth` | Minimize | Total circuit resource usage |

### 1.3 Circuit Complexity Classification

| Level | Qubits | Gates | Depth | Label |
|-------|--------|-------|-------|-------|
| 1 | 1–2 | 1–5 | 1–3 | Trivial |
| 2 | 2–4 | 5–15 | 3–8 | Simple |
| 3 | 4–8 | 15–50 | 8–20 | Moderate |
| 4 | 8–15 | 50–200 | 20–50 | Complex |
| 5 | 15+ | 200+ | 50+ | Advanced |

---

## 2. Conversion Quality & Correctness

### 2.1 Structural Preservation Metrics

| Metric | Formula | Perfect Score |
|--------|---------|---------------|
| **Gate Count Preservation** | `output_gates / input_gates` | 1.0 |
| **Depth Preservation** | `output_depth / input_depth` | 1.0 |
| **Qubit Preservation** | `output_qubits / input_qubits` | 1.0 |
| **Decomposition Overhead** | `(output_gates − input_gates) / input_gates × 100` | 0% |
| **QASM Code Size** | `len(output_qasm.splitlines())` | N/A |

### 2.2 Semantic Equivalence

Compare measurement probability distributions from source and converted circuits:

```python
import math

def hellinger_distance(p: dict, q: dict, shots: int) -> float:
    """0 = identical distributions, 1 = completely different."""
    all_states = set(p.keys()) | set(q.keys())
    p_norm = {s: p.get(s, 0) / shots for s in all_states}
    q_norm = {s: q.get(s, 0) / shots for s in all_states}
    return math.sqrt(
        sum((math.sqrt(p_norm[s]) - math.sqrt(q_norm[s]))**2 for s in all_states)
    ) / math.sqrt(2)

def total_variation_distance(p: dict, q: dict, shots: int) -> float:
    """0 = identical, 1 = completely different."""
    all_states = set(p.keys()) | set(q.keys())
    return 0.5 * sum(abs(p.get(s,0)/shots - q.get(s,0)/shots) for s in all_states)

def semantic_equivalence_score(source_counts, converted_counts, shots=1024):
    hd = hellinger_distance(source_counts, converted_counts, shots)
    tvd = total_variation_distance(source_counts, converted_counts, shots)
    return {
        "hellinger_distance": round(hd, 4),
        "total_variation": round(tvd, 4),
        "equivalence_score": round(1 - hd, 4),  # 1.0 = perfect
        "is_equivalent": hd < 0.05,
    }
```

### 2.3 Roundtrip Consistency

```
Qiskit    → QASM → Qiskit    → QASM  (compare QASM₁ vs QASM₂)
Cirq      → QASM → Cirq      → QASM  (compare QASM₁ vs QASM₂)
PennyLane → QASM → PennyLane → QASM  (compare QASM₁ vs QASM₂)
```

| Check | Method | Pass Criteria |
|-------|--------|---------------|
| Code match | Normalized string compare | Identical after whitespace normalization |
| Gate count match | Compare `gate_counts` dicts | Identical dictionaries |
| Output match | Compare simulation results | Hellinger distance < 0.05 |

### 2.4 Syntax Validity

```python
def validate_qasm(qasm_code: str) -> dict:
    try:
        from openqasm3 import parse
        ast = parse(qasm_code)
        return {"valid": True, "errors": [], "warnings": []}
    except Exception as e:
        return {"valid": False, "errors": [str(e)], "warnings": []}
```

---

## 3. Simulation Benchmarking

### 3.1 Performance Metrics

| Metric | Formula | Unit | Source |
|--------|---------|------|--------|
| **Execution Time** | Direct | ms | `SimulationResult.execution_time` |
| **Time per Shot** | `exec_time_ms / shots` | ms/shot | Computed |
| **Time per Qubit** | `exec_time_ms / n_qubits` | ms/qubit | Computed |
| **Memory Usage** | Direct | MB | `SimulationResult.memory_usage` |
| **Memory per Qubit** | `memory_mb / n_qubits` | MB/qubit | Computed |
| **CPU Usage** | Direct | % | `SimulationResult.cpu_usage` |
| **Fidelity** | `successful / total × 100` | % | `SimulationResult.fidelity` |
| **Throughput** | `jobs / time_window` | jobs/min | Aggregated |
| **P50/P95/P99 Latency** | Percentiles of `exec_time_ms` | ms | Aggregated |

### 3.2 Output Distribution Metrics

| Metric | Formula | What It Reveals |
|--------|---------|-----------------|
| **Shannon Entropy** | `−Σ p(x) log₂ p(x)` | Randomness (max = n_qubits bits) |
| **Dominant State** | `argmax(probabilities)` | Most likely outcome |
| **Dominant Probability** | `max(probabilities)` | How peaked the distribution is |
| **Effective States** | States with `p > 0.01` | Significant outcomes |
| **Uniformity Score** | `entropy / max_entropy` | 1.0 = perfectly uniform |

```python
import math

def output_distribution_metrics(probabilities: dict, n_qubits: int) -> dict:
    max_entropy = n_qubits
    entropy = -sum(p * math.log2(p) for p in probabilities.values() if p > 0)
    dominant_state = max(probabilities, key=probabilities.get)
    effective_states = sum(1 for p in probabilities.values() if p > 0.01)
    return {
        "shannon_entropy": round(entropy, 4),
        "max_entropy": max_entropy,
        "uniformity_score": round(entropy / max_entropy, 4) if max_entropy > 0 else 0,
        "dominant_state": dominant_state,
        "dominant_probability": round(probabilities[dominant_state], 4),
        "effective_states": effective_states,
        "total_possible_states": 2 ** n_qubits,
    }
```

### 3.3 Backend Comparison Matrix

| Backend | Best For | Memory Scaling | Speed |
|---------|----------|----------------|-------|
| **Statevector** | Exact amplitudes, ≤25 qubits | O(2ⁿ) | Medium |
| **Density Matrix** | Noise simulation, mixed states | O(4ⁿ) | Slow |
| **Stabilizer** | Clifford-only circuits | O(n²) | Very Fast |

### 3.4 Scaling Benchmark: Record at Increasing Qubit Counts

| Qubits | State Space | Statevector (ms) | Density Matrix (ms) | Stabilizer (ms) | Memory (MB) |
|--------|-------------|-------------------|---------------------|------------------|-------------|
| 2 | 4 | — | — | — | — |
| 5 | 32 | — | — | — | — |
| 10 | 1,024 | — | — | — | — |
| 15 | 32,768 | — | — | — | — |
| 20 | 1,048,576 | — | — | — | — |
| 25 | 33,554,432 | — | — | — | — |

---

## 4. Cross-Framework Comparison

### 4.1 Per-Circuit Benchmark Report

```
┌─────────────────────────┬──────────┬──────────┬─────────────┐
│ Metric                  │ Qiskit   │ Cirq     │ PennyLane   │
├─────────────────────────┼──────────┼──────────┼─────────────┤
│ Conversion Time (ms)    │          │          │             │
│ Output Gate Count       │          │          │             │
│ Output Depth            │          │          │             │
│ QASM Lines Generated    │          │          │             │
│ Gate Overhead (%)       │          │          │             │
│ Semantic Equiv. Score   │          │          │             │
│ Syntax Validity         │          │          │             │
│ Roundtrip Consistent    │          │          │             │
└─────────────────────────┴──────────┴──────────┴─────────────┘
```

### 4.2 Error Distribution per Framework

| Error Category | Description | Track Key |
|----------------|-------------|-----------|
| Parse Error | Failed to parse source code | `error_type = 'parse'` |
| Unsupported Gate | Gate not in target set | `error_type = 'unsupported_gate'` |
| Type Mismatch | Data type incompatibility | `error_type = 'type_error'` |
| Decomposition Failure | Cannot decompose to primitives | `error_type = 'decomposition'` |
| Syntax Error | Generated QASM is invalid | `error_type = 'syntax'` |

---

## 5. Composite Quality Score (0–100)

### 5.1 Formula

```
QualityScore = 25 × Structure + 30 × Efficiency + 30 × Correctness + 15 × Performance
```

### 5.2 Component Breakdown

| Component | Weight | Sub-metrics (weights) |
|-----------|--------|-----------------------|
| **Structure** | 25% | Gate Diversity (40%), Has Measurements (30%), Entanglement Ratio (30%) |
| **Efficiency** | 30% | Gate/Qubit Ratio (40%), Depth/Qubit Ratio (30%), Two-Qubit Ratio (30%) |
| **Correctness** | 30% | Semantic Equivalence (50%), Syntax Validity (30%), Roundtrip (20%) |
| **Performance** | 15% | Execution Time normalized to 5s baseline (100%) |

### 5.3 Complete Scoring Function

```python
def compute_quality_score(metrics: dict) -> dict:
    # Structure (0-25)
    structure = 25 * (
        0.4 * min(metrics['gate_diversity_index'], 1.0) +
        0.3 * (1.0 if metrics['has_measurements'] else 0.5) +
        0.3 * min(metrics['entanglement_ratio'] * 2, 1.0)
    )
    # Efficiency (0-30)
    efficiency = 30 * (
        0.4 * max(0, 1.0 - metrics['gate_to_qubit_ratio'] / 20) +
        0.3 * max(0, 1.0 - metrics['depth_to_qubit_ratio'] / 10) +
        0.3 * max(0, 1.0 - metrics['two_qubit_ratio'])
    )
    # Correctness (0-30)
    correctness = 30 * (
        0.5 * metrics.get('semantic_equivalence', 1.0) +
        0.3 * (1.0 if metrics.get('syntax_valid', True) else 0.0) +
        0.2 * (1.0 if metrics.get('roundtrip_consistent', True) else 0.0)
    )
    # Performance (0-15)
    performance = 15 * max(0, 1.0 - metrics.get('exec_time_ms', 0) / 5000)

    total = round(structure + efficiency + correctness + performance, 1)
    grade = "A+" if total >= 90 else "A" if total >= 80 else "B" if total >= 70 else "C" if total >= 60 else "D"

    return {
        "structure_score": round(structure, 1),
        "efficiency_score": round(efficiency, 1),
        "correctness_score": round(correctness, 1),
        "performance_score": round(performance, 1),
        "total_quality_score": total,
        "quality_grade": grade,
    }
```

### 5.4 Grade Scale

| Score | Grade | Color | Description |
|-------|-------|-------|-------------|
| 90–100 | A+ | 🟢 | QPU-ready, highly optimized |
| 80–89 | A | 🟢 | Well-structured, minor tweaks |
| 70–79 | B | 🟡 | Good, some inefficiencies |
| 60–69 | C | 🟠 | Fair, needs optimization |
| < 60 | D | 🔴 | Needs significant improvement |

---

## 6. Reference Benchmark Circuits

| # | Circuit | Qubits | Gates | Depth | Purpose |
|---|---------|--------|-------|-------|---------|
| 1 | **Bell State** | 2 | 2 | 2 | Baseline entanglement |
| 2 | **GHZ State** | 3–10 | N | N | Scalable entanglement |
| 3 | **QFT** | 4–8 | O(n²) | O(n²) | Multi-qubit algorithm |
| 4 | **Grover's Search** | 3–5 | ~20–80 | ~15–40 | Oracle + diffusion |
| 5 | **VQE Ansatz** | 4–6 | ~30–60 | ~20–30 | Variational circuit |
| 6 | **Random Circuit** | 5–15 | ~50–200 | ~20–80 | Stress test |
| 7 | **Bernstein-Vazirani** | 4–8 | O(n) | O(1) | Oracle-based |
| 8 | **QAOA** | 4–8 | ~40–100 | ~20–40 | Optimization |
| 9 | **Teleportation** | 3 | 7 | 5 | Classical control flow |
| 10 | **Repetition Code** | 5–9 | ~15–30 | ~10–15 | Error correction |

---

## 7. Database Schema

### 7.1 `circuit_quality_metrics`

```sql
CREATE TABLE circuit_quality_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversion_id UUID REFERENCES conversions(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    -- Gate Classification
    single_qubit_gates INTEGER DEFAULT 0,
    two_qubit_gates INTEGER DEFAULT 0,
    multi_qubit_gates INTEGER DEFAULT 0,
    measurement_gates INTEGER DEFAULT 0,
    total_gates INTEGER DEFAULT 0,
    unique_gate_types INTEGER DEFAULT 0,
    t_gate_count INTEGER DEFAULT 0,
    gate_counts_json JSONB,
    -- Ratios
    gate_to_qubit_ratio FLOAT,
    depth_to_qubit_ratio FLOAT,
    two_qubit_ratio FLOAT,
    entanglement_ratio FLOAT,
    gate_diversity_index FLOAT,
    measurement_density FLOAT,
    spacetime_volume INTEGER,
    -- Complexity
    complexity_level INTEGER CHECK (complexity_level BETWEEN 1 AND 5),
    complexity_label VARCHAR(20),
    -- Quality Score
    structure_score FLOAT,
    efficiency_score FLOAT,
    correctness_score FLOAT,
    performance_score FLOAT,
    total_quality_score FLOAT,
    quality_grade VARCHAR(2),
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_quality_user ON circuit_quality_metrics(user_id);
CREATE INDEX idx_quality_score ON circuit_quality_metrics(total_quality_score);
```

### 7.2 `simulation_benchmarks`

```sql
CREATE TABLE simulation_benchmarks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    n_qubits INTEGER NOT NULL,
    total_gates INTEGER NOT NULL,
    circuit_depth INTEGER NOT NULL,
    backend VARCHAR(30) NOT NULL,
    shots INTEGER NOT NULL,
    execution_time_ms FLOAT NOT NULL,
    time_per_shot_ms FLOAT,
    time_per_qubit_ms FLOAT,
    memory_usage_mb FLOAT,
    fidelity FLOAT,
    shannon_entropy FLOAT,
    uniformity_score FLOAT,
    dominant_state VARCHAR(50),
    dominant_probability FLOAT,
    effective_states INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_bench_backend ON simulation_benchmarks(backend);
CREATE INDEX idx_bench_qubits ON simulation_benchmarks(n_qubits);
```

### 7.3 `conversion_benchmarks`

```sql
CREATE TABLE conversion_benchmarks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversion_id UUID REFERENCES conversions(id) ON DELETE CASCADE,
    input_gates INTEGER,
    output_gates INTEGER,
    gate_count_preservation FLOAT,
    input_depth INTEGER,
    output_depth INTEGER,
    depth_preservation FLOAT,
    decomposition_overhead_pct FLOAT,
    qasm_line_count INTEGER,
    syntax_valid BOOLEAN DEFAULT TRUE,
    semantic_equivalence_score FLOAT,
    hellinger_distance FLOAT,
    roundtrip_consistent BOOLEAN,
    conversion_time_ms FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 8. Backend Implementation

### 8.1 SQLAlchemy Model (`backend/app/models/quality_metrics.py`)

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Boolean, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.config.database import Base

class CircuitQualityMetrics(Base):
    __tablename__ = "circuit_quality_metrics"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversion_id = Column(UUID(as_uuid=True), ForeignKey("conversions.id", ondelete="CASCADE"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    single_qubit_gates = Column(Integer, default=0)
    two_qubit_gates = Column(Integer, default=0)
    multi_qubit_gates = Column(Integer, default=0)
    measurement_gates = Column(Integer, default=0)
    total_gates = Column(Integer, default=0)
    unique_gate_types = Column(Integer, default=0)
    t_gate_count = Column(Integer, default=0)
    gate_counts_json = Column(JSON)
    gate_to_qubit_ratio = Column(Float)
    depth_to_qubit_ratio = Column(Float)
    two_qubit_ratio = Column(Float)
    entanglement_ratio = Column(Float)
    gate_diversity_index = Column(Float)
    measurement_density = Column(Float)
    spacetime_volume = Column(Integer)
    complexity_level = Column(Integer)
    complexity_label = Column(String(20))
    structure_score = Column(Float)
    efficiency_score = Column(Float)
    correctness_score = Column(Float)
    performance_score = Column(Float)
    total_quality_score = Column(Float)
    quality_grade = Column(String(2))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class SimulationBenchmark(Base):
    __tablename__ = "simulation_benchmarks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    n_qubits = Column(Integer, nullable=False)
    total_gates = Column(Integer, nullable=False)
    circuit_depth = Column(Integer, nullable=False)
    backend = Column(String(30), nullable=False)
    shots = Column(Integer, nullable=False)
    execution_time_ms = Column(Float, nullable=False)
    time_per_shot_ms = Column(Float)
    time_per_qubit_ms = Column(Float)
    memory_usage_mb = Column(Float)
    fidelity = Column(Float)
    shannon_entropy = Column(Float)
    uniformity_score = Column(Float)
    dominant_state = Column(String(50))
    dominant_probability = Column(Float)
    effective_states = Column(Integer)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
```

### 8.2 Quality Service (`backend/app/services/quality_service.py`)

```python
import math
from typing import Dict, Any

class QualityService:
    SINGLE_QUBIT = {'h','x','y','z','s','sdg','t','tdg','rx','ry','rz',
                    'u','u1','u2','u3','phase','sx','id'}
    TWO_QUBIT = {'cx','cnot','cz','cy','swap','ch','crx','cry','crz','cp','iswap'}
    MULTI_QUBIT = {'ccx','toffoli','cswap','fredkin','ccz','mcx'}
    MEASURE = {'measure','measure_all'}

    @staticmethod
    def analyze_circuit(gate_counts: dict, n_qubits: int, depth: int,
                        exec_time_ms: float = 0, probabilities: dict = None) -> dict:
        classified = QualityService._classify_gates(gate_counts)
        ratios = QualityService._compute_ratios(classified, n_qubits, depth)
        complexity = QualityService._classify_complexity(n_qubits, classified["total"], depth)
        score = QualityService._compute_quality_score(
            classified, ratios, exec_time_ms=exec_time_ms
        )
        result = {**classified, **ratios, **complexity, **score}
        if probabilities:
            result.update(QualityService._output_metrics(probabilities, n_qubits))
        return result

    @staticmethod
    def _classify_gates(gc: dict) -> dict:
        sq = sum(v for k, v in gc.items() if k.lower() in QualityService.SINGLE_QUBIT)
        tq = sum(v for k, v in gc.items() if k.lower() in QualityService.TWO_QUBIT)
        mq = sum(v for k, v in gc.items() if k.lower() in QualityService.MULTI_QUBIT)
        ms = sum(v for k, v in gc.items() if k.lower() in QualityService.MEASURE)
        tg = sum(v for k, v in gc.items() if k.lower() in {'t', 'tdg'})
        return {
            "single_qubit_gates": sq, "two_qubit_gates": tq,
            "multi_qubit_gates": mq, "measurement_gates": ms,
            "total_gates": sum(gc.values()), "unique_gate_types": len(gc),
            "t_gate_count": tg,
        }

    @staticmethod
    def _compute_ratios(c: dict, n_qubits: int, depth: int) -> dict:
        total = c["total"] or 1
        nq = max(n_qubits, 1)
        return {
            "gate_to_qubit_ratio": round(total / nq, 4),
            "depth_to_qubit_ratio": round(depth / nq, 4),
            "two_qubit_ratio": round(c["two_qubit_gates"] / total, 4),
            "entanglement_ratio": round((c["two_qubit_gates"] + c["multi_qubit_gates"]) / total, 4),
            "gate_diversity_index": round(c["unique_gate_types"] / total, 4),
            "measurement_density": round(c["measurement_gates"] / total, 4),
            "spacetime_volume": n_qubits * depth,
        }

    @staticmethod
    def _classify_complexity(qubits, gates, depth) -> dict:
        if qubits <= 2 and gates <= 5:   return {"complexity_level": 1, "complexity_label": "Trivial"}
        if qubits <= 4 and gates <= 15:  return {"complexity_level": 2, "complexity_label": "Simple"}
        if qubits <= 8 and gates <= 50:  return {"complexity_level": 3, "complexity_label": "Moderate"}
        if qubits <= 15 and gates <= 200:return {"complexity_level": 4, "complexity_label": "Complex"}
        return {"complexity_level": 5, "complexity_label": "Advanced"}

    @staticmethod
    def _compute_quality_score(classified, ratios, exec_time_ms=0,
                                semantic_eq=1.0, syntax_valid=True, roundtrip=True) -> dict:
        has_meas = classified["measurement_gates"] > 0
        structure = 25 * (0.4*min(ratios["gate_diversity_index"],1) +
                         0.3*(1 if has_meas else 0.5) +
                         0.3*min(ratios["entanglement_ratio"]*2,1))
        efficiency = 30 * (0.4*max(0,1-ratios["gate_to_qubit_ratio"]/20) +
                          0.3*max(0,1-ratios["depth_to_qubit_ratio"]/10) +
                          0.3*max(0,1-ratios["two_qubit_ratio"]))
        correctness = 30 * (0.5*semantic_eq + 0.3*(1 if syntax_valid else 0) + 0.2*(1 if roundtrip else 0))
        performance = 15 * max(0, 1 - exec_time_ms / 5000)
        total = round(structure + efficiency + correctness + performance, 1)
        grade = "A+" if total>=90 else "A" if total>=80 else "B" if total>=70 else "C" if total>=60 else "D"
        return {"structure_score": round(structure,1), "efficiency_score": round(efficiency,1),
                "correctness_score": round(correctness,1), "performance_score": round(performance,1),
                "total_quality_score": total, "quality_grade": grade}

    @staticmethod
    def _output_metrics(probs: dict, n_qubits: int) -> dict:
        max_ent = n_qubits
        entropy = -sum(p * math.log2(p) for p in probs.values() if p > 0)
        dom = max(probs, key=probs.get)
        return {
            "shannon_entropy": round(entropy, 4),
            "uniformity_score": round(entropy/max_ent, 4) if max_ent > 0 else 0,
            "dominant_state": dom,
            "dominant_probability": round(probs[dom], 4),
            "effective_states": sum(1 for p in probs.values() if p > 0.01),
        }
```

---

## 9. API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/quality/circuit/{conversion_id}` | Full quality analysis for a conversion |
| `GET` | `/api/quality/user/{user_id}/summary` | User's avg quality score and trends |
| `GET` | `/api/quality/leaderboard` | Top users by avg quality score |
| `GET` | `/api/quality/benchmarks` | Platform-wide benchmark statistics |
| `GET` | `/api/quality/benchmarks/scaling` | Qubit scaling performance data |
| `GET` | `/api/quality/frameworks/compare` | Cross-framework quality comparison |
| `POST` | `/api/quality/analyze` | Ad-hoc circuit quality analysis |

---

## 10. Frontend Dashboard Specifications

### 10.1 Quality Report Card (per circuit)

| Widget | Visual Type | Data Source |
|--------|-------------|-------------|
| Score Badge | Circular gauge (0–100) + grade letter | `total_quality_score`, `quality_grade` |
| Score Breakdown | 4-segment horizontal bar | structure, efficiency, correctness, performance |
| Gate Distribution | Donut chart | single vs two vs multi vs measurement |
| Circuit Stats | Stat cards row | qubits, depth, total gates, spacetime volume |
| Key Ratios | 4 mini gauges | gate/qubit, depth/qubit, 2Q ratio, entanglement |
| Complexity Badge | Colored pill | Level 1–5 with label |

### 10.2 Analytics Dashboard (admin/aggregate)

| Widget | Type | Shows |
|--------|------|-------|
| Avg Quality Trend | Line chart (30 days) | Quality score over time |
| Framework Comparison | Grouped bar chart | Qiskit vs Cirq vs PennyLane |
| Complexity Distribution | Histogram | Level 1–5 circuit counts |
| Top Circuits | Table | Highest-scoring circuits |
| Backend Performance | Multi-line chart | Exec time by backend vs qubits |
| Gate Type Heatmap | Heatmap | Gate usage by framework |
| Output Entropy Distribution | Histogram | Shannon entropy distribution |
