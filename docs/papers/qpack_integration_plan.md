# QPack Integration Plan for Paper 5
## Cross-Framework Quantum Algorithm Benchmarking — QCanvas

> **Document type:** Comparative analysis + augmentation plan  
> **Source paper:** *"QPack Scores: Quantitative performance metrics for application-oriented quantum computer benchmarking"* – Donkers et al. (arXiv:2205.12142v1)  
> **Base document:** `paper5_implementation_guide.md`  
> **Date:** March 2026

---

## 1. Overview

The QPack paper provides a mature, peer-reviewed benchmarking framework based on **four quantitative sub-scores**: Runtime, Accuracy, Scalability, and Capacity.  
Paper 5 (our work) benchmarks **cross-framework structural and distributional equivalence** via a unified QASM 3.0 pipeline.

These two papers are **complementary, not competing**. QPack provides the benchmarking *score language*; Paper 5 provides the *compilation-level explanation* of why scores differ between frameworks.

The key insight: **QPack reveals THAT simulators differ; QCanvas reveals WHY (at the QASM level).**

---

## 2. Side-by-Side Comparison

| Dimension | Paper 5 (Current Plan) | QPack Paper | Gap / Opportunity |
|---|---|---|---|
| **Primary metric** | JSD + Chi-squared on distributions | `S_runtime`, `S_accuracy`, `S_scalability`, `S_capacity` composite scores | Paper 5 lacks a composite **single-number score** |
| **Algorithms** | 12 algorithms (fixed circuits) | 6 VQAs (QAOA×4, VQE×2), variational | Paper 5 could adopt QPack's **scalable problem-size** approach |
| **Framework comparison** | Qiskit vs. Cirq vs. PennyLane (QASM output) | Qiskit Aer vs. Cirq vs. Rigetti QVM vs. QuEST | QPack tests **hardware backends**; Paper 5 tests **source-language to QASM** |
| **Accuracy metric** | JSD against theoretical ideal | Relative error vs. QuEST noiseless baseline | QPack's accuracy formula is formalised — adopt it |
| **Runtime metric** | Compilation time + sim time (separate) | **Gates-per-second** (depth × shots / T_quantum) | QPack's runtime score normalises for circuit size — more fair |
| **Scalability** | Regression slope on gate count vs n | Exponential fit `T_Q(N) = N^a` → score from `a` | QPack's `a`-value quantifies scalability exactly |
| **Capacity metric** | Not currently present | Max qubits where relative error ≤ 20% | **Missing entirely from Paper 5 — high priority addition** |
| **QV estimation** | Structural QV estimate (depolarizing model) | Not covered | Paper 5's QV estimate is an **original contribution** |
| **Single overall score** | Not currently defined | `S = ½(S_runtime + S_scalability)(S_accuracy + S_capacity)` | Paper 5 should define an equivalent composite score |
| **Visualisation** | 14 figures (bar charts, heatmaps) | Radar plots + bar graph per device | Adopt **radar plots** for side-by-side framework comparison |

---

## 3. What QPack Adds That We Should Adopt

### 3.1 ✅ Formalised Runtime Score (adopt directly)

QPack defines runtime as **gates-per-second**, not raw time:

```
G_{P,N} = D_{P,N} × S_{P,N}          (gates per shot = depth × shots)
S_pure_runtime = (1 / (N_e - N_s)) × Σ G_{P,N} / T_Q_{P,N}
S_mapped_runtime = log10(S_pure_runtime)
```

**Why this is better than what we have now:**  
Raw compilation time unfairly punishes frameworks that produce deeper circuits (deeper QASM → longer to write to disk) *and* raw simulation time ignores that Grover's is inherently deeper than Bell State.  
Gates-per-second normalises for this: a framework that produces 20% more gates but runs 20% slower gets the *same* score. Only genuine efficiency differences appear.

**Action:** Add `S_runtime` computation to `benchmarks/scripts/statistical_tests.py` and `benchmarks/metrics/`.

---

### 3.2 ✅ Formalised Accuracy Score (adopt with modification)

QPack defines accuracy as:

```
S_pure_accuracy = (1/(N_e-N_s)) × Σ |E_ideal - E_Q| / |E_ideal|
S_mapped_accuracy = c0 × (2/π) × arctan(c1 × S_pure_accuracy)
  where c0 = 30/π, c1 = 50
```

QPack uses the **QuEST noiseless simulator** as the ideal baseline.  
For Paper 5, our ideal baseline is the **theoretical distribution** (e.g., exactly 50/50 for Bell State). For variational circuits (VQE/QAOA), we can use noiseless QSim output.

**Modification for Paper 5:**
- For deterministic algorithms (Bell, GHZ, Grover's, BV, DJ, QRNG): use the **theoretical ideal distribution**
- For variational algorithms (VQE, QAOA): use **noiseless QSim statevector output** as the ideal

**Action:** Replace raw JSD with `S_accuracy` as the primary per-algorithm accuracy metric. Keep JSD as a supplementary metric.

---

### 3.3 ✅ Formalised Scalability Score (adopt directly)

QPack fits `T_Q(N) = N^a` and uses `a` as the scalability score:

```
S_pure_scalability = a     (exponent of power-law fit)
S_mapped_scalability = c2 × (2/π) × arctan(c3 × (a - 1))
  where c2 = 30/π, c3 = 0.75
```

- `a = 1` → linear scaling (ideal)  
- `a > 1` → worse-than-linear (concerning for larger circuits)  
- `a < 1` → sub-linear (excellent)  

**For Paper 5:** Apply this to **gate count vs. n_qubits** (rather than runtime vs. problem size), since we are studying structural scaling. This fits our RQ4 directly.

**Action:** Add power-law fit and `a`-value computation to `benchmarks/scripts/statistical_tests.py`.

---

### 3.4 🆕 Capacity Score (not in current plan — add it)

This is the most important missing metric. QPack defines Capacity as:

```
S_capacity = max { Q_N  where  |E_ideal - E_Q| / |E_ideal|  ≤  A }
```
where `A = 0.20` (20% relative accuracy threshold).

**For Paper 5:** Capacity measures **the largest qubit count at which a framework's compiled QASM still produces distributions within 20% JSD of the ideal**. This is the "usable scale" of each framework's compilation.

| Framework | Expected Capacity-equivalent |
|---|---|
| Qiskit | High (clean CNOT decompositions) |
| Cirq | High (moment-based, minimal overhead) |
| PennyLane | Potentially lower (template overhead at scale) |

**Action:** Add `S_capacity` computation using JSD threshold (JSD < 0.05 equivalent) in `benchmarks/scripts/`.

---

### 3.5 🆕 QPack-Style Overall Composite Score (new addition)

QPack combines sub-scores as:

```
S_overall = ½ × (S_runtime + S_scalability) × (S_accuracy + S_capacity)
```

This elegant formula gives an **area of a quadrilateral in radar-plot space**, meaning it rewards balanced performance across all four dimensions. A framework that excels in only one dimension will not dominate.

**For Paper 5:** Adapt this to our framework comparison context:

```
S_overall_framework = ½ × (S_compile_speed + S_scalability) × (S_accuracy + S_capacity)

where:
  S_compile_speed  = log10(mean_gates_per_second over all algorithms)
  S_scalability    = mapped scalability exponent a (power-law on gate count)
  S_accuracy       = mapped relative error vs. ideal distribution
  S_capacity       = largest n_qubits where JSD < 0.05 threshold
```

This gives one number per framework (Qiskit, Cirq, PennyLane), enabling a **headline result** for the paper.

**Action:** Define and compute `S_overall` in `benchmarks/notebooks/nb06_results_tables.ipynb` and add a radar plot as Fig. 15.

---

### 3.6 ✅ Radar Plot Visualisation (add as Fig. 15)

QPack uses a radar/spider plot to visualise all four sub-scores simultaneously per device. This is excellent for the paper — one figure shows everything.

**For Paper 5:**
```
Radar Plot Axes:  [S_compile_speed, S_scalability, S_accuracy, S_capacity]
One trace per framework: Qiskit (purple), Cirq (teal), PennyLane (orange)
```

**Action:** Add `plot_radar()` function to `benchmarks/scripts/figure_styles.py` and produce Fig. 15 in `nb05_figures.ipynb`.

---

## 4. What QPack Does That We Should NOT Copy

| QPack Feature | Reason Not to Copy |
|---|---|
| LibKet cross-platform execution | QCanvas is our own cross-platform engine — highlighting it is our original contribution |
| Random Erdős-Rényi graphs (Atos Q-score style) | Our algorithms are deterministic and reproducible — better for controlled comparison |
| Classical optimizer iterations as a metric | We don't run full VQA optimisation loops; we compile fixed circuits |
| Hardware queue time / serviceability | Paper 5 is about the compilation pipeline, not cloud provider latency |
| COBYLA optimizer | Not relevant — we fix VQE/QAOA parameters to make QASM deterministic |

---

## 5. What Paper 5 Contributes That QPack Does NOT Have

| Paper 5 Original Contribution | Description |
|---|---|
| **QASM 3.0 structural diff** | QPack never inspects the compiled QASM — we do. Gate-level divergence across frameworks is novel. |
| **Source-language attribution** | QPack compares backends; we compare *source frameworks*. Same algorithm, three source languages → three QASM outputs. |
| **Quantum Volume per circuit** | QPack doesn't estimate QV per compiled circuit. Our QV-vs-depth scatter (Fig. 12) is original. |
| **QASM 3.0 modifier usage** | `ctrl@`, `inv@`, `pow()` — QPack never looks at this. QASM 3.0 expressiveness is our unique angle. |
| **JSD-based distribution equivalence** | QPack uses relative error to a baseline. JSD is a stricter, information-theoretic equivalence test. |

---

## 6. Revised Paper 5 Metrics Table

After integrating QPack insights, the complete metric set for Paper 5 becomes:

### 6.1 Structural Metrics (from QASM analysis — no simulation needed)
| Metric | Description | Where computed |
|---|---|---|
| Total gate count | Number of gate invocations in QASM | `analyze_qasm.py` → `structural_metrics.csv` |
| Circuit depth | Critical path length | `analyze_qasm.py` |
| Multi-qubit gate ratio | 2Q gates / total gates | `analyze_qasm.py` |
| Gate type breakdown | H, CNOT, RZ, RX, RY counts | `analyze_qasm.py` |
| QASM 3.0 modifier count | `ctrl@`, `inv@`, `pow()` usage | `analyze_qasm.py` |
| Compilation time (ms) | 10 repeats, mean ± std | `compile_all.py` |
| **Effective QV estimate** | **Depolarizing noise model** | **`quantum_volume.py`** |
| **Scalability exponent `a`** | **Power-law fit: gates ~ N^a** | **`statistical_tests.py`** |

### 6.2 Simulation / Distribution Metrics (from QSim runs)
| Metric | Description | Where computed |
|---|---|---|
| Simulation time (ms) | 10 repeats × 3 shot counts | `simulate_all.py` |
| Peak memory (MB) | `tracemalloc` | `simulate_all.py` |
| Measurement distribution | Counts per bitstring | `simulate_all.py` |
| Jensen-Shannon Divergence | Pairwise per algorithm | `statistical_tests.py` |
| Chi-squared p-value | vs. theoretical ideal | `statistical_tests.py` |
| **S_accuracy (QPack-adapted)** | **Relative error vs. ideal, arctan-mapped** | **`statistical_tests.py`** |
| **S_capacity (QPack-adapted)** | **Largest n where JSD < 0.05** | **`statistical_tests.py`** |

### 6.3 Composite Scores (per framework, over all algorithms)
| Score | Formula | Where computed |
|---|---|---|
| **S_compile_speed** | `log10(mean gates-per-second)` | `nb06_results_tables.ipynb` |
| **S_scalability** | `arctan-mapped exponent a` | `nb06_results_tables.ipynb` |
| **S_accuracy** | `arctan-mapped mean relative error` | `nb06_results_tables.ipynb` |
| **S_capacity** | `max n where JSD < 0.05` | `nb06_results_tables.ipynb` |
| **S_overall** | `½(S_speed + S_scale)(S_acc + S_cap)` | `nb06_results_tables.ipynb` |

---

## 7. Changes to Existing Files

### 7.1 `benchmarks/scripts/statistical_tests.py`
Add the following functions (all currently TODO):
- `compute_runtime_score(gates_per_second_list)` → `S_mapped_runtime`
- `compute_accuracy_score(relative_errors)` → `S_mapped_accuracy`
- `fit_power_law(n_qubits, gate_counts)` → returns exponent `a`
- `compute_scalability_score(a)` → `S_mapped_scalability`  
- `compute_capacity_score(jsd_by_nqubits, threshold=0.05)` → `S_capacity`
- `compute_overall_score(S_speed, S_scale, S_acc, S_cap)` → `S_overall`

### 7.2 `benchmarks/notebooks/nb03_statistical_analysis.ipynb`
Add cells for:
- Power-law scaling fit (`a`-value) with plot
- `S_accuracy` computed per algorithm per framework
- `S_capacity` computed for variable-qubit algorithms
- Comparison of Q-score-equivalent results

### 7.3 `benchmarks/notebooks/nb06_results_tables.ipynb`
Add a new **Table 7: QPack-Adapted Composite Benchmark Scores**:
```
Framework  | S_compile_speed | S_scalability | S_accuracy | S_capacity | S_overall
-----------|----------------|---------------|-----------|-----------|----------
Qiskit     |                |               |           |           |
Cirq       |                |               |           |           |
PennyLane  |                |               |           |           |
```

### 7.4 `benchmarks/notebooks/nb05_figures.ipynb`
Add **Fig. 15: Radar Plot of QPack-Adapted Composite Scores** (one trace per framework).

### 7.5 `benchmarks/scripts/figure_styles.py`
Add `plot_radar(ax, scores_dict, framework_order)` helper function.

---

## 8. New Output Files

| File | Description |
|---|---|
| `benchmarks/metrics/qpack_scores.csv` | `S_speed, S_scale, S_acc, S_cap, S_overall` per framework |
| `benchmarks/metrics/power_law_fits.csv` | exponent `a`, R², fit quality per algorithm per framework |
| `benchmarks/results/structural/fig15_radar_qpack.pdf` | Radar plot |

---

## 9. Research Questions — Revised

With QPack integration, the RQs improve in precision:

| # | Original RQ | QPack-Enhanced Version |
|---|---|---|
| RQ1 | Do QASM structures differ? | Do QASM structures differ, and which framework produces the most hardware-efficient QASM (measured by S_compile_speed and effective QV)? |
| RQ2 | Are distributions equivalent? | Are distributions statistically equivalent (JSD < 0.05), and how does S_accuracy compare across frameworks? |
| RQ3 | Do performance metrics vary? | What is the S_overall composite score per framework, and does it correlate with structural metrics? |
| RQ4 | How do differences scale? | What is the scaling exponent `a` per framework (from gates ~ N^a fit), and which framework has the best S_scalability? |
| **RQ5 (NEW)** | — | **What is the maximum usable qubit count (S_capacity) per framework before distributional divergence exceeds 20% JSD?** |

---

## 10. Implementation Priority

| Priority | Item | Effort | Impact |
|---|---|---|---|
| 🔴 High | Add `fit_power_law()` and `a`-value to `statistical_tests.py` | Low | Directly answers RQ4 with QPack-grade rigour |
| 🔴 High | Add `S_accuracy` (arctan-mapped relative error) | Low | Replaces raw JSD as the headline accuracy metric |
| 🔴 High | Add `S_capacity` (max usable qubits) | Medium | New RQ5 — original finding, not in current plan |
| 🟡 Medium | Add `S_overall` composite score | Low | Headline single-number result for the paper |
| 🟡 Medium | Add radar plot (Fig. 15) | Medium | Clean visual for framework comparison |
| 🟢 Low | Adopt QPack's gates-per-second runtime score | Medium | More rigorous than raw compile time |
| 🟢 Low | Add power-law fit plots to `nb03` | Low | Supports RQ4 argument |

---

## 11. Paper Section Mapping

| Paper Section | Content | QPack Influence |
|---|---|---|
| Section 3: Methodology | Pipeline description, circuit suite | Cite QPack §II as related work |
| Section 4: Structural Results | Gate count, depth, QV, compile time | Add S_compile_speed and exponent `a` |
| Section 5: Simulation Results | JSD, chi-squared, memory | Replace with S_accuracy; add S_capacity |
| **Section 6: Composite Scores (NEW)** | **S_overall radar plot, Table 7** | **Directly inspired by QPack §IV** |
| Section 7: Case Studies | Bell, Grover's, VQE/QAOA, QML | Reference QPack's similar MaxCut findings |
| Section 8: Discussion | Limitations, future work | Compare our S_overall to QPack scores on equivalent simulators |

---

## 12. Citation Strategy

Cite QPack in Paper 5 as:
1. **Related Work (Section 2):** QPack as prior application-oriented benchmarking framework
2. **Methodology (Section 3):** Our accuracy and scalability formulas adapted from QPack §IV
3. **Discussion (Section 8):** Compare our composite scores to QPack's published QuEST and Qiskit-Aer results (QuEST overall = 183.2, Qiskit Aer = 147.2) — our noiseless QSim baseline should produce comparable numbers, providing external validation

**Key differentiator statement for the paper:**
> *"Unlike QPack, which benchmarks execution backends, QCanvas targets the **source-language-to-QASM compilation step**, attributing performance differences explicitly to the source quantum framework. We adopt QPack's composite scoring methodology (§IV) and apply it to the first systematic cross-framework QASM structural study."*
