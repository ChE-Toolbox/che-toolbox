# Test Scenarios: Thermodynamic Extension

**Date**: 2025-12-30
**Feature**: Thermodynamic Extension (002-thermodynamic-models)
**Status**: Testing Phase

---

## Overview

This document defines comprehensive test scenarios for:
1. Van der Waals EOS validation
2. Ideal Gas Law verification
3. PT Flash calculation convergence
4. Cross-model comparison

All test data sourced from NIST WebBook, Perry's Handbook, and Smith et al.

---

## Van der Waals Test Scenarios

### Scenario VDW-1: High Pressure Methane
**Objective**: Validate VDW at high pressure where attractive forces dominate

**Test Conditions**:
- Compound: Methane (CH4)
- Temperature: 300 K
- Pressure: 50 MPa
- Critical properties: Tc=190.56K, Pc=4.5992MPa

**Expected Results**:
- Z-factor: 0.864 ± 0.017 (2% tolerance)
- V_molar: ~5.42e-05 m³/mol
- Phase: Supercritical (T > Tc)

**Validation**:
- Compare against NIST WebBook data
- Verify Z < 1.0 (attractive forces)
- Check parameter calculations: a > 0, b > 0

---

### Scenario VDW-2: Moderate Pressure Ethane
**Objective**: Test VDW accuracy at intermediate conditions

**Test Conditions**:
- Compound: Ethane (C2H6)
- Temperature: 350 K
- Pressure: 20 MPa
- Critical properties: Tc=305.32K, Pc=4.8722MPa

**Expected Results**:
- Z-factor: 0.752 ± 0.015 (2% tolerance)
- V_molar: ~1.10e-04 m³/mol
- Phase: Supercritical

**Validation**:
- NIST comparison within ±2%
- Verify cubic solver finds valid root
- Material balance: V = nRT*Z/P

---

### Scenario VDW-3: Multi-Compound Validation
**Objective**: Parametrized test across 5 compounds

**Test Matrix**:

| Compound | T (K) | P (MPa) | Z_NIST | Tolerance |
|----------|-------|---------|--------|-----------|
| Methane  | 300   | 50      | 0.864  | ±2%       |
| Ethane   | 350   | 20      | 0.752  | ±2%       |
| Propane  | 400   | 15      | 0.798  | ±2%       |
| Water    | 500   | 25      | 0.712  | ±2%       |
| Nitrogen | 250   | 30      | 0.801  | ±2%       |

**Validation**:
- All compounds pass ±2% error threshold
- VDW degrades gracefully for polar compounds (water)
- Non-polar compounds show best accuracy

---

### Scenario VDW-4: Edge Cases
**Objective**: Test VDW robustness at boundary conditions

**Test Cases**:

1. **Near-Zero Pressure**:
   - T=300K, P=0.1 Pa
   - Expected: V → ∞ (ideal gas limit)
   - Z → 1.0

2. **Near-Critical Temperature**:
   - T=0.95*Tc, P=Pc
   - Expected: Z significantly < 1.0
   - VDW less accurate (known limitation)

3. **Invalid Inputs**:
   - T ≤ 0: ValueError
   - P < 0: ValueError
   - Tc ≤ 0, Pc ≤ 0: ValueError

---

## Ideal Gas Test Scenarios

### Scenario IG-1: Standard Temperature and Pressure
**Objective**: Verify ideal gas at STP

**Test Conditions**:
- T: 298.15 K
- P: 101325 Pa
- n: 1.0 mol

**Expected Results**:
- V_molar: 0.024466 m³/mol (22.4 L/mol)
- Z-factor: 1.0000 exactly
- Phase: VAPOR

**Validation**:
- Z = 1.0 exactly (no approximation)
- V = RT/P calculated correctly
- Phase always VAPOR

---

### Scenario IG-2: Wide Range Validation
**Objective**: Test ideal gas across temperature/pressure ranges

**Test Matrix**:

| T (K) | P (Pa) | V_expected (m³/mol) | Z |
|-------|--------|---------------------|---|
| 273.15 | 101325 | 0.022414 | 1.0 |
| 298.15 | 101325 | 0.024466 | 1.0 |
| 373.15 | 101325 | 0.030619 | 1.0 |
| 300 | 50e6 | 4.99e-05 | 1.0 |

**Validation**:
- Z always exactly 1.0
- V scales linearly with T/P
- No cubic solve required

---

### Scenario IG-3: Invalid Input Handling
**Objective**: Test error handling

**Test Cases**:
1. T ≤ 0: ValueError("Temperature must be positive")
2. P ≤ 0: ValueError("Pressure must be positive")
3. n ≤ 0: ValueError("Moles must be positive")

---

## Cross-Model Comparison Scenarios

### Scenario CMP-1: Ethane at Moderate Conditions
**Objective**: Compare all three EOS models

**Test Conditions**:
- Compound: Ethane
- T: 350 K
- P: 20 MPa

**Expected Results**:

| Model | Z-factor | V_molar (m³/mol) | Notes |
|-------|----------|------------------|-------|
| Ideal Gas | 1.0000 | 1.46e-04 | Baseline |
| Van der Waals | 0.7524 | 1.10e-04 | Attractive forces |
| Peng-Robinson | 0.7832 | 1.14e-04 | Most accurate |

**Validation**:
- Z_ideal > Z_vdw, Z_pr (non-ideal effects)
- All models return valid states
- PR should be closest to NIST

---

### Scenario CMP-2: Cross-EOS Function
**Objective**: Test `compare_compressibility_factors()` utility

**Implementation**:
```python
def compare_compressibility_factors(compound, T, P):
    """Return dict with Z-factors from all models."""
    return {
        'ideal_Z': 1.0,
        'vdw_Z': ...,
        'pr_Z': ...
    }
```

**Validation**:
- Returns dict with all three keys
- Z-factors in expected order
- No exceptions raised

---

## PT Flash Test Scenarios

### Scenario FLASH-1: Binary Ethane-Propane
**Objective**: Standard binary flash convergence

**Test Conditions**:
- Feed: 60% ethane, 40% propane
- T: 300 K
- P: 2 MPa
- EOS: Peng-Robinson

**Expected Results**:
- Convergence: SUCCESS (4-6 iterations)
- L: 0.424 ± 0.01
- V: 0.576 ± 0.01
- x_ethane: 0.510 ± 0.01
- y_ethane: 0.725 ± 0.01
- K_ethane: ~1.42
- Material balance error: < 1e-6
- Fugacity tolerance: < 1e-6

**Validation**:
- L + V = 1.0 exactly
- sum(x) = 1.0, sum(y) = 1.0
- K_i = y_i / x_i
- Convergence in < 50 iterations

---

### Scenario FLASH-2: Single-Phase Detection
**Objective**: Test single-phase detection logic

**Test Cases**:

1. **Pure Component (n=1)**:
   - Feed: 100% methane
   - Expected: FlashConvergence.SINGLE_PHASE
   - L=1.0 or V=1.0 (depending on P vs P_sat)

2. **Supercritical Mixture**:
   - T: 400 K (above both Tc)
   - Expected: FlashConvergence.SINGLE_PHASE
   - V=1.0, L=0.0

3. **Subcooled Liquid**:
   - T: 250 K, P: 50 MPa (high pressure)
   - Expected: FlashConvergence.SINGLE_PHASE
   - L=1.0, V=0.0

**Validation**:
- Single-phase detected before RR iteration
- No wasted iterations
- Correct phase assignment

---

### Scenario FLASH-3: Material Balance Validation
**Objective**: Verify material balance closure

**Test Conditions**:
- Binary: methane-propane (55%-45%)
- T: 280 K, P: 3 MPa

**Expected Results**:
- Material balance: max(|z_i - (L*x_i + V*y_i)|) < 1e-6

**Validation Check**:
```python
for i in range(n_components):
    error = abs(z[i] - (L * x[i] + V * y[i]))
    assert error < 1e-6
```

---

### Scenario FLASH-4: Fugacity Equilibrium
**Objective**: Verify fugacity equilibrium criterion

**Test Conditions**:
- Binary: ethane-propane (50%-50%)
- T: 310 K, P: 2.5 MPa

**Expected Results**:
- Fugacity criterion: |f_i^v / f_i^l - 1| < 1e-6 for all i

**Validation**:
- Calculate fugacity coefficients from PR EOS
- Verify ratio ≈ 1.0 within tolerance
- Check all components simultaneously

---

### Scenario FLASH-5: Convergence Robustness
**Objective**: Test flash with difficult initial guesses

**Test Cases**:

1. **Poor K-value Initialization**:
   - Initialize K_i = 1.0 (uniform)
   - Expected: Still converges, but more iterations

2. **Near-Critical Conditions**:
   - T ≈ 0.95*Tc_mix
   - Expected: Slower convergence, but success

3. **Extreme Compositions**:
   - Feed: 95% light, 5% heavy
   - Expected: Converges, handles numerical stability

**Validation**:
- Convergence achieved in < 50 iterations
- Material balance maintained
- No numerical overflow/underflow

---

## Integration Test Scenarios

### Scenario INT-1: All EOS Models Runnable
**Objective**: Verify all three models can run on identical conditions

**Test Conditions**:
- Compound: Ethane
- T: 350 K, P: 20 MPa

**Validation**:
- IdealGasEOS.calculate_volume() → positive result
- VanDerWaalsEOS.calculate_volume() → positive result
- PengRobinsonEOS.calculate_volume() → positive result
- No exceptions raised

---

### Scenario INT-2: CLI Integration
**Objective**: Test CLI wrappers (Phase 6)

**Commands**:
```bash
python -m src.cli vdw --compound methane --temperature 300 --pressure 50e6
python -m src.cli ideal --temperature 298.15 --pressure 101325
python -m src.cli flash --mixture "ethane:0.6,propane:0.4" --temperature 300 --pressure 2e6
```

**Validation**:
- All commands execute without error
- Output formatted correctly
- Results match unit test expectations

---

## Performance Test Scenarios

### Scenario PERF-1: Calculation Speed
**Objective**: Verify performance targets

**Test Matrix**:

| Operation | Target | Measurement |
|-----------|--------|-------------|
| VDW volume | < 5 ms | Avg of 100 runs |
| Ideal Gas | < 1 ms | Avg of 100 runs |
| Binary flash | < 200 ms | Single calculation |
| 5-component flash | < 500 ms | Single calculation |

**Validation**:
- Use `pytest-benchmark` for timing
- Report 95th percentile latency
- Flag performance regressions

---

### Scenario PERF-2: Full Test Suite
**Objective**: Complete test suite runs in reasonable time

**Target**: < 60 seconds on standard laptop

**Validation**:
- Run `pytest tests/ -v`
- Measure wall-clock time
- Coverage > 80%

---

## Test Coverage Requirements

### Unit Test Coverage
- **Target**: > 80% line coverage
- **Tools**: pytest-cov

**Per-Module Requirements**:
- `van_der_waals.py`: > 90% (critical)
- `ideal_gas.py`: > 95% (simple)
- `flash_pt.py`: > 85% (complex)

### Type Coverage
- **Target**: 100% (mypy --strict)
- **Zero errors** from mypy

### Validation Coverage
- **NIST tests**: 5 compounds × 3 conditions = 15 tests
- **Flash tests**: 9 binary mixtures (from CSV)
- **Edge cases**: 10+ scenarios

---

## Test Execution Plan

### Phase 3A: Unit Tests (Priority 1)
1. `test_van_der_waals.py` (T033-T038)
2. `test_ideal_gas.py` (T054-T058)
3. `test_flash_pt.py` (T085-T090)

### Phase 3B: Integration Tests (Priority 2)
4. `test_integration.py` (T059-T063, T091-T095)

### Phase 3C: Validation Tests (Priority 3)
5. `vdw_nist_validation.py` (T039-T043)
6. `flash_balance_tests.py` (T096-T100)

### Phase 3D: Final QA (Priority 4)
7. Type checking (T046, T066, T103)
8. Coverage report (T118)
9. Code linting (T120)

---

## Acceptance Criteria

**Phase 3 Complete When**:
- [ ] All unit tests pass (green)
- [ ] All NIST validation tests within ±2% tolerance
- [ ] All flash tests converge with < 1e-6 error
- [ ] pytest-cov reports > 80% coverage
- [ ] mypy --strict reports zero errors
- [ ] ruff check reports zero issues

**MVP Ready When**:
- [ ] Phases 1-4 complete
- [ ] VDW matches NIST reference data
- [ ] Cross-model comparison functional
- [ ] All tests green

---

**Status**: Test Scenarios Defined ✓
