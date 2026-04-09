# Quantum Volume (QV) Estimation in QCanvas

This document explains the logic, mathematics, and interpretation of the **Quantum Volume (QV)** metric used in the Paper 5 benchmarking suite.

---

## 1. What is Quantum Volume?

Originally proposed by IBM, **Quantum Volume** is a holistic metric designed to measure the capabilities and error rates of a quantum computer. It combines several factors—qubit count, gate error rates, connectivity, and measurement errors—into a single number: $2^m$.

A system has a Quantum Volume of $2^m$ if it can successfully execute a "square" circuit of width $m$ (qubits) and depth $m$ (gate layers) with a heavy output probability greater than $2/3$.

## 2. "Effective QV" for Compilation Benchmarking

In the QCanvas project, we use an **Effective QV** metric. Since we are simulating ideal circuits, we use QV as a proxy for **compilation efficiency** rather than hardware quality.

### The Question we ask:

> "What is the largest **square circuit** (m × m qubits and depth) that can be executed under the assumed noise model with fidelity > 50%?"

By computing the QV achievable under representative hardware noise parameters (regardless of actual compiled circuit structure), we can objectively rank compilers:

- Circuits produced by frameworks serve as **reference points** for complexity
- Higher effective QV means the framework's output is more efficient and hardware-ready

### Key Insight:

The **quantum volume is independent of actual circuit structure**—it's a hardware capability metric. The actual circuit's fidelity is reported separately as `actual_fidelity`.

For benchmarking, by fixing noise parameters and comparing QV across frameworks, we establish a baseline capability level for NISQ devices.

---

## 3. Mathematical Noise Model

The estimation uses a depolarizing noise model combined with $T_1$ relaxation effects.

### A. Fidelity Model

For a circuit with $n$ qubits and $d$ depth layers, the estimated fidelity ($F$) is:
$$F = F_{gate} \times F_{T1}$$

1. **Gate Fidelity ($F_{gate}$):**
   Estimates error accumulation per two-qubit gate layer (assuming $d/2$ layers contain 2Q gates).
   $$F_{gate} = (1 - \epsilon)^{(d/2 \times n)}$$
   _Default $\epsilon = 0.01$ (1% error)._

2. **$T_1$ Fidelity ($F_{T1}$):**
   Estimates decay over time (decoherence).
   $$F_{T1} = \exp\left(-\frac{d \times t_{gate}}{T_1}\right)$$
   _Default $T_1 = 100 \mu s$, $t_{gate} = 50 ns$._

### B. Estimation Algorithm

To find the **Effective QV Log2** ($m$):

1. Start with width $m = 1$.
2. Calculate $F(m, m)$ — fidelity of a **square circuit** (m qubits, m depth layers).
3. Increment $m$ until $F < 0.5$.
4. **Result:** $Effective\_QV = 2^{m-1}$.

---

## 4. Interpretation Guide & Realistic Values

The Effective QV is a **fixed hardware capability metric** (independent of circuit structure). It represents the largest square circuit the device can reliably execute.

### Expected QV Ranges (Default Noise Model: 1% gate error, 100 μs T1, 50 ns 2Q gates)

| QV Range            | m (log2) | Use Case                                                           |
| :------------------ | :------- | :----------------------------------------------------------------- |
| $2^{15}$ – $2^{20}$ | 15–20    | Shallow NISQ algorithms (Bell state, simple preparations)          |
| $2^{10}$ – $2^{14}$ | 10–14    | Medium circuits (Grover's, VQE ansatz)                             |
| $2^{5}$ – $2^{9}$   | 5–9      | Deeper circuits (iterative refinement, multiple entangling layers) |
| $2^{1}$ – $2^{4}$   | 1–4      | Very deep circuits (10+ layers); limited fault-tolerance           |

### Example: Circuit Depth vs. Actual Fidelity

| Circuit         | Width | Depth | QV (Hardware Capability) | Actual Fidelity    |
| :-------------- | :---- | :---- | :----------------------- | :----------------- |
| **Bell State**  | 2     | 3     | $2^{18}$                 | 0.978 (excellent)  |
| **Grover (5Q)** | 5     | 15    | $2^{9}$                  | 0.720 (good)       |
| **Deep Ansatz** | 4     | 40    | $2^{4}$                  | 0.440 (borderline) |

---

## 5. Assumed Parameters (NISQ Baseline)

The script uses representative parameters for superconducting transmon qubits:

- **Gate Error Rate:** $1.0\%$
- **T1 Time:** $100 \mu s$
- **2Q Gate Time:** $50 ns$

_Note: These are estimates for relative comparison across frameworks, not measured hardware performance._
