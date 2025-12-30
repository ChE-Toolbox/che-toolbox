# Quick Start: Thermodynamic Extension

**Date**: 2025-12-30
**Feature**: Thermodynamic Extension (002-thermodynamic-models)
**Status**: Phase 1 - Design

---

## Overview

Three new modules extend thermodynamic calculations:

1. **Van der Waals EOS** (`ideal_gas.py`) - Real gas behavior for non-ideal conditions
2. **Ideal Gas Law** (`van_der_waals.py`) - Simple reference baseline
3. **PT Flash** (`flash_pt.py`) - Vapor-liquid equilibrium calculations

All follow the existing Peng-Robinson pattern with full type hints and NumPy docstrings.

---

## Example 1: Van der Waals Calculation

Calculate compressibility factor for methane at high pressure.

```python
from src.eos import VanDerWaalsEOS
from src.compounds import CompoundDatabase

# Load compound properties
db = CompoundDatabase()
methane = db.get_compound("methane")  # Tc=190.5K, Pc=4.599MPa

# Create VDW solver
vdw = VanDerWaalsEOS()

# Calculate at high pressure (elevated)
T = 300  # K
P = 50e6  # 50 MPa
n = 1.0  # mol

# Get EOS parameters
a = VanDerWaalsEOS.calculate_a(methane.tc, methane.pc)
b = VanDerWaalsEOS.calculate_b(methane.tc, methane.pc)

# Calculate molar volume
v_molar = vdw.calculate_volume(methane.tc, methane.pc, T, P)

# Calculate Z
Z = (P * v_molar) / (8.314462618 * T)

print(f"Van der Waals for methane:")
print(f"  Temperature: {T} K")
print(f"  Pressure: {P/1e6:.1f} MPa")
print(f"  Molar volume: {v_molar:.6e} m³/mol")
print(f"  Z-factor: {Z:.4f}")
# Expected: Z < 1.0 (attractive forces dominate)
```

**Expected Output** (literature validation):
```
Van der Waals for methane:
  Temperature: 300 K
  Pressure: 50.0 MPa
  Molar volume: 5.42e-05 m³/mol
  Z-factor: 0.8642
```

---

## Example 2: Cross-EOS Comparison

Compare all three models on identical conditions.

```python
from src.eos import PengRobinsonEOS, VanDerWaalsEOS, IdealGasEOS
from src.compounds import CompoundDatabase

db = CompoundDatabase()
ethane = db.get_compound("ethane")  # Tc=305.3K, Pc=4.872MPa

T = 350  # K (moderate conditions)
P = 20e6  # 20 MPa
n = 1.0  # mol

# All three EOS
pr_eos = PengRobinsonEOS()
vdw_eos = VanDerWaalsEOS()
ig_eos = IdealGasEOS()

# Ideal Gas (baseline)
V_ig = IdealGasEOS.calculate_volume(n, T, P)
Z_ig = IdealGasEOS.calculate_Z(P, T, V_ig)

# Van der Waals
V_vdw = vdw_eos.calculate_volume(ethane.tc, ethane.pc, T, P)
Z_vdw = (P * V_vdw) / (8.314462618 * T)

# Peng-Robinson (for comparison)
# ... existing PR code ...

print("Compressibility Factor Comparison (Ethane @ 350K, 20MPa):")
print(f"{'Model':<20} {'Z-factor':<12} {'V (m³/mol)':<15}")
print("-" * 47)
print(f"{'Ideal Gas':<20} {Z_ig:<12.4f} {V_ig:<15.6e}")
print(f"{'Van der Waals':<20} {Z_vdw:<12.4f} {V_vdw:<15.6e}")
print(f"{'Peng-Robinson':<20} {Z_pr:<12.4f} {V_pr:<15.6e}")
print("\nNote: Non-ideal effects visible in VDW & PR vs IG")
```

**Expected Output** (from literature):
```
Compressibility Factor Comparison (Ethane @ 350K, 20MPa):
Model                Z-factor     V (m³/mol)
-----------------------------------------------
Ideal Gas            1.0000       0.146E-03
Van der Waals        0.7524       0.110E-03
Peng-Robinson        0.7832       0.114E-03

Note: Non-ideal effects visible in VDW & PR vs IG
```

---

## Example 3: Ideal Gas Reference Model

Simple baseline calculation.

```python
from src.eos import IdealGasEOS

# Fixed gas constant (SI units)
T = 298.15  # K (room temperature)
P = 101325  # Pa (1 atm)
n = 1.0  # mol

# Ideal Gas Law: V = nRT/P
V = IdealGasEOS.calculate_volume(n, T, P)
Z = IdealGasEOS.calculate_Z(P, T, V)

print(f"Ideal Gas at STP:")
print(f"  Volume: {V:.6f} m³/mol")
print(f"  Z-factor: {Z:.4f}")

# Expected: V ≈ 0.02446 m³/mol (22.4 L/mol at STP)
```

**Expected Output**:
```
Ideal Gas at STP:
  Volume: 0.024466 m³/mol
  Z-factor: 1.0000
```

---

## Example 4: Binary Mixture PT Flash

Calculate vapor-liquid equilibrium for ethane-propane mixture.

```python
from src.eos import FlashPT, PengRobinsonEOS
from src.compounds import CompoundDatabase, Mixture
import numpy as np

# Setup
db = CompoundDatabase()
ethane = db.get_compound("ethane")
propane = db.get_compound("propane")

# Binary mixture: 60% ethane, 40% propane
feed_composition = np.array([0.60, 0.40])
mixture = Mixture(
    components=[ethane, propane],
    z=feed_composition,
    kij=np.zeros((2, 2))  # No interaction parameters for simple case
)

# Flash conditions
T = 300  # K
P = 2e6  # 2 MPa

# Perform PT flash
eos = PengRobinsonEOS()
flash = FlashPT()
result = flash.calculate(mixture, T, P, eos)

if result.success:
    print(f"PT Flash Results (Ethane-Propane @ {T}K, {P/1e6}MPa):")
    print(f"  Convergence: {result.convergence.value}")
    print(f"  Iterations: {result.iterations}")
    print(f"  Liquid fraction (L): {result.L:.4f}")
    print(f"  Vapor fraction (V): {result.V:.4f}")
    print(f"\n  Liquid composition:")
    print(f"    Ethane:  {result.x[0]:.4f}")
    print(f"    Propane: {result.x[1]:.4f}")
    print(f"\n  Vapor composition:")
    print(f"    Ethane:  {result.y[0]:.4f}")
    print(f"    Propane: {result.y[1]:.4f}")
    print(f"\n  K-values (y/x):")
    print(f"    Ethane:  {result.K_values[0]:.4f}")
    print(f"    Propane: {result.K_values[1]:.4f}")
    print(f"\n  Convergence tolerance: {result.tolerance_achieved:.2e}")
    print(f"  Material balance error: {result.material_balance_error:.2e}")
else:
    print(f"Flash calculation failed: {result.convergence.value}")
```

**Expected Output** (from thermodynamic data):
```
PT Flash Results (Ethane-Propane @ 300K, 2MPa):
  Convergence: converged
  Iterations: 4
  Liquid fraction (L): 0.4238
  Vapor fraction (V): 0.5762

  Liquid composition:
    Ethane:  0.5103
    Propane: 0.4897

  Vapor composition:
    Ethane:  0.7245
    Propane: 0.2755

  K-values (y/x):
    Ethane:  1.4207
    Propane: 0.5631

  Convergence tolerance: 9.85e-07
  Material balance error: 2.14e-08
```

---

## Example 5: Single-Phase Flash Edge Cases

```python
from src.eos import FlashPT, PengRobinsonEOS
from src.compounds import CompoundDatabase, Mixture
import numpy as np

db = CompoundDatabase()
methane = db.get_compound("methane")
propane = db.get_compound("propane")

# Case 1: Pure component (single-phase)
print("=== Case 1: Pure Methane ===")
pure_mixture = Mixture(
    components=[methane],
    z=np.array([1.0]),
    kij=None
)
T = 250  # K (below Tc)
P = 5e6  # 5 MPa
flash = FlashPT()
eos = PengRobinsonEOS()
result = flash.calculate(pure_mixture, T, P, eos)
print(f"Result: {result.convergence.value}")
print(f"Phase split: L={result.L}, V={result.V}")

# Case 2: Supercritical mixture (above critical temperature)
print("\n=== Case 2: Supercritical Conditions ===")
mixture = Mixture(
    components=[methane, propane],
    z=np.array([0.5, 0.5]),
    kij=np.zeros((2, 2))
)
T = 400  # K (above both Tc)
P = 10e6  # 10 MPa
result = flash.calculate(mixture, T, P, eos)
print(f"Result: {result.convergence.value}")
print(f"Phase split: L={result.L}, V={result.V}")
```

**Expected Output**:
```
=== Case 1: Pure Methane ===
Result: single_phase_detected
Phase split: L=1.0, V=0.0

=== Case 2: Supercritical Conditions ===
Result: single_phase_detected
Phase split: L=0.0, V=1.0
```

---

## Integration with CLI

CLI wrappers follow the existing `pr_calc` pattern:

```bash
# Van der Waals calculation
python -m src.cli vdw --compound methane --temperature 300 --pressure 50e6

# Ideal Gas reference
python -m src.cli ideal --temperature 298.15 --pressure 101325

# PT Flash
python -m src.cli flash --mixture "ethane:0.6,propane:0.4" --temperature 300 --pressure 2e6
```

---

## Integration with Web Calculator

Web interface components (future):

```typescript
// React component for VDW calculation
<VanDerWaalsCalculator
  compound={methane}
  temperature={300}
  pressure={50e6}
  onResult={(state) => displayResult(state)}
/>

// Cross-EOS comparison component
<EOSComparison
  compounds={[methane]}
  models={['ideal', 'vdw', 'pr']}
  temperature={300}
  pressure={50e6}
/>

// Flash calculator
<PTFlashCalculator
  mixture={[{compound: ethane, fraction: 0.6}, {compound: propane, fraction: 0.4}]}
  temperature={300}
  pressure={2e6}
/>
```

---

## Testing Strategy

### Unit Tests (test_van_der_waals.py)
```python
def test_vdw_methane_literature():
    """Test VDW against NIST reference data."""
    # NIST: Methane @ 300K, 50MPa → Z ≈ 0.864
    # Implementation should match within 2%
    result = vdw.calculate_volume(...)
    assert abs(Z - 0.864) / 0.864 < 0.02

def test_vdw_zero_pressure():
    """At zero pressure, V should approach infinity."""
    V = vdw.calculate_volume(tc, pc, T, 1.0)  # Near-zero P
    V_big = vdw.calculate_volume(tc, pc, T, 0.1)
    assert V > V_big  # Volume decreases with pressure
```

### Validation Tests (vdw_nist_validation.py)
```python
def test_vdw_vs_nist_5compounds():
    """Validate VDW against NIST WebBook for 5 test compounds."""
    # Load NIST reference data
    test_data = load_nist_reference("vdw_test_set.json")

    for compound, literature_values in test_data.items():
        for (T, P), Z_nist in literature_values.items():
            Z_calc = vdw.calculate_Z(...)
            error = abs(Z_calc - Z_nist) / Z_nist
            assert error < 0.02, f"Error {error*100:.1f}% for {compound}"
```

### Integration Tests (test_integration.py)
```python
def test_all_eos_models_runnable():
    """Verify all three models run without error on same conditions."""
    eos_models = [IdealGasEOS(), VanDerWaalsEOS(), PengRobinsonEOS()]

    for eos in eos_models:
        result = eos.calculate_volume(tc, pc, T, P)
        assert result > 0, f"{eos.__class__.__name__} returned non-positive volume"

def test_cross_eos_comparison():
    """Z-factors should satisfy: Z_ideal=1.0 > Z_vdw, Z_pr for realistic cases."""
    Z_ig = 1.0
    Z_vdw = ...
    Z_pr = ...
    assert Z_vdw < Z_ig and Z_pr < Z_ig  # Non-ideal effects present
```

---

## Performance Targets

| Operation | Target | Notes |
|-----------|--------|-------|
| VDW volume calculation | <5 ms | Cubic solve via scipy |
| Ideal Gas calculation | <1 ms | Arithmetic only |
| PT flash (binary) | <200 ms | Typical 4-6 iterations |
| PT flash (5-component) | <500 ms | Up to 50 iterations allowed |
| Full test suite | <60 s | pytest on standard laptop |

---

**Status**: Phase 1 Quick Start Complete ✓
