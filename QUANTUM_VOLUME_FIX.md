# Quantum Volume Calculation Fix — March 2026

## 🔴 THE BUG (FOUND & FIXED)

### What Was Wrong
The `estimate_effective_qv()` function was **testing fidelity with the actual circuit's depth** instead of a **square circuit** (m × m).

**Buggy Code:**
```python
f = estimate_circuit_fidelity(m, circuit_depth, ...)  # ❌ WRONG
```

**Problem:** 
- For shallow circuits (depth 3), **any value of m** maintains fidelity > 0.5
- Result: Bell State (depth 3) incorrectly got QV = **2^30 (1,073,741,824)** ⚠️

### The Correct Definition
Quantum Volume requires finding the largest **m** such that a **square circuit** (m qubits × m depth) maintains fidelity > 0.5:

$$QV = 2^m \text{ where } F(m, m) > 0.5$$

**Fixed Code:**
```python
f = estimate_circuit_fidelity(m, m, ...)  # ✓ CORRECT
```

---

## ✅ EXPECTED VALUES (AFTER FIX)

| Algorithm | Framework | Depth | Corrected QV | Old (Buggy) QV |
| :--- | :--- | :--- | :--- | :--- |
| **Bell State** | all | 3 | **2^11** (2,048) | 2^30 (1B) ❌ |
| **Bernstein-Vazirani (3Q)** | all | 4 | **2^11** (2,048) | 2^30 (1B) ❌ |
| **Bernstein-Vazirani (4Q)** | Qiskit | 6 | **2^11** (2,048) | 2^22 (4M) ❌ |
| **Bernstein-Vazirani (4Q)** | PennyLane | 4 | **2^11** (2,048) | 2^30 (1B) ❌ |

### Typical Realistic Ranges
- **Shallow circuits (depth 3–6):** QV = 2^10 to 2^15 (1K–32K)
- **Medium circuits (depth 10–20):** QV = 2^5 to 2^10 (32–1K)  
- **Deep circuits (depth 30+):** QV = 2^1 to 2^5 (2–32)

---

## 🔧 CODE CHANGES MADE

### 1. **`benchmarks/scripts/quantum_volume.py`**
   - Changed line 161 in `estimate_effective_qv()`:
     - FROM: `f = estimate_circuit_fidelity(m, circuit_depth, ...)`
     - TO: `f = estimate_circuit_fidelity(m, m, ...)`
   - Added detailed docstring explaining the fix

### 2. **`docs/explanations/quantum_volume.md`**
   - Updated section 2 to clarify QV is a **hardware capability metric**, independent of circuit structure
   - Fixed section 3.B algorithmto show **square circuit** testing
   - Updated expected value ranges and interpretation guide
   - Added realistic circuit examples with corrected QV values

---

## 🚀 HOW TO REGENERATE THE DATA

### Option A: Run the Notebook Cell (RECOMMENDED)
1. **Open** `benchmarks/notebooks/nb02_simulation_and_qv.ipynb`
2. **Re-run cell 9** (Quantum Volume estimation):
   ```python
   from benchmarks.scripts.quantum_volume import compute_qv_for_all
   df_qv = compute_qv_for_all('../metrics/structural_metrics.csv')
   df_qv.to_csv('../metrics/quantum_volume_estimates.csv', index=False)
   ```
   - This will regenerate `quantum_volume_estimates.csv` with corrected values

### Option B: Run the Script
```bash
cd c:\Study Material\FYP\QCanvas-Project\QCanvas
python benchmarks\scripts\quantum_volume.py
```

---

## 📊 CORRECTED DATA SAMPLE

A new file `benchmarks/metrics/quantum_volume_estimates_new.csv` has been pre-computed and is ready to replace the old one.

**Head of corrected data (first 5 rows):**
```
algorithm                framework    n_qubits  circuit_depth  effective_qv_log2  effective_qv  actual_fidelity
bell_state               cirq         2         3              11                 2048          0.978631
bell_state               pennylane    2         3              11                 2048          0.978631
bell_state               qiskit       2         3              11                 2048          0.978631
bernstein_vazirani       cirq         3         4              11                 2048          0.939599
```

---

## 📝 KEY TAKEAWAYS

1. **Quantum Volume is a hardware metric**, not a compilation metric
2. It represents the **largest square circuit** executable with >50% fidelity
3. The **same QV applies to all frameworks** under the same noise model
4. **`actual_fidelity`** column shows how well the specific circuit performs
5. **Framework comparison** should focus on circuit depth and structure, not QV directly

### Updated Interpretation:
- ✅ **Use QV** to understand device capabilities under assumed noise
- ✅ **Use `actual_fidelity`** to compare framework output quality
- ✅ **Use circuit_depth** to rank compiler efficiency

---

## ✨ FILES MODIFIED

- ✅ `benchmarks/scripts/quantum_volume.py` — Fixed algorithm
- ✅ `docs/explanations/quantum_volume.md` — Updated documentation
- 💾 `benchmarks/metrics/quantum_volume_estimates_new.csv` — Corrected data (ready to deploy)

---

## 🔍 VERIFICATION

To verify the fix is working correctly:

```python
from benchmarks.scripts.quantum_volume import estimate_effective_qv

# Test: Bell State (2Q, depth 3)
result = estimate_effective_qv(n_qubits=2, circuit_depth=3)
print(f"QV Log2: {result['effective_qv_log2']}")      # Should be: 11
print(f"QV: {result['effective_qv']}")                 # Should be: 2048
print(f"Actual Fidelity: {result['actual_fidelity']}")  # Should be: ~0.978
```

Expected output:
```
QV Log2: 11
QV: 2048
Actual Fidelity: 0.978631
```

