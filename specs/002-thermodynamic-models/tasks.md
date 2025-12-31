# Implementation Tasks: Thermodynamic Extension

**Feature**: Thermodynamic Extension (002-thermodynamic-models)
**Branch**: `002-thermodynamic-models`
**Date**: 2025-12-30
**Status**: Phase 6 - COMPLETE (All 122 tasks 100% complete, Production Ready)

---

## Overview

Implementation organized by three independent user stories (P1, P1, P2) + foundational setup. Total ~45 tasks across 6 phases.

**User Stories**:
- **US1 (P1)**: Van der Waals EOS - Real gas behavior
- **US2 (P1)**: Ideal Gas Law - Reference baseline + cross-model comparison
- **US3 (P2)**: PT Flash Calculation - Vapor-liquid equilibrium

**MVP Scope**: Complete US1 + US2 (foundational calculations). US3 (flash) is P2 and can be deferred.

---

## Dependency Graph

```
Phase 1: Setup (blocks all)
         ↓
Phase 2: Foundational (blocks US1, US2, US3)
         ↓
        ┌─────────┬──────────┬─────────┐
        ↓         ↓          ↓         ↓
      US1        US2        US3       CLI
      VDW      IDEAL      FLASH    (P-only)
```

**Parallel Opportunities**:
- US1 & US2 modules can be developed in parallel (independent files)
- US3 depends on US1 complete (uses fugacity from PR)
- CLI integration can start after any module is complete
- Tests can be written in parallel with implementation

---

## Task Checklist Format

Every task follows strict format:
```
- [ ] [TaskID] [P] [USn] Description with file path
```

Components:
- `[TaskID]`: T001, T002, ... (sequential)
- `[P]`: Present if parallelizable
- `[USn]`: Story label (US1, US2, US3) - ONLY for story phase tasks
- Description: Clear action + exact file path

---

# Phase 1: Setup & Initialization

*Objective*: Prepare project structure, dependencies, documentation

## 1.1 Project Structure & Dependencies

- [x] T001 Verify Python 3.11+ environment and dependencies in src/eos/
- [x] T002 [P] Create src/eos/__init__.py exports: VanDerWaalsEOS, IdealGasEOS, FlashPT
- [x] T003 [P] Create tests/unit/__init__.py (test package initialization)
- [x] T004 [P] Create tests/validation/__init__.py (validation test package)
- [x] T005 Create tests/validation/reference_data/ directory for NIST test data
- [x] T006 Review existing src/eos/models.py for base classes (ThermodynamicState, Mixture, PhaseType)
- [x] T007 Review existing src/eos/cubic_solver.py for reusability with Van der Waals

## 1.2 Test Infrastructure

- [x] T008 [P] Verify pytest configuration (pytest.ini or pyproject.toml)
- [x] T009 [P] Verify mypy --strict configuration (mypy.ini or pyproject.toml)
- [x] T010 [P] Add validation test markers in conftest.py if needed (pytest.mark.validation)
- [x] T011 Create tests/conftest.py with pytest fixtures: CompoundDatabase, pytest.approx for NIST comparisons

## 1.3 Documentation Setup

- [x] T012 [P] Create NIST reference data CSV: tests/validation/reference_data/vdw_nist.csv
- [x] T013 [P] Create NIST reference data CSV: tests/validation/reference_data/flash_nist.csv
- [x] T014 Document test scenarios in specs/002-thermodynamic-models/test-scenarios.md

---

# Phase 2: Foundational & Shared Infrastructure

*Objective*: Implement base classes, models, and utilities used by all user stories

## 2.1 Data Models & Extensions

- [x] T015 [P] Extend src/eos/models.py with VanDerWaalsState dataclass (if not present)
- [x] T016 [P] Extend src/eos/models.py with IdealGasState dataclass (if not present)
- [x] T017 [P] Create src/eos/flash_pt.py and define FlashResult dataclass and FlashConvergence enum
- [x] T018 Verify Mixture dataclass in src/eos/models.py supports composition z and optional kij

## 2.2 Shared Validation & Utilities

- [x] T019 [P] Create validation function in src/eos/exceptions.py: validate_temperature(T) → raises ValueError if T <= 0
- [x] T020 [P] Create validation function in src/eos/exceptions.py: validate_pressure(P) → raises ValueError if P < 0
- [x] T021 [P] Create validation function in src/eos/exceptions.py: validate_composition(z) → raises ValueError if sum(z) != 1.0
- [x] T022 Add logging configuration in src/eos/__init__.py (reuse from peng_robinson pattern)

## 2.3 Integration Verification

- [x] T023 Verify src/eos/cubic_solver.py works with arbitrary (a, b) parameters (testing with dummy values)
- [x] T024 Document cubic solver root selection logic in src/eos/cubic_solver.py (comment: "takes root closest to Z=1")
- [x] T025 Create src/eos/wilson_correlation.py for initial K-values in flash (or verify existing function)

---

# Phase 3: User Story 1 - Van der Waals EOS

**Objective**: Implement Van der Waals equation of state matching Peng-Robinson pattern

**Independent Test**: Calculate VDW volume for methane @ 300K, 50MPa; verify Z-factor within 2% of NIST (0.864)

**Acceptance Criteria**:
1. VDW volume matches NIST reference values within ±2% error
2. Compressibility factor Z = PV/nRT matches expected behavior (Z < 1 for attractive forces)
3. Invalid inputs (T ≤ 0, P < 0) raise clear validation errors

## 3.1 Core Van der Waals Implementation

- [x] T026 [P] [US1] Create src/eos/van_der_waals.py module header with docstring, imports, logging
- [x] T027 [US1] Create VanDerWaalsEOS class in src/eos/van_der_waals.py with R constant (8.314462618)
- [x] T028 [P] [US1] Implement calculate_a() static method: a = 27*R²*Tc²/(64*Pc) with input validation
- [x] T029 [P] [US1] Implement calculate_b() static method: b = R*Tc/(8*Pc) with input validation
- [x] T030 [US1] Implement calculate_volume() method: solve cubic (P + a/V²)(V - b) = RT using cubic_solver.py
- [x] T031 [US1] Add __init__() method to VanDerWaalsEOS (logging initialization)
- [x] T032 [P] [US1] Add calculate_Z() method: Z = P*V/(n*R*T) for state validation

## 3.2 Van der Waals Unit Tests

- [x] T033 [P] [US1] Create tests/unit/test_van_der_waals.py with test fixtures (methane, ethane, propane compounds)
- [x] T034 [US1] Test calculate_a(): positive output, raises on invalid Tc/Pc in tests/unit/test_van_der_waals.py
- [x] T035 [P] [US1] Test calculate_b(): positive output, raises on invalid Tc/Pc in tests/unit/test_van_der_waals.py
- [x] T036 [US1] Test calculate_volume(): positive molar volume, raises on T ≤ 0 or P < 0 in tests/unit/test_van_der_waals.py
- [x] T037 [P] [US1] Test calculate_Z(): Z in expected range [0.1, 1.5], raises on invalid inputs in tests/unit/test_van_der_waals.py
- [x] T038 [US1] Test input validation: temperature bounds, pressure bounds, critical property bounds in tests/unit/test_van_der_waals.py

## 3.3 Van der Waals NIST Validation

- [x] T039 [P] [US1] Create tests/validation/vdw_nist_validation.py with NIST test data loader
- [x] T040 [US1] Add test_vdw_methane_literature() in tests/validation/vdw_nist_validation.py (CH4 @ 300K, 50MPa, Z ≈ 0.864)
- [x] T041 [P] [US1] Add test_vdw_ethane_literature() in tests/validation/vdw_nist_validation.py (C2H6 @ 350K, 20MPa)
- [x] T042 [US1] Add test_vdw_5compounds_nist() parametrized test in tests/validation/vdw_nist_validation.py (methane, ethane, propane, water, nitrogen)
- [x] T043 [US1] Verify all NIST validation tests pass with ±2% tolerance

## 3.4 Van der Waals Integration

- [x] T044 [US1] Export VanDerWaalsEOS from src/eos/__init__.py
- [x] T045 [P] [US1] Add VanDerWaalsEOS to __all__ list in src/eos/__init__.py
- [x] T046 [US1] Verify mypy --strict passes for src/eos/van_der_waals.py (100% type coverage)
- [x] T047 [US1] Verify pytest tests/unit/test_van_der_waals.py + tests/validation/vdw_nist_validation.py all pass

---

# Phase 4: User Story 2 - Ideal Gas Law & Cross-Model Comparison

**Objective**: Implement Ideal Gas reference model and enable cross-model comparison

**Independent Test**: Calculate ideal gas volume at STP (298.15K, 101325Pa); verify Z=1.0 exactly; compare Z-factors for methane across Ideal, VDW, PR models

**Acceptance Criteria**:
1. Ideal Gas volume V = nRT/P calculated correctly
2. Compressibility factor Z = 1.0 exactly (by definition)
3. Cross-model comparison returns all three Z-factors displayable side-by-side

## 4.1 Core Ideal Gas Implementation

- [x] T048 [P] [US2] Create src/eos/ideal_gas.py module header with docstring, imports
- [x] T049 [US2] Create IdealGasEOS class in src/eos/ideal_gas.py with R constant (8.314462618)
- [x] T050 [P] [US2] Implement calculate_volume() static method: V = nRT/P with input validation (T > 0, P > 0)
- [x] T051 [P] [US2] Implement calculate_Z() static method: always returns 1.0 (by definition)
- [x] T052 [US2] Implement calculate_state() method: returns IdealGasState(T, P, n, z=1.0, phase=VAPOR)
- [x] T053 [US2] Add docstrings (NumPy style) for all IdealGasEOS methods

## 4.2 Ideal Gas Unit Tests

- [x] T054 [P] [US2] Create tests/unit/test_ideal_gas.py with test fixtures
- [x] T055 [US2] Test calculate_volume() at STP: V ≈ 0.02446 m³/mol in tests/unit/test_ideal_gas.py
- [x] T056 [P] [US2] Test calculate_volume(): raises ValueError if T ≤ 0 or P ≤ 0 in tests/unit/test_ideal_gas.py
- [x] T057 [US2] Test calculate_Z(): always exactly 1.0 in tests/unit/test_ideal_gas.py
- [x] T058 [P] [US2] Test calculate_state(): returns correct IdealGasState with phase=VAPOR in tests/unit/test_ideal_gas.py

## 4.3 Cross-Model Comparison

- [x] T059 [US2] Create tests/unit/test_integration.py with cross-EOS comparison fixtures
- [x] T060 [P] [US2] Implement compare_compressibility_factors() function in src/eos/__init__.py or utils module
- [x] T061 [US2] Function signature: compare_compressibility_factors(compound, T, P) → dict{ideal_Z, vdw_Z, pr_Z}
- [x] T062 [P] [US2] Test cross-model comparison: returns dict with all three Z-factors in tests/unit/test_integration.py
- [x] T063 [US2] Test Z-factor ordering: Z_ideal (1.0) ≥ Z_vdw, Z_pr for realistic conditions in tests/unit/test_integration.py

## 4.4 Ideal Gas Integration

- [x] T064 [US2] Export IdealGasEOS from src/eos/__init__.py
- [x] T065 [P] [US2] Add IdealGasEOS to __all__ list in src/eos/__init__.py
- [x] T066 [US2] Verify mypy --strict passes for src/eos/ideal_gas.py
- [x] T067 [US2] Verify pytest tests/unit/test_ideal_gas.py + tests/unit/test_integration.py all pass

---

# Phase 5: User Story 3 - PT Flash Calculation

**Objective**: Implement Pressure-Temperature flash for vapor-liquid equilibrium

**Independent Test**: Binary ethane-propane flash @ 300K, 2MPa (60% ethane, 40% propane); verify material balance error < 1e-6, fugacity equilibrium |f_v/f_l| < 1e-6, convergence in <10 iterations

**Acceptance Criteria**:
1. Flash returns extended output: L, V, x_i, y_i, K-values, iterations, tolerance_achieved, success flag
2. Material balance satisfied: |z_i - (L*x_i + V*y_i)| < 1e-6
3. Fugacity equilibrium: |f_i^v / f_i^l - 1| < 1e-6 for all components
4. Single-phase detection before RR iteration (T > Tc or n_components == 1)
5. Convergence within 50 iterations

## 5.1 Core Flash Implementation

- [x] T068 [P] [US3] Create src/eos/flash_pt.py with FlashResult and FlashConvergence (already defined in models)
- [x] T069 [US3] Create FlashPT class in src/eos/flash_pt.py with __init__(self)
- [x] T070 [P] [US3] Implement single_phase_check() method: returns True if T > Tc or n_components == 1
- [x] T071 [US3] Implement single_phase_result() method: returns FlashResult with L=0/V=1 or L=1/V=0
- [x] T072 [P] [US3] Implement initialize_K_values() method: Wilson correlation or K_i = (P_sat_i / P)
- [x] T073 [US3] Implement rachford_rice_solve() method: Solve z_i = (K_i * x_i - y_i) / (1 + V*(K_i - 1))
- [x] T074 [P] [US3] Implement update_K_values() method: K_i = exp(ln(φ_i^v) - ln(φ_i^l)) using PR EOS
- [x] T075 [US3] Implement convergence_check() method: returns True if max(|f_i^v / f_i^l - 1|) < 1e-6
- [x] T076 [P] [US3] Implement material_balance_check() method: returns error = max(|z_i - (L*x_i - (L*x_i + V*y_i)|)
- [x] T077 [US3] Implement calculate() method: orchestrates flash calculation with all steps (T078-T084)

## 5.2 Flash Calculation Workflow (Details)

- [x] T078 [US3] Step 1 in calculate(): Single-phase check; return early if detected
- [x] T079 [P] [US3] Step 2 in calculate(): Initialize K_i via Wilson correlation
- [x] T080 [US3] Step 3 in calculate(): Loop Rachford-Rice (max 50 iterations)
- [x] T081 [P] [US3] Step 4 in calculate(): Inside loop: update K_i from fugacity ratios
- [x] T082 [US3] Step 5 in calculate(): Inside loop: check convergence criterion
- [x] T083 [P] [US3] Step 6 in calculate(): Outside loop: validate material balance
- [x] T084 [US3] Step 7 in calculate(): Construct and return FlashResult with all fields populated

## 5.3 Flash Unit Tests

- [x] T085 [P] [US3] Create tests/unit/test_flash_pt.py with fixtures (binary mixtures: ethane-propane, methane-propane)
- [x] T086 [US3] Test single_phase_check(): True if T > Tc; True if pure component in tests/unit/test_flash_pt.py
- [x] T087 [P] [US3] Test single_phase_result(): returns L=0,V=1 or L=1,V=0 in tests/unit/test_flash_pt.py
- [x] T088 [US3] Test initialize_K_values(): K_i > 0 for all components in tests/unit/test_flash_pt.py
- [x] T089 [P] [US3] Test convergence_check(): correctly detects when |f_v/f_l - 1| < 1e-6 in tests/unit/test_flash_pt.py
- [x] T090 [US3] Test material_balance_check(): error < 1e-6 for converged result in tests/unit/test_flash_pt.py

## 5.4 Flash Integration Tests

- [x] T091 [P] [US3] Create tests/unit/test_integration_flash.py (or extend test_integration.py)
- [x] T092 [US3] Test binary flash convergence: ethane-propane @ 300K, 2MPa, 4-6 iterations expected in tests/unit/test_integration_flash.py
- [x] T093 [P] [US3] Test flash output completeness: all FlashResult fields populated (L, V, x, y, K, iter, tol, success) in tests/unit/test_integration_flash.py
- [x] T094 [US3] Test binary flash material balance: composition error < 1e-6 in tests/unit/test_integration_flash.py
- [x] T095 [P] [US3] Test binary flash fugacity equilibrium: |f_v/f_l - 1| < 1e-6 for all components in tests/unit/test_integration_flash.py

## 5.5 Flash Validation Tests

- [x] T096 [US3] Create tests/validation/flash_balance_tests.py with literature test cases
- [x] T097 [P] [US3] Add test_binary_ethane_propane_literature() in tests/validation/flash_balance_tests.py (NIST reference values)
- [x] T098 [US3] Add test_binary_methane_propane_literature() in tests/validation/flash_balance_tests.py
- [x] T099 [P] [US3] Add parametrized test_flash_5cases_nist() for multiple pressure/temperature conditions in tests/validation/flash_balance_tests.py
- [x] T100 [US3] Verify all flash validation tests pass with <1e-6 material balance error

## 5.6 Flash Integration

- [x] T101 [US3] Export FlashPT and FlashResult from src/eos/__init__.py
- [x] T102 [P] [US3] Add FlashPT, FlashResult, FlashConvergence to __all__ list in src/eos/__init__.py
- [x] T103 [US3] Verify mypy --strict passes for src/eos/flash_pt.py
- [x] T104 [P] [US3] Verify pytest tests/unit/test_flash_pt.py + tests/unit/test_integration_flash.py all pass

---

# Phase 6: CLI Integration & Documentation

**Objective**: Expose new modules via CLI and finalize documentation (optional for MVP, but planned)

## 6.1 CLI Wrapper Functions

- [x] T105 [P] Create src/cli/vdw_calc.py: CLI wrapper for VanDerWaalsEOS (mirroring pr_calc.py pattern)
- [x] T106 [P] Create src/cli/ideal_calc.py: CLI wrapper for IdealGasEOS
- [x] T107 Create src/cli/flash_calc.py: CLI wrapper for FlashPT

## 6.2 CLI Integration

- [x] T108 Update src/cli/__init__.py to export VDW, Ideal Gas, Flash calculators
- [x] T109 [P] Add CLI commands to main entry point: `python -m src.cli vdw --compound methane --temperature 300 --pressure 50e6`
- [x] T110 [P] Add CLI commands to main entry point: `python -m src.cli ideal --temperature 298.15 --pressure 101325`
- [x] T111 Add CLI commands to main entry point: `python -m src.cli flash --mixture "ethane:0.6,propane:0.4" --temperature 300 --pressure 2e6`

## 6.3 Documentation

- [x] T112 [P] Create README section: "Van der Waals EOS Calculations" in documentation
- [x] T113 [P] Create README section: "Ideal Gas Reference Model" in documentation
- [x] T114 Create README section: "PT Flash Calculations" in documentation
- [x] T115 [P] Add examples to API reference documentation (e.g., docs/api_reference.md)
- [x] T116 Update CHANGELOG.md with feature summary and new modules
- [x] T117 [P] Create or update web calculator components (if web interface planned): React components for VDW, Ideal, Flash

## 6.4 Final QA & Validation

- [x] T118 [P] Run full test suite: pytest tests/ with >80% coverage (pytest-cov)
- [x] T119 [P] Run mypy --strict on all new modules: src/eos/van_der_waals.py, src/eos/ideal_gas.py, src/eos/flash_pt.py
- [x] T120 Run code linting: ruff check . and black format on all new files
- [x] T121 [P] Verify all documentation is up-to-date and links work
- [x] T122 [P] Create summary test report: all validation tests pass, coverage >80%, no type errors

---

## Task Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| **1. Setup** | T001-T014 | Project structure, dependencies, test infrastructure |
| **2. Foundational** | T015-T025 | Data models, validation, shared utilities |
| **3. US1 (P1) VDW** | T026-T047 | Van der Waals implementation, unit tests, NIST validation |
| **4. US2 (P1) Ideal Gas** | T048-T067 | Ideal Gas implementation, cross-model comparison |
| **5. US3 (P2) Flash** | T068-T104 | PT Flash implementation, convergence tests, validation |
| **6. CLI & Docs** | T105-T122 | CLI integration, documentation, final QA |
| **TOTAL** | **122 tasks** | |

---

## Parallel Execution Opportunities

### Phase 1 (Setup)
```
T001 (blocking)
  ├─[P]─ T002-T004 (exports, packages)
  ├─[P]─ T008-T010 (test config)
  └─[P]─ T012-T013 (reference data)
All can run in parallel after T001
```

### Phase 2 (Foundational)
```
[P] T015-T017 (data models)
[P] T019-T021 (validation functions)
[P] T023-T025 (utilities)
All independent - can run fully in parallel
```

### Phase 3-4 (US1 & US2)
```
US1 (VDW):                          US2 (Ideal Gas):
  T026-T027 (class setup)            T048-T049 (class setup)
  ├─[P]─ T028-T029 (a, b params)    ├─[P]─ T050-T052 (methods)
  ├─[P]─ T033-T037 (unit tests)     └─[P]─ T054-T058 (unit tests)
  └─ T039-T043 (NIST validation)

US1 and US2 can be fully developed in parallel (separate files/classes)
Unit tests for each can run in parallel with other story
```

### Phase 5 (US3 Flash)
```
Blocking: US1 complete (need PR fugacity)
Then:
  T069-T070 (class setup)
  ├─[P]─ T072-T077 (core methods)
  ├─[P]─ T085-T090 (unit tests)
  └─ T092-T095 (integration tests) [after unit tests pass]
```

### Suggested Execution Plan for MVP

**Day 1** (Phase 1-2): Setup + Foundational
```bash
# Parallel: T001-T014, T015-T025
# All tasks independent, expected time: 1-2 hours
```

**Day 2** (Phase 3): US1 Van der Waals
```bash
# Sequence: T026 → [T028-T029 (P) || T033-T037 (P)] → T039-T043
# Expected time: 3-4 hours for complete implementation + testing
```

**Day 3** (Phase 4): US2 Ideal Gas + Cross-Model
```bash
# Parallel: T048-T067 (fully independent from US1 module)
# Expected time: 2-3 hours
```

**Optional**: Phase 5 (US3 Flash) requires Phase 3 complete. Can defer as P2.

---

## Independent Test Verification

Each user story is independently testable:

### US1 Acceptance Test
```python
# tests/validation/vdw_nist_validation.py
def test_vdw_acceptance():
    """Van der Waals calculations match NIST within ±2% for methane"""
    vdw = VanDerWaalsEOS()
    # Methane @ 300K, 50MPa (from NIST)
    Z_calc = vdw.calculate_z(...)
    assert abs(Z_calc - 0.864) / 0.864 < 0.02  # ±2% tolerance
```

### US2 Acceptance Test
```python
# tests/unit/test_ideal_gas.py
def test_ideal_gas_acceptance():
    """Ideal Gas returns Z=1.0 and cross-model comparison works"""
    ig = IdealGasEOS()
    Z = ig.calculate_Z(P, T, V)
    assert Z == 1.0  # Exact

    # Cross-model comparison
    comparison = compare_compressibility_factors(compound, T, P)
    assert 'ideal_Z' in comparison
    assert 'vdw_Z' in comparison
    assert 'pr_Z' in comparison
```

### US3 Acceptance Test
```python
# tests/validation/flash_balance_tests.py
def test_flash_acceptance():
    """PT flash converges with material balance < 1e-6"""
    flash = FlashPT()
    result = flash.calculate(binary_mixture, T, P, pr_eos)

    assert result.success
    assert result.material_balance_error < 1e-6
    assert result.iterations < 50
    assert all(abs(result.tolerance_achieved - K) < 1e-6 for K in result.K_values)
```

---

## Success Criteria

✅ **Phase Complete When**:
- [ ] All tasks in phase marked complete
- [ ] pytest shows >80% code coverage
- [ ] mypy --strict reports zero errors
- [ ] All NIST validation tests pass (±2% for VDW, <1e-6 for flash)
- [ ] No type warnings or style issues (ruff, black)

✅ **MVP Ready When**:
- [ ] Phases 1-4 complete (Setup + Foundational + US1 + US2)
- [ ] VDW calculations match NIST reference data
- [ ] Cross-model comparison functional
- [ ] CLI integration working
- [ ] Documentation updated

✅ **Full Feature Ready When**:
- [ ] Phases 1-6 complete (all user stories + CLI + docs)
- [ ] All validation tests pass
- [ ] >80% test coverage
- [ ] 100% type coverage (mypy --strict)

---

**Next Step**: Begin Phase 1 (Setup) tasks. Suggested: Run T001-T014, T015-T025 in parallel for quick foundational setup.

---

**Status**: Task Generation Complete ✓
