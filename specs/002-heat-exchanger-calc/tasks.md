# Implementation Tasks: Heat Exchanger Calculations

**Feature**: 002-heat-exchanger-calc | **Date**: 2025-12-30 | **Branch**: `002-heat-exchanger-calc`
**Specification**: [spec.md](spec.md) | **Design**: [plan.md](plan.md) | **Data Model**: [data-model.md](data-model.md)

## Overview

This document contains 85 implementation tasks organized by phase and user story. The feature provides a Python library + CLI for heat exchanger calculations with 4 independent modules:

1. **US1 (P1)**: LMTD Method - Calculate heat transfer using Log Mean Temperature Difference
2. **US2 (P1)**: NTU Method - Calculate effectiveness and outlet temperatures
3. **US3 (P2)**: Convection Correlations - Calculate heat transfer coefficients
4. **US4 (P2)**: Insulation Sizing - Economic thickness optimization

Each user story is independently testable and deliverable. Tasks marked `[P]` can run in parallel.

---

## Implementation Strategy

**MVP Scope**: User Story 1 (LMTD Method)
- Completes all setup, foundational, and US1 tasks
- Provides functional library + CLI for LMTD calculations
- Full validation tests against Incropera reference data
- Deliverable in ~40 tasks; estimated 20-25 hours effort

**Phase 2 (P2 Stories)**: Add US2, US3, US4 sequentially
- Each adds ~20 tasks and 5-6 hours effort
- Can be delivered independently after US1

---

## Phase 1: Setup (Project Initialization)

### Foundation & Dependencies

- [x] T001 Create project directory structure: `src/heat_calc/`, `tests/`, `data/`, `docs/`
- [x] T002 [P] Create `pyproject.toml` with dependencies (NumPy, SciPy, Pint, Pydantic, pytest, click, mypy)
- [x] T003 [P] Create `setup.py` for development install support
- [x] T004 [P] Create `tox.ini` for test environment management
- [x] T005 [P] Create `.gitignore` with Python patterns (__pycache__, *.pyc, .venv, dist, build, *.egg-info, .pytest_cache)
- [x] T006 [P] Create `MANIFEST.in` to include data files in distribution

### Package Initialization

- [x] T007 Create `src/heat_calc/__init__.py` with public API exports (placeholder for final exports)
- [x] T008 [P] Create `src/heat_calc/models/__init__.py` (empty, for submodule)
- [x] T009 [P] Create `src/heat_calc/cli/__init__.py` (empty, for CLI submodule)
- [x] T010 [P] Create `src/heat_calc/utils/__init__.py` (empty, for utilities submodule)
- [x] T011 Create `tests/__init__.py` (empty, for test discovery)

### Documentation & Configuration

- [x] T012 Create `README.md` with feature overview, quickstart, and links to docs
- [x] T013 [P] Create `docs/API.md` as stub (placeholder for detailed API reference)
- [x] T014 [P] Create `docs/DEVELOPMENT.md` with setup, testing, and contribution guidelines
- [x] T015 [P] Create `.pre-commit-config.yaml` with black, isort, flake8, mypy checks
- [x] T016 Create `pytest.ini` with coverage thresholds (min 80% coverage)

---

## Phase 2: Foundational Tasks (Blocking Prerequisites)

### Shared Models & Utilities

- [x] T017 Create base Pydantic models in `src/heat_calc/models/base.py`: `BaseCalculationInput`, `BaseCalculationResult`
- [x] T018 Create `src/heat_calc/models/__init__.py` with exports for all model classes (defer specific models to story phases)
- [x] T019 [P] Create `src/heat_calc/utils/validation.py` with input validation helpers (unit checking, range validation, NaN/Inf guards)
- [x] T020 [P] Create `src/heat_calc/utils/constants.py` with physical constants (Boltzmann, gas constant, etc.) and reference correlations metadata

### Validation Test Data

- [x] T021 Create `data/reference_test_cases.json` with structure: `{"lmtd": [...], "ntu": [...], "convection": [...], "insulation": [...]}`
- [x] T022 Populate `data/reference_test_cases.json` with 10+ reference cases from Incropera textbook (with page numbers, expected outputs, tolerance bounds)
- [x] T023 [P] Add NIST reference data entries to validation JSON (4-5 cases per category)

### CLI Infrastructure

- [x] T024 Create `src/heat_calc/cli/main.py` with Click group `@click.group()` and stub commands for: `calculate-lmtd`, `calculate-ntu`, `calculate-convection`, `calculate-insulation`
- [x] T025 Implement CLI argument parsing base: input file handling (JSON/YAML detection), --format option, --output option, --verbose flag
- [x] T026 [P] Implement CLI I/O utilities: JSON deserializer with Pint quantity parsing, YAML deserializer, result formatters (JSON, YAML, table)

### Type Checking & Linting Setup

- [x] T027 Create `mypy.ini` with strict mode config (disallow_untyped_defs, no_implicit_optional, warn_unused_ignores)
- [x] T028 [P] Create `.flake8` config (max-line-length=120, ignore E501, E203, W503 for Pydantic compatibility)
- [x] T029 Run initial mypy check on package stubs (expected: 0 errors baseline)

---

## Phase 3: User Story 1 - LMTD Method (Priority P1)

**Goal**: Calculate heat transfer rate using Log Mean Temperature Difference method for counterflow, parallel, and crossflow configurations.

**Independent Test Criteria**:
- Can calculate LMTD for all 3 configurations
- Results match Incropera reference values within 1%
- Energy balance error < 1%
- Edge cases (near-zero LMTD) handled without overflow

**Files to Create/Modify**:
- `src/heat_calc/models/lmtd_input.py` → Input models
- `src/heat_calc/models/lmtd_results.py` → Result models
- `src/heat_calc/lmtd.py` → Core calculation function
- `src/heat_calc/cli/main.py` → `calculate-lmtd` command
- `tests/unit/test_lmtd.py` → Unit tests
- `tests/validation/test_lmtd_incropera.py` → Validation tests

### Models (Pydantic Entities)

- [x] T030 [US1] Create `src/heat_calc/models/lmtd_input.py` with: `FluidState`, `HeatExchangerConfiguration`, `LMTDInput` classes per data-model.md
- [x] T031 [US1] Create `src/heat_calc/models/lmtd_results.py` with: `LMTDResult` class with heat_transfer_rate, LMTD_arithmetic, LMTD_effective, energy_balance validation fields
- [x] T032 [US1] [P] Add Pydantic validators to `LMTDResult`: ensure LMTD_effective ≤ LMTD_arithmetic, energy_balance_error_percent < 1%, handle NaN/Inf guards

### Core Calculation Function

- [x] T033 [US1] Create `src/heat_calc/lmtd.py` with function stub: `calculate_lmtd(input_data: LMTDInput) -> LMTDResult`
- [x] T034 [US1] Implement LMTD logarithmic mean calculation: `LMTD = (ΔT1 - ΔT2) / ln(ΔT1 / ΔT2)` with epsilon guard for small differences
- [x] T035 [US1] [P] Implement counterflow configuration: LMTD formula for counterflow, F_correction factor application (F=1.0 for ideal counterflow)
- [x] T036 [US1] [P] Implement parallel flow configuration: LMTD formula for parallel, F_correction from input (typical F=0.75-0.85)
- [x] T037 [US1] Implement crossflow configuration: LMTD formula for unmixed/unmixed, unmixed/mixed, mixed/mixed options
- [x] T038 [US1] [P] Implement heat transfer rate calculation: `Q = UA × F × LMTD` where U from properties module, A from input
- [x] T039 [US1] [P] Implement energy balance validation: calculate `Q_hot = mdot_h × cp_h × ΔT_h` and `Q_cold = mdot_c × cp_c × ΔT_c`, verify < 1% error
- [x] T040 [US1] Implement edge case handling: guard against LMTD → 0 (parallel flow with equal temps), retrograde flow (T_outlet > T_inlet for hot), return error with guidance

### Unit Tests

- [x] T041 [US1] Create `tests/unit/test_lmtd.py` with test structure and helper functions
- [x] T042 [US1] [P] Test counterflow LMTD calculation: basic case, symmetrical temps, asymmetrical temps
- [x] T043 [US1] [P] Test parallel flow LMTD calculation: all three configurations (unmixed/unmixed, etc.)
- [x] T044 [US1] [P] Test crossflow configurations: unmixed/unmixed, mixed/unmixed options
- [x] T045 [US1] Test correction factor application: F in [0, 1], LMTD_effective validation
- [x] T046 [US1] [P] Test energy balance: hot and cold side Q values match within tolerance, error_percent < 1%
- [x] T047 [US1] Test edge cases: near-zero ΔT, inverted temps (hot < cold), retrograde flow detection

### Validation Tests (Literature)

- [x] T048 [US1] Create `tests/validation/test_lmtd_incropera.py` with Incropera test case loading
- [x] T049 [US1] [P] Implement validation test loop: load reference cases from JSON, calculate, compare within tolerance
- [x] T050 [US1] [P] Test validation: Incropera Example 10.1-10.5 (or available page numbers), 100% pass rate required
- [x] T051 [US1] Test validation: at least 5 different configurations (counterflow, parallel, crossflow variants), all within 1% tolerance

### CLI Implementation

- [x] T052 [US1] Implement `calculate-lmtd` CLI command in `src/heat_calc/cli/main.py`: argument parser for input file
- [x] T053 [US1] [P] Implement `calculate-lmtd` input validation: detect JSON vs YAML, parse Quantity strings (e.g., "100 degC")
- [x] T054 [US1] [P] Implement `calculate-lmtd` output formatting: --format json (default), --format yaml, --format table (human-readable)
- [x] T055 [US1] [P] Implement `calculate-lmtd` error handling: exit code 1 for input errors, 2 for calculation errors, 0 for success
- [x] T056 [US1] Test CLI: provide test input files (test_lmtd_counterflow.json, test_lmtd_parallel.json, test_lmtd_crossflow.json)

### Final Integration

- [x] T057 [US1] Update `src/heat_calc/__init__.py` to export: `calculate_lmtd`, `LMTDInput`, `LMTDResult`
- [x] T058 [US1] [P] Run full mypy check: zero errors on lmtd module and tests
- [x] T059 [US1] Run test suite: pytest tests/unit/test_lmtd.py tests/validation/test_lmtd_incropera.py --cov=src/heat_calc/lmtd (expect >90% coverage)
- [x] T060 [US1] [P] Manual CLI testing: run calculate-lmtd with test cases, verify output accuracy and format options
- [x] T061 [US1] Document `calculate_lmtd()` function with NumPy-style docstring (see quickstart.md template)

**US1 Subtotal**: 32 tasks | **Status**: ✅ COMPLETE (MVP DELIVERABLE)

---

## Phase 4: User Story 2 - NTU Method (Priority P1)

**Goal**: Calculate heat exchanger effectiveness and outlet temperatures using Number of Transfer Units method.

**Independent Test Criteria**:
- Can calculate NTU for all 4 configurations
- Effectiveness bounded to [0, 1]
- Outlet temperatures satisfy energy balance within 2%
- Results match published NTU correlations

**Files to Create/Modify**:
- `src/heat_calc/models/ntu_input.py` → Input models
- `src/heat_calc/models/ntu_results.py` → Result models
- `src/heat_calc/ntu.py` → Core calculation function
- `src/heat_calc/cli/main.py` → `calculate-ntu` command
- `tests/unit/test_ntu.py` → Unit tests
- `tests/validation/test_ntu_correlations.py` → Validation tests

### Models (Pydantic Entities)

- [x] T062 [US2] Create `src/heat_calc/models/ntu_input.py` with: `NTUInput` class per data-model.md
- [x] T063 [US2] Create `src/heat_calc/models/ntu_results.py` with: `NTUResult` class with NTU, effectiveness, outlet temps, C_min/C_max, Q_max, energy_balance fields
- [x] T064 [US2] [P] Add Pydantic validators to `NTUInput`: mutually exclusive `T_hot_outlet` and `T_cold_outlet` (supply one or neither, not both)
- [x] T065 [US2] [P] Add Pydantic validators to `NTUResult`: effectiveness in [0, 1], NTU >= 0, Q_actual ≤ Q_max

### Core Calculation Function

- [x] T066 [US2] Create `src/heat_calc/ntu.py` with function stub: `calculate_ntu(input_data: NTUInput) -> NTUResult`
- [x] T067 [US2] Implement heat capacity rate calculations: `C_hot = mdot_hot × cp_hot`, `C_cold = mdot_cold × cp_cold`, `C_min`, `C_max`, `C_ratio`
- [x] T068 [US2] Implement counterflow effectiveness correlation: `ε = (1 - exp(-NTU(1-Cr))) / (1 - Cr×exp(-NTU(1-Cr)))` for Cr ≠ 1
- [x] T069 [US2] [P] Implement parallel flow effectiveness: `ε = (1 - exp(-NTU(1+Cr))) / (1 + Cr)` for all Cr
- [x] T070 [US2] [P] Implement shell-and-tube (1 shell pass, 2 tube passes) effectiveness correlation
- [x] T071 [US2] [P] Implement crossflow unmixed/unmixed and mixed configurations
- [x] T072 [US2] Implement NTU calculation: `NTU = UA / C_min` with reverse lookup if needed
- [x] T073 [US2] [P] Implement outlet temperature calculation: `T_outlet = T_inlet ± Q / (mdot × cp)` with energy balance check
- [x] T074 [US2] [P] Implement Q_max (thermodynamic limit): `Q_max = C_min × (T_hot_inlet - T_cold_inlet)`
- [x] T075 [US2] Implement edge cases: NTU → 0 (ε → 0), NTU → ∞ (ε → 1 or Cr×1), Cr > 1 handling, retrograde temps

### Unit Tests

- [x] T076 [US2] Create `tests/unit/test_ntu.py` with test structure
- [x] T077 [US2] [P] Test counterflow NTU: basic case, Cr = 0, Cr near 1, high NTU
- [x] T078 [US2] [P] Test parallel flow NTU: all Cr values, effectiveness limits
- [x] T079 [US2] [P] Test shell-and-tube effectiveness: 1-2 LMTD correction factors, extreme Cr
- [x] T080 [US2] [P] Test crossflow configurations: unmixed/unmixed, mixed combinations
- [x] T081 [US2] Test outlet temperature calculation: known inlet and UA, verify energy balance
- [x] T082 [US2] [P] Test effectiveness bounds: 0 ≤ ε ≤ 1, ε increases with NTU, ε decreases with Cr
- [x] T083 [US2] Test edge cases: NTU = 0, very high NTU, Cr > 1, retrograde temps

### Validation Tests (Literature)

- [x] T084 [US2] Create `tests/validation/test_ntu_correlations.py` with reference correlation loading
- [x] T085 [US2] [P] Implement validation test loop: load NTU reference cases, calculate effectiveness, compare within tolerance (2%)
- [x] T086 [US2] Test validation: at least 5 reference configurations from Perry's or GPSA, all within 2% tolerance

### CLI Implementation

- [x] T087 [US2] Implement `calculate-ntu` CLI command: input file parsing, format options, error handling
- [x] T088 [US2] [P] Test CLI: calculate-ntu with various input files, verify outlet temp output

### Final Integration

- [x] T089 [US2] Update `src/heat_calc/__init__.py` to export: `calculate_ntu`, `NTUInput`, `NTUResult`
- [x] T090 [US2] [P] Run mypy check on ntu module: zero errors
- [x] T091 [US2] Run test suite: pytest tests/unit/test_ntu.py tests/validation/test_ntu_correlations.py --cov (expect >85% coverage)
- [x] T092 [US2] [P] Manual CLI testing and documentation

**US2 Subtotal**: 31 tasks | **Status**: ✅ COMPLETE

---

## Phase 5: User Story 3 - Convection Correlations (Priority P2)

**Goal**: Calculate convection heat transfer coefficients for various geometries and flow regimes.

**Independent Test Criteria**:
- Can calculate h for all 4 geometry types
- Coefficients match published correlations within 5%
- Dimensionless numbers (Re, Pr, Nu, Gr, Ra) computed correctly
- Flow regime detection accurate

**Files**: Models, calculations, CLI, tests similar to US1/US2 pattern

**Task Count**: ~20 tasks (abbreviated here for space)

- [x] T093 [US3] Create convection models in `src/heat_calc/models/convection_input.py` and `_results.py`
- [x] T094 [US3] Create `src/heat_calc/convection.py` with geometry-specific correlation functions
- [x] T095 [US3] Implement flat plate laminar (Nusselt: 0.664×Re^0.5×Pr^(1/3))
- [x] T096 [US3] [P] Implement flat plate turbulent (Gnielinski or Dittus-Boelert variant)
- [x] T097 [US3] [P] Implement pipe flow (Dittus-Boelert: Nu = 0.023×Re^0.8×Pr^0.4)
- [x] T098 [US3] Implement cylinder crossflow (Ranz-Marshall or Morgan correlation per Re range)
- [x] T099 [US3] [P] Implement natural convection vertical plate (Ra-based correlation)
- [x] T100 [US3] Create unit and validation tests with literature references
- [x] T101 [US3] Implement `calculate-convection` CLI command

**US3 Subtotal**: ~20 tasks | **Status**: ✅ COMPLETE

---

## Phase 6: User Story 4 - Insulation Sizing (Priority P2)

**Goal**: Calculate economic insulation thickness for cylindrical pipes.

**Independent Test Criteria**:
- Can calculate optimal thickness
- Payback period computed correctly
- Heat loss reduction quantified accurately
- Economic optimization produces minimum cost solution

**Task Count**: ~20 tasks (similar pattern to US3)

- [x] T102 [US4] Create insulation models in `src/heat_calc/models/insulation_input.py` and `_results.py`
- [x] T103 [US4] Create `src/heat_calc/insulation.py` with optimization function
- [x] T104 [US4] Implement heat loss calculation for cylindrical geometry
- [x] T105 [US4] [P] Implement economic optimization (minimize: insulation_cost + energy_loss_cost)
- [x] T106 [US4] [P] Implement temperature constraint mode
- [x] T107 [US4] Implement payback period calculation
- [x] T108 [US4] Create unit and validation tests
- [x] T109 [US4] Implement `calculate-insulation` CLI command

**US4 Subtotal**: ~20 tasks | **Status**: ✅ COMPLETE

---

## Phase 7: Polish & Cross-Cutting Concerns

### Type Coverage & Linting

- [ ] T110 Run mypy on entire codebase: `mypy src/ tests/ --strict` (0 errors required)
- [ ] T111 [P] Run flake8: `flake8 src/ tests/` (0 errors)
- [ ] T112 [P] Run black formatting check: `black --check src/ tests/` (all formatted)
- [ ] T113 Run isort import ordering: `isort --check src/ tests/`

### Test Coverage

- [ ] T114 [P] Run full test suite with coverage: `pytest tests/ --cov=src/heat_calc --cov-report=term-missing`
- [ ] T115 [P] Verify coverage >= 80% (minimum per Constitution III)
- [ ] T116 Verify all validation tests pass: >85% of reference cases within tolerance

### Documentation

- [ ] T117 Create `docs/CALCULATIONS.md` explaining each calculation method with formulas
- [ ] T117 [P] Create `docs/EXAMPLES.md` with 3-4 worked examples (one per story)
- [ ] T118 Update `docs/API.md` with detailed function reference and examples
- [ ] T119 Update `README.md` with installation, quickstart, and links to documentation

### Performance Validation

- [ ] T120 [P] Benchmark suite: time 1000 iterations of each calculation, verify <100ms aggregate (SC-007)
- [ ] T121 [P] Memory profiling: verify <100MB memory per calculation
- [ ] T122 Profile CLI overhead: ensure <10ms added by argument parsing

### Properties Module Integration

- [ ] T123 [P] Verify integration with 001-data-foundations properties abstraction
- [ ] T124 [P] Test with constant properties (user-provided cp, k, etc.)
- [ ] T125 [P] Test with dynamic properties (if CoolProp available via properties module)

### Release Preparation

- [ ] T126 Update version in `src/heat_calc/__init__.py` and `pyproject.toml` to 1.0.0
- [ ] T127 [P] Create CHANGELOG.md documenting features and first release
- [ ] T128 [P] Create LICENSE (MIT) file
- [ ] T129 [P] Final code review: read through lmtd, ntu, convection, insulation modules
- [ ] T130 [P] Final manual testing: exercise all CLIs with sample inputs, verify output quality

---

## Execution Order & Dependencies

### Critical Path (MVP - US1 only):
1. **Phase 1 (Setup)**: T001-T016 (must complete before any implementation)
2. **Phase 2 (Foundational)**: T017-T029 (must complete before US1)
3. **Phase 3 (US1)**: T030-T061 (independent, can start after Phase 2)
4. **Validation**: T048-T051 (parallel with US1, validates US1 completion)

**MVP Completion Time**: ~25 hours, 61 tasks
**Critical Path Length**: ~7-8 hours (parallelizable sections can run concurrently)

### Phase 2 Additions (US2, US3, US4):
- **Phase 4 (US2)**: T062-T092 (depends on Phase 1+2, can start after US1 if US1 passing)
- **Phase 5 (US3)**: T093-T101 (can start after Phase 1+2)
- **Phase 6 (US4)**: T102-T109 (can start after Phase 1+2)

**Full Feature Completion**: ~130 tasks total, ~45-50 hours

### Parallel Execution Groups:
- **T002-T006** (dependencies setup): Can run in parallel
- **T008-T010** (package init): Can run in parallel after T007
- **T035-T039** (LMTD configurations): Can run in parallel
- **T068-T071** (NTU correlations): Can run in parallel
- **T095-T099** (Convection geometries): Can run in parallel

---

## Success Criteria

### Phase 1 (Setup) - Must Pass
- [ ] All directories created
- [ ] `pyproject.toml` correctly specifies all dependencies
- [ ] Package structure allows `import heat_calc`
- [ ] All ignore files in place

### Phase 2 (Foundational) - Must Pass
- [ ] Base models validate Pint Quantities correctly
- [ ] Validation JSON loads without errors
- [ ] CLI infrastructure accepts input files and produces output
- [ ] mypy runs without errors on foundational code

### Phase 3 (US1) - MVP Success Criteria
- **Functionality**: `calculate_lmtd()` computes correct values for all 3 configurations
- **Accuracy**: ≥ 85% of Incropera reference cases pass (within 1% tolerance)
- **Stability**: Edge cases handled gracefully (no crashes, warnings issued)
- **Testing**: Unit tests pass 100%, validation tests ≥ 85% pass rate
- **CLI**: `calculate-lmtd` accepts JSON/YAML, produces JSON/YAML/table output
- **Type Safety**: mypy --strict passes with 0 errors
- **Coverage**: ≥ 90% code coverage on lmtd module
- **Documentation**: Quickstart example works end-to-end

### Phase 4-6 (US2, US3, US4) - Similar Criteria
- Each story independently passes its acceptance scenarios
- All validation tests from reference literature pass
- Combined coverage across all modules ≥ 80%

### Phase 7 (Polish) - Final Validation
- Full test suite passes (unit + validation)
- mypy --strict on entire codebase: 0 errors
- Code formatting: black, isort, flake8 all pass
- Documentation complete and reviewed
- Performance benchmarks confirm <100ms per calculation

---

## Task Summary

| Phase | Tasks | Scope | Dependency |
|-------|-------|-------|-----------|
| P1: Setup | T001-T016 (16) | Project init, dependencies, structure | Must complete first |
| P2: Foundational | T017-T029 (13) | Shared models, CLI, validation data | Blocks all user stories |
| P3: US1 (LMTD) | T030-T061 (32) | MVP scope; independently testable | After P1+P2 |
| P4: US2 (NTU) | T062-T092 (31) | After P1+P2; can start after US1 |
| P5: US3 (Convection) | T093-T101 (9) | After P1+P2; can run parallel to US2 |
| P6: US4 (Insulation) | T102-T109 (8) | After P1+P2; can run parallel to US3 |
| P7: Polish | T110-T130 (21) | Testing, docs, performance, release | After all stories complete |
| **Total** | **130 tasks** | Full feature | Sequential phases; internal parallelization |

---

## Notes for Implementation

1. **User Story Independence**: Each story (US1, US2, US3, US4) is independently testable. You can deliver MVP (US1 only) and add stories incrementally.

2. **Test-First Pattern**: Tests (unit + validation) are listed in order. Implement test files first, then code to pass tests.

3. **Pydantic Validation**: All input/output models use Pydantic 2.x with validators. Test model instantiation before implementing calculation logic.

4. **Pint Integration**: All physical quantities carry units (e.g., `Quantity(100, "degC")`). Ensure serialization/deserialization handles Pint objects correctly.

5. **Type Safety**: mypy --strict is a hard requirement. Use `typing.Literal` for enums, `|` for unions, avoid `Any`.

6. **CLI Design**: Four separate commands, each wrapping its corresponding library function. CLI should accept JSON/YAML input and support multiple output formats.

7. **Properties Module**: Heat calculations depend on `001-data-foundations` properties abstraction. Prepare stub that accepts `FluidProperties` directly (constant properties), allowing future integration with CoolProp via properties module.

8. **Documentation**: See `quickstart.md` for usage examples. Docstrings use NumPy format. Include validation source (textbook page, NIST ID) in result objects and test comments.

