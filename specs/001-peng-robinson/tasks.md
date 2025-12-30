# Tasks: Peng-Robinson EOS Thermodynamic Engine

**Input**: Design documents from `/specs/001-peng-robinson/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are explicitly requested in the specification and validation is a co-equal priority feature (User Story 4 - P1).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

Single project structure: `src/`, `tests/`, `data/` at repository root per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure per plan.md

- [X] T001 Create project directory structure: src/{eos,compounds,validation,cli}/, tests/{unit,validation,integration}/, data/{nist_reference}/
- [X] T002 Initialize Python project with pyproject.toml including dependencies: NumPy 1.24+, SciPy 1.10+, Pint 0.23+, Pydantic 2.x, pytest 7.x+, mypy 1.0+
- [X] T003 [P] Configure mypy for strict type checking in pyproject.toml
- [X] T004 [P] Configure pytest with coverage settings in pyproject.toml (target >80%)
- [X] T005 [P] Setup ruff for linting and formatting in pyproject.toml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models, utilities, and infrastructure that MUST be complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Create PhaseType enum in src/eos/models.py (VAPOR, LIQUID, SUPERCRITICAL, TWO_PHASE, UNKNOWN)
- [X] T007 [P] Implement Compound Pydantic model in src/compounds/models.py with validators for Tc>0, Pc>0, -1<ω<2
- [X] T008 [P] Implement Mixture Pydantic model in src/eos/models.py with validators for mole fraction sum=1.0±1e-6
- [X] T009 [P] Implement ThermodynamicState Pydantic model in src/eos/models.py with temperature, pressure, composition fields
- [X] T010 [P] Implement ValidationTestCase Pydantic model in src/validation/models.py
- [X] T011 [P] Implement BinaryInteractionParameter Pydantic model in src/eos/models.py
- [X] T012 Implement CompoundDatabase class in src/compounds/database.py with get(), get_by_cas(), list_compounds(), add_compound() methods
- [X] T013 Create data/compounds.json with critical properties for 5 compounds: methane, ethane, propane, n-butane, water (Tc, Pc, ω from research.md)
- [X] T014 [P] Create custom ConvergenceWarning exception class in src/eos/exceptions.py with best_estimate and residual attributes
- [X] T015 [P] Setup Pint unit registry and configure temperature/pressure unit handling in src/eos/units.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Pure Component Property Calculation (Priority: P1) 🎯 MVP

**Goal**: Calculate compressibility factor (Z) and fugacity for pure components at specified T, P to enable real gas corrections for process design

**Independent Test**: Provide T, P, compound identifier → compare calculated Z and fugacity against NIST reference data (within 5% for Z, 10% for fugacity)

### Implementation for User Story 1

- [X] T016 [P] [US1] Implement analytical cubic formula solver (Cardano's method) in src/eos/cubic_solver.py with function solve_cubic_analytical(a, b, c, d) -> tuple[float, ...]
- [X] T017 [P] [US1] Implement NumPy-based cubic solver in src/eos/cubic_solver.py with function solve_cubic_numpy(a, b, c, d) -> tuple[float, ...]
- [X] T018 [US1] Implement hybrid cubic solver in src/eos/cubic_solver.py with function solve_cubic(a, b, c, d, method="hybrid") combining NumPy with analytical fallback
- [X] T019 [US1] Implement Peng-Robinson EOS parameters calculation in src/eos/peng_robinson.py: functions calculate_a(Tc, Pc, omega, T), calculate_b(Tc, Pc)
- [X] T020 [US1] Implement Z factor calculation for pure components in src/eos/peng_robinson.py: method PengRobinsonEOS.calculate_z_factor(T, P, compound) using cubic solver, returns sorted tuple (smallest=liquid, largest=vapor)
- [X] T021 [US1] Implement fugacity coefficient calculation for pure components in src/eos/peng_robinson.py: method PengRobinsonEOS.calculate_fugacity_coefficient(T, P, compound, phase=None)
- [X] T022 [US1] Implement phase identification logic in src/eos/peng_robinson.py: determine VAPOR/LIQUID/SUPERCRITICAL/TWO_PHASE based on T/Tc, P/Pc, number of real roots
- [X] T023 [US1] Implement calculate_state() convenience method in src/eos/peng_robinson.py returning complete ThermodynamicState object
- [X] T024 [US1] Add input validation in PengRobinsonEOS methods: raise ValueError for T≤0, P≤0, invalid critical properties
- [X] T025 [US1] Add logging for calculation steps and phase identification in src/eos/peng_robinson.py

**Checkpoint**: At this point, User Story 1 should be fully functional - can calculate Z and fugacity for pure components

---

## Phase 4: User Story 2 - Vapor Pressure Prediction (Priority: P2)

**Goal**: Calculate saturation pressure at given temperature for pure components to enable phase boundary predictions and equipment design

**Independent Test**: Request vapor pressure at specified T → compare against NIST saturation pressure data (within 5%)

### Implementation for User Story 2

- [ ] T026 [US2] Implement fugacity equality residual function in src/eos/peng_robinson.py: calculate residual for vapor pressure iteration (f_vapor - f_liquid)
- [ ] T027 [US2] Implement vapor pressure calculation using SciPy brentq in src/eos/peng_robinson.py: method PengRobinsonEOS.calculate_vapor_pressure(T, compound) with bracket [1e-6*Pc, 0.999*Pc], max_iterations=100
- [ ] T028 [US2] Add convergence failure handling in calculate_vapor_pressure(): raise ConvergenceWarning with best estimate after max_iterations
- [ ] T029 [US2] Add validation for supercritical conditions: raise ValueError if T ≥ Tc (no vapor pressure exists)
- [ ] T030 [US2] Extend calculate_state() to include vapor pressure calculation for subcritical pure components

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - can calculate properties and vapor pressure

---

## Phase 5: User Story 3 - Mixture Property Calculation (Priority: P3)

**Goal**: Calculate thermodynamic properties for multi-component mixtures using van der Waals mixing rules to enable realistic process simulations

**Independent Test**: Provide T, P, multi-component composition → compare calculated mixture properties against NIST reference data (within 5%)

### Implementation for User Story 3

- [ ] T031 [P] [US3] Implement van der Waals mixing rule for parameter 'a' in src/eos/mixing_rules.py: calculate_a_mix(compounds, mole_fractions, T, kij_matrix) with geometric mean a_ij = (1-kij)*sqrt(ai*aj)
- [ ] T032 [P] [US3] Implement van der Waals mixing rule for parameter 'b' in src/eos/mixing_rules.py: calculate_b_mix(compounds, mole_fractions) = Σ xi*bi
- [ ] T033 [US3] Implement Mixture.from_names() class method in src/eos/models.py to construct mixture from compound names using CompoundDatabase
- [ ] T034 [US3] Extend PengRobinsonEOS.calculate_z_factor() to handle Mixture composition using mixing rules
- [ ] T035 [US3] Extend PengRobinsonEOS.calculate_fugacity_coefficient() to handle Mixture composition and return component fugacity coefficients
- [ ] T036 [US3] Add composition validation in Mixture model: verify mole fractions sum to 1.0±1e-6, no negative values, no NaN
- [ ] T037 [US3] Add binary interaction parameter validation: verify -0.5 < kij < 0.5, ensure symmetry (kij = kji)
- [ ] T038 [US3] Create data/binary_interaction_params.json with literature kij values for common pairs (methane-ethane, methane-propane, ethane-propane)

**Checkpoint**: All calculation user stories (1-3) should now be independently functional

---

## Phase 6: User Story 4 - Validation Against Reference Data (Priority: P1)

**Goal**: Verify Peng-Robinson implementation accuracy against NIST WebBook data to ensure calculations are reliable for engineering use

**Independent Test**: Run automated test suite comparing calculations against NIST data across T and P ranges with automated pass/fail criteria (≥95% within tolerance)

### NIST Data Collection

- [ ] T039 [P] [US4] Create NIST reference data JSON for methane in data/nist_reference/methane.json (50 test points: Z factor, fugacity across 200-500 K, 1-100 bar)
- [ ] T040 [P] [US4] Create NIST reference data JSON for ethane in data/nist_reference/ethane.json (50 test points across valid range)
- [ ] T041 [P] [US4] Create NIST reference data JSON for propane in data/nist_reference/propane.json (50 test points across valid range)
- [ ] T042 [P] [US4] Create NIST reference data JSON for n-butane in data/nist_reference/n_butane.json (50 test points across valid range)
- [ ] T043 [P] [US4] Create NIST reference data JSON for water in data/nist_reference/water.json (50 test points across valid range)

### Validation Infrastructure

- [ ] T044 [US4] Implement NISTDataLoader class in src/validation/nist_data.py to load and parse NIST reference JSON files
- [ ] T045 [US4] Implement ValidationResult data class in src/validation/models.py to store test results (passed, failed, deviations)
- [ ] T046 [US4] Implement NISTValidation class in src/validation/validator.py with validate_z_factor(), validate_fugacity(), validate_vapor_pressure() methods
- [ ] T047 [US4] Implement validation report generator in src/validation/reporter.py: generate summary with pass rates, max/min/avg deviations
- [ ] T048 [US4] Create pytest validation test suite in tests/validation/test_nist_pure_components.py for all 5 compounds (parametrized tests)
- [ ] T049 [P] [US4] Create pytest validation test suite in tests/validation/test_nist_mixtures.py for binary/ternary mixtures (if NIST mixture data available)

### Unit Tests (Supporting US1-US4)

- [ ] T050 [P] [US4] Create unit tests for cubic solver in tests/unit/test_cubic_solver.py: test analytical, numpy, hybrid methods with known roots
- [ ] T051 [P] [US4] Create unit tests for Peng-Robinson core in tests/unit/test_peng_robinson.py: test parameter calculation, Z factor edge cases
- [ ] T052 [P] [US4] Create unit tests for mixing rules in tests/unit/test_mixing_rules.py: test a_mix, b_mix calculations
- [ ] T053 [P] [US4] Create unit tests for CompoundDatabase in tests/unit/test_compounds.py: test get(), add_compound(), validation
- [ ] T054 [P] [US4] Create unit tests for Pydantic models in tests/unit/test_models.py: test validators, edge cases

**Checkpoint**: Complete validation suite operational - can verify accuracy across all compounds and properties

---

## Phase 7: User Story Integration & CLI (Cross-cutting)

**Purpose**: Integrate all user stories through unified Python API and CLI interfaces

### Python API Finalization

- [ ] T055 Setup public API exports in src/eos/__init__.py: export PengRobinsonEOS, PhaseType
- [ ] T056 [P] Setup public API exports in src/compounds/__init__.py: export CompoundDatabase, Compound
- [ ] T057 [P] Setup public API exports in src/eos/models.py: export Mixture, ThermodynamicState
- [ ] T058 [P] Setup public API exports in src/validation/__init__.py: export NISTValidation (for advanced users)

### CLI Implementation (Contracts from contracts/cli_interface.md)

- [ ] T059 [P] Implement 'pr-calc z-factor' command in src/cli/pr_calc.py with argparse: pure component and mixture support, unit conversion
- [ ] T060 [P] Implement 'pr-calc fugacity' command in src/cli/pr_calc.py: output fugacity coefficient and fugacity value
- [ ] T061 [P] Implement 'pr-calc vapor-pressure' command in src/cli/pr_calc.py: subcritical check, convergence warnings
- [ ] T062 [P] Implement 'pr-calc state' command in src/cli/pr_calc.py: complete state output with all properties
- [ ] T063 [P] Implement 'pr-calc mixture' command in src/cli/pr_calc.py: load mixture JSON, calculate properties
- [ ] T064 [P] Implement 'pr-calc validate' command in src/cli/pr_calc.py: run NIST validation suite, generate report
- [ ] T065 [P] Implement 'pr-calc list-compounds' command in src/cli/pr_calc.py: display available compounds with properties
- [ ] T066 Add CLI output formatting in src/cli/formatters.py: text format (human-readable) and JSON format
- [ ] T067 Add CLI error handling and exit codes in src/cli/pr_calc.py: 0=success, 1=invalid input, 2=calc failure, 3=convergence warning, 4=validation failure
- [ ] T068 Create CLI entry point script in pyproject.toml: register 'pr-calc' command

### Integration Tests

- [ ] T069 [P] Create integration test for pure component workflow in tests/integration/test_pure_component.py: get compound → calculate Z → calculate fugacity
- [ ] T070 [P] Create integration test for vapor pressure workflow in tests/integration/test_vapor_pressure.py: calculate Psat → verify phase equilibrium
- [ ] T071 [P] Create integration test for mixture workflow in tests/integration/test_mixture.py: create mixture → calculate properties
- [ ] T072 [P] Create integration test for CLI commands in tests/integration/test_cli.py: test all pr-calc commands with subprocess

**Checkpoint**: Full system operational - Python API and CLI both functional for all user stories

---

## Phase 8: Documentation & Polish

**Purpose**: User-facing documentation, code quality improvements, and quickstart validation

- [ ] T073 [P] Add NumPy-style docstrings to all public methods in src/eos/peng_robinson.py
- [ ] T074 [P] Add NumPy-style docstrings to all public methods in src/compounds/database.py
- [ ] T075 [P] Add NumPy-style docstrings to all mixing rules functions in src/eos/mixing_rules.py
- [ ] T076 Create API reference documentation in docs/api_reference.md based on contracts/python_api.md
- [ ] T077 [P] Create theory documentation in docs/theory.md: PR-EOS derivation, mixing rules explanation
- [ ] T078 [P] Create troubleshooting guide in docs/troubleshooting.md: convergence issues, edge cases
- [ ] T079 Create README.md at repository root: installation, quick start, examples
- [ ] T080 Validate all examples from specs/001-peng-robinson/quickstart.md work correctly: run and verify output
- [ ] T081 Run full test suite and verify >80% code coverage: pytest --cov=src --cov-report=html
- [ ] T082 Run mypy strict type checking and fix any issues: mypy --strict src/
- [ ] T083 Run ruff linting and fix any issues: ruff check . --fix
- [ ] T084 Performance profiling: verify Z factor <1ms, fugacity <2ms, vapor pressure <50ms, validation suite <60s

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) completion
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2) completion - can run parallel to US1
- **User Story 3 (Phase 5)**: Depends on Foundational (Phase 2) completion - can run parallel to US1, US2
- **User Story 4 (Phase 6)**: Depends on US1, US2, US3 implementation completion (needs code to validate)
- **CLI Integration (Phase 7)**: Depends on US1, US2, US3 completion
- **Documentation (Phase 8)**: Depends on all implementation phases

### User Story Dependencies

- **US1 (P1 - Pure Components)**: Independent - can start after Foundational
- **US2 (P2 - Vapor Pressure)**: Builds on US1 (uses Z factor and fugacity) - sequential dependency
- **US3 (P3 - Mixtures)**: Extends US1 (uses core PR-EOS but adds mixing rules) - can develop in parallel with US2
- **US4 (P1 - Validation)**: Co-equal priority with US1 but needs US1-US3 implemented to validate

### Recommended Execution Order

**Option 1: Sequential MVP-First**
1. Phase 1: Setup (T001-T005)
2. Phase 2: Foundational (T006-T015) ← CRITICAL GATE
3. Phase 3: User Story 1 (T016-T025) ← MVP!
4. Phase 4: User Story 2 (T026-T030)
5. Phase 5: User Story 3 (T031-T038)
6. Phase 6: User Story 4 (T039-T054)
7. Phase 7: CLI Integration (T055-T072)
8. Phase 8: Documentation (T073-T084)

**Option 2: Parallel Development (with team)**
1. Complete Phase 1 + 2 together
2. Split team:
   - Developer A: US1 (T016-T025)
   - Developer B: US3 (T031-T038) in parallel (independent of US2)
3. Sequential: US2 (T026-T030) after US1 complete
4. Team: US4 validation (T039-T054) after all implementations
5. Parallel: CLI commands (T059-T068)
6. Parallel: Documentation tasks (T073-T084)

### Within Each User Story

**US1 Pattern:**
- Parallel: Cubic solvers (T016, T017) → Hybrid (T018)
- Sequential: Parameters (T019) → Z factor (T020) → Fugacity (T021) → Phase ID (T022) → State (T023)

**US2 Pattern:**
- Sequential: Residual function (T026) → Brent's method (T027) → Error handling (T028-T029) → Integration (T030)

**US3 Pattern:**
- Parallel: Mixing rules (T031, T032), Mixture model (T033)
- Sequential: Extend Z factor (T034) → Extend fugacity (T035) → Validation (T036-T037)

**US4 Pattern:**
- Parallel: All NIST data files (T039-T043)
- Sequential: Loader (T044) → Result model (T045) → Validator (T046) → Reporter (T047)
- Parallel: All test suites (T048-T054)

### Parallel Opportunities

**Setup Phase:**
- T003, T004, T005 (all config files)

**Foundational Phase:**
- T007, T008, T009, T010, T011 (all Pydantic models)
- T014, T015 (exception + units)

**US1:**
- T016, T017 (two solver implementations)

**US3:**
- T031, T032 (mixing rules for a and b)

**US4:**
- T039-T043 (all 5 NIST data files)
- T050-T054 (all unit test files)

**CLI:**
- T059-T065, T067 (all CLI commands)
- T069-T072 (all integration tests)

**Documentation:**
- T073-T075, T077-T078 (docstrings and docs)

---

## Parallel Example: User Story 1 Core Implementation

```bash
# After Foundational phase complete, launch in parallel:
Task T016: "Implement analytical cubic solver in src/eos/cubic_solver.py"
Task T017: "Implement NumPy cubic solver in src/eos/cubic_solver.py"

# Then sequential:
Task T018: "Hybrid solver combining both" (depends on T016, T017)
Task T019: "PR-EOS parameters a, b calculation"
Task T020: "Z factor calculation using cubic solver" (depends on T018, T019)
Task T021: "Fugacity calculation" (depends on T020)
```

---

## Implementation Strategy

### MVP First (User Story 1 + Validation Core)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T015) ← BLOCKS everything
3. Complete Phase 3: User Story 1 (T016-T025) ← DELIVERS MVP
4. Complete Phase 6 (partial): US4 validation for US1 only (T039-T043 for methane only, T044-T048)
5. **STOP and VALIDATE**: Does pure component calculation work? Does it match NIST?
6. If yes → Deploy MVP / Demo capability

### Incremental Delivery

1. **Milestone 1**: Setup + Foundational → Foundation ready
2. **Milestone 2**: + User Story 1 → Pure component Z and fugacity (MVP!) → Test independently → Deploy/Demo
3. **Milestone 3**: + User Story 2 → Vapor pressure prediction → Test independently → Deploy/Demo
4. **Milestone 4**: + User Story 3 → Mixture calculations → Test independently → Deploy/Demo
5. **Milestone 5**: + User Story 4 → Full validation suite → Generate accuracy report → Publish results
6. **Milestone 6**: + CLI → Command-line interface → Deploy CLI tool
7. **Milestone 7**: + Documentation → User-ready package

### Success Criteria Per Phase

**Phase 1-2 Success**: Can import modules, create Compound objects, database loads
**Phase 3 Success**: Can calculate Z factor and fugacity for methane at 300 K, 50 bar
**Phase 4 Success**: Can calculate vapor pressure for water at 373.15 K ≈ 1.013 bar
**Phase 5 Success**: Can calculate properties for 85% CH4 + 15% C2H6 mixture
**Phase 6 Success**: ≥95% of Z factor tests pass, ≥90% of fugacity tests pass
**Phase 7 Success**: All CLI commands work, return correct JSON/text output
**Phase 8 Success**: All quickstart.md examples work, mypy passes, coverage >80%

---

## Notes

- **[P] tasks** = different files, can run in parallel
- **[Story] label** maps task to specific user story for traceability
- Each user story should be independently completable and testable after Foundational phase
- US2 extends US1 (uses fugacity calculation) - sequential dependency
- US3 can develop in parallel with US2 (independent mixing rules)
- US4 validates all stories - must come after US1-US3 implementation
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- NIST data collection (T039-T043) can be done incrementally as needed
- Target metrics: Z factor <5% deviation, fugacity <10% deviation, vapor pressure <5% deviation
