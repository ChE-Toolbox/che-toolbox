# Tasks: IAPWS-IF97 Steam Properties

**Feature**: 002-steam-properties | **Branch**: `002-steam-properties` | **Date**: 2025-12-30

**Input**: Design documents from `/specs/002-steam-properties/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/, research.md

**Organization**: Tasks are grouped by user story (US1-US4) to enable independent implementation and testing.

**Format**: `- [ ] [TaskID] [P?] [Story?] Description with file path`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure: `src/iapws_if97/`, `src/iapws_if97_cli/`, `tests/` per plan.md
- [ ] T002 [P] Initialize Python 3.11+ project with dependencies: NumPy 1.24+, SciPy 1.10+, Pint 0.23+, Pydantic 2.x in `setup.py` or `pyproject.toml`
- [ ] T003 [P] Configure linting and formatting: Black formatter, isort, flake8 configuration files
- [ ] T004 [P] Configure type checking: mypy --strict configuration in `mypy.ini` or `pyproject.toml`
- [ ] T005 [P] Setup pytest configuration in `pytest.ini` or `pyproject.toml` with test discovery
- [ ] T006 Create `src/iapws_if97/__init__.py` with public API exports (SteamTable, exceptions, ureg)
- [ ] T007 Create `src/iapws_if97/exceptions.py` with InputRangeError, NumericalInstabilityError, InvalidStateError classes

**Checkpoint**: Project structure initialized, dependencies installed, development tools configured

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure and shared utilities that MUST complete before any user story begins

**⚠️ CRITICAL**: No user story implementation can start until this phase completes

- [ ] T008 Create `src/iapws_if97/utils.py` with polynomial evaluation helpers (Horner's method) and NumPy integration
- [ ] T009 [P] Download and embed IAPWS-IF97 reference validation tables in `src/iapws_if97/validation/iapws_tables.json` (1300+ test points from official IAPWS)
- [ ] T010 [P] Create unit registry initialization: `src/iapws_if97/units.py` with Pint UnitRegistry singleton and SI unit definitions
- [ ] T011 Create `src/iapws_if97/constants.py` with critical point (22.064 MPa, 373.946 K), triple point, region boundaries, singularity threshold (0.05)
- [ ] T012 [P] Create base dataclasses: `src/iapws_if97/models.py` with Region (enum), SteamProperties, SaturationProperties (frozen dataclasses)
- [ ] T013 Create region routing logic: `src/iapws_if97/router.py` with function to assign region from (P, T) and validate inputs
- [ ] T014 [P] Setup SciPy integration: `src/iapws_if97/solver.py` with brentq root-finding wrapper and convergence criteria
- [ ] T015 Create test fixtures and IAPWS reference data loader: `tests/conftest.py` with pytest fixtures for reference tables

**Checkpoint**: Foundation ready - all core libraries, data, and utilities in place. User story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - P-T Property Lookups (Priority: P1) 🎯 MVP

**Goal**: Engineers can calculate steam/water properties (h, s, u, ρ) at any pressure-temperature conditions with ±0.03-0.2% accuracy

**Independent Test**: Verify properties at 3 test points (Region 1, Region 2, Region 3) match IAPWS reference values within specified accuracy

### Tests for User Story 1

- [ ] T016 [P] [US1] Create validation tests for Region 1 in `tests/unit/test_region1_validation.py` with ~400 reference points from IAPWS tables (6.8-863.91 MPa, ±0.03% tolerance)
- [ ] T017 [P] [US1] Create validation tests for Region 2 in `tests/unit/test_region2_validation.py` with ~400 reference points (0-100 MPa, ±0.06% tolerance)
- [ ] T018 [P] [US1] Create validation tests for Region 3 in `tests/unit/test_region3_validation.py` with ~200 reference points (16.6-100 MPa, ±0.2% tolerance)
- [ ] T019 [US1] Create integration test for complete P-T lookup workflow in `tests/integration/test_pt_workflow.py` (end-to-end from SteamTable.h_pt to Pint Quantity)

### Implementation for User Story 1

- [ ] T020 [P] [US1] Implement Region 1 equations: `src/iapws_if97/regions/region1.py` with IAPWS-IF97 polynomial coefficients and property calculation functions
- [ ] T021 [P] [US1] Implement Region 2 equations: `src/iapws_if97/regions/region2.py` with IAPWS-IF97 ideal gas + residual terms
- [ ] T022 [P] [US1] Implement Region 3 equations: `src/iapws_if97/regions/region3.py` with cubic equation of state for supercritical region
- [ ] T023 [US1] Create region dispatcher: `src/iapws_if97/dispatcher.py` that routes (P, T) to correct region and calls appropriate equations (depends on T020, T021, T022)
- [ ] T024 [US1] Implement SteamTable base class with P-T input validation: `src/iapws_if97/steam_table.py` lines 1-50 (constructor, input validation, region assignment)
- [ ] T025 [P] [US1] Implement SteamTable.h_pt() method in `src/iapws_if97/steam_table.py` returning enthalpy as Pint Quantity (kJ/kg)
- [ ] T026 [P] [US1] Implement SteamTable.s_pt() method in `src/iapws_if97/steam_table.py` returning entropy as Pint Quantity (kJ/(kg·K))
- [ ] T027 [P] [US1] Implement SteamTable.u_pt() method in `src/iapws_if97/steam_table.py` returning internal energy as Pint Quantity (kJ/kg)
- [ ] T028 [P] [US1] Implement SteamTable.rho_pt() method in `src/iapws_if97/steam_table.py` returning density as Pint Quantity (kg/m³)
- [ ] T029 [US1] Add singularity detection for Region 3: `src/iapws_if97/stability.py` with distance calculation from critical point and RuntimeError raising (depends on T022)
- [ ] T030 [US1] Add comprehensive error handling and messages in steam_table.py: InputRangeError for bounds, NumericalInstabilityError for singularities, structured message format

**Checkpoint**: User Story 1 complete. Engineers can calculate properties at any P-T condition. Run `tests/integration/test_pt_workflow.py` to verify independently.

---

## Phase 4: User Story 2 - Saturation Line Properties (Priority: P1)

**Goal**: Engineers can find saturation temperature/pressure and properties (h_f, h_g, ρ_f, ρ_g) at saturation line with ±0.1% accuracy

**Independent Test**: Verify saturation properties at 3 test pressures match IAPWS tables within ±0.1% tolerance

### Tests for User Story 2

- [ ] T031 [P] [US2] Create validation tests for saturation line in `tests/unit/test_saturation_validation.py` with ~300 reference points from IAPWS tables (0.611657 Pa-22.064 MPa, ±0.1% tolerance)
- [ ] T032 [US2] Create integration test for saturation workflow in `tests/integration/test_saturation_workflow.py` (T_sat and P_sat round-trip consistency check)

### Implementation for User Story 2

- [ ] T033 [US2] Implement Wagner-Pruss saturation pressure equation: `src/iapws_if97/regions/saturation.py` functions P_sat_direct(T) (does not require iteration)
- [ ] T034 [US2] Implement saturation temperature root-finding: `src/iapws_if97/regions/saturation.py` function T_sat(P) using scipy.optimize.brentq with Wagner-Pruss (depends on T014 SciPy solver, T033)
- [ ] T035 [P] [US2] Implement saturation property calculations: `src/iapws_if97/regions/saturation.py` functions for h_f, h_g, s_f, s_g, rho_f, rho_g at saturation
- [ ] T036 [US2] Implement SteamTable.T_sat(pressure) method: `src/iapws_if97/steam_table.py` returning SaturationProperties dataclass with T_sat, P_sat, liquid and vapor properties as Pint Quantities (depends on T034, T035)
- [ ] T037 [US2] Implement SteamTable.P_sat(temperature) method: `src/iapws_if97/steam_table.py` returning SaturationProperties dataclass (depends on T033, T035)
- [ ] T038 [US2] Add saturation line detection: InvalidStateError when user attempts P-T lookup on saturation line in steam_table.py validation

**Checkpoint**: User Story 2 complete. Engineers can query saturation properties. Both US1 and US2 should work independently.

---

## Phase 5: User Story 3 - Validation Against IAPWS Tables (Priority: P1)

**Goal**: System validates against official IAPWS-IF97 reference tables with documented accuracy for all regions and saturation line

**Independent Test**: Run full validation suite; all 1300+ reference points pass within specified accuracy tolerances (±0.03% R1, ±0.06% R2, ±0.2% R3, ±0.1% sat)

### Tests for User Story 3

- [ ] T039 [US3] Create comprehensive validation runner: `tests/validation/validate_all_regions.py` that loads IAPWS reference tables and reports accuracy statistics per region
- [ ] T040 [US3] Create edge case validation tests: `tests/validation/test_edge_cases.py` for critical point (22.064 MPa, 373.946 K), triple point (611.657 Pa, 273.16 K), region boundaries
- [ ] T041 [US3] Create singularity validation: `tests/validation/test_singularities.py` ensuring RuntimeError raised within 5% of critical point, convergence failures documented
- [ ] T042 [US3] Create accuracy reporting: `tests/validation/accuracy_report.py` generating summary table of error % per region for documentation

### Implementation for User Story 3

- [ ] T043 [US3] Run validation suite (T039-T042) against all regions; document and fix any accuracy issues (may require coefficient tuning)
- [ ] T044 [US3] Create `docs/validation_results.md` documenting test points used, accuracy achieved per region, methodology, deviations explained
- [ ] T045 [US3] Add docstrings to all region equation files documenting source (IAPWS-IF97 Release), coefficient origins, accuracy claims per requirement FR-012

**Checkpoint**: User Story 3 complete. System validated against official standards. All three P1 stories (US1, US2, US3) complete and independently testable.

---

## Phase 6: User Story 4 - SteamTable Convenience API (Priority: P2)

**Goal**: Python developers have clean, unit-aware SteamTable API for integration into larger applications; CLI available for scripting

**Independent Test**: Create sample script using SteamTable API with Pint Quantities; verify enthalpy, entropy, saturation lookups work without documentation reference

### Tests for User Story 4

- [ ] T046 [P] [US4] Create Python API tests: `tests/integration/test_steamtable_api.py` with examples from quickstart.md (Pint unit handling, method signatures, error catching)
- [ ] T047 [P] [US4] Create CLI tests: `tests/integration/test_cli_commands.py` with property, saturation, and batch subcommands
- [ ] T048 [US4] Create error message validation tests: `tests/unit/test_error_messages.py` ensuring InputRangeError, NumericalInstabilityError include parameter names and guidance

### Implementation for User Story 4

- [ ] T049 [US4] Polish SteamTable class with type hints and docstrings (NumPy style) in `src/iapws_if97/steam_table.py` (depends on completion of T025-T028, T036-T037)
- [ ] T050 [P] [US4] Create CLI wrapper: `src/iapws_if97_cli/cli.py` with click commands: property (--pressure, --temperature, --property), saturation (--pressure or --temperature), batch (--input, --output)
- [ ] T051 [P] [US4] Implement CLI output formatters: `src/iapws_if97_cli/formatters.py` with human-readable and JSON formatting options
- [ ] T052 [US4] Create CLI entry point: `setup.py` or `pyproject.toml` defining `steam-table` command (depends on T050, T051)
- [ ] T053 [US4] Create usage examples and documentation: `docs/cli_examples.md` with bash examples for scripting workflows
- [ ] T054 [US4] Add logging to library: `src/iapws_if97/logging_config.py` with region assignment, convergence info (DEBUG level) for troubleshooting

**Checkpoint**: User Story 4 complete. Python API and CLI both fully functional. All user stories (US1-US4) now complete.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple stories, documentation, quality assurance

- [ ] T055 [P] Run full linting and type checking: Black formatting, isort imports, flake8 checks, mypy --strict across all source files
- [ ] T056 [P] Run full test suite: pytest with coverage report; verify >80% coverage across `src/iapws_if97/`
- [ ] T057 [P] Generate coverage HTML report: `htmlcov/index.html` showing covered/uncovered lines
- [ ] T058 Create comprehensive documentation: `docs/design.md` explaining region equations, singularity handling, numerical methods per research.md decisions
- [ ] T059 Create API reference documentation: `docs/api_reference.md` with SteamTable method signatures, exception types, example code
- [ ] T060 Create installation and quickstart guide: `README.md` with pip install, basic Python usage, CLI examples from quickstart.md
- [ ] T061 [P] Performance profiling and optimization: `tests/benchmark/benchmark_performance.py` measuring calculation time per region; ensure <10ms target met
- [ ] T062 [P] Security audit: Check for input validation coverage, bounds checking, no external dependencies with known CVEs
- [ ] T063 Create CONTRIBUTING.md with development guidelines (type hints required, validation tests required, commit message conventions)
- [ ] T064 Validate against quickstart.md examples: Run all code examples in `docs/quickstart.md` to ensure they work end-to-end
- [ ] T065 Create CHANGELOG.md documenting version 1.0.0 release with features, breaking changes (none for MVP), known limitations

**Checkpoint**: All documentation complete, quality gates passed (linting, typing, testing), ready for release.

---

## Phase 8: Optional Future Enhancements (DEFERRED - Not MVP)

**Note**: These tasks are documented for future reference but NOT part of MVP scope (US1-US4 complete)

- [ ] T066 [P] [Future] Implement quality-based property lookups (P-h, T-s): `src/iapws_if97/regions/quality_calcs.py` (deferred to P3 per spec clarifications)
- [ ] T067 [Future] Add derivative calculations (cp, cv, speed of sound) as optional SteamProperties fields
- [ ] T068 [P] [Future] Create web calculator component: Static Next.js component with P/T inputs, property display
- [ ] T069 [Future] Implement batch vectorized calculations for NumPy array inputs
- [ ] T070 [Future] Add caching wrapper as separate utility module for user optimization

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - **BLOCKS all user stories**
- **User Story 1 (Phase 3)**: Depends on Foundational completion - Can run in parallel with US2-US4
- **User Story 2 (Phase 4)**: Depends on Foundational completion - Can run in parallel with US1, US3-US4
- **User Story 3 (Phase 5)**: Depends on US1 completion (needs working region equations) - Can run after US1
- **User Story 4 (Phase 6)**: Depends on US1 and US2 completion (API wraps working SteamTable) - Final story
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### Task Dependencies Within Stories

**User Story 1**:
- Models (T020-T022) can run in parallel
- Dispatcher (T023) depends on region implementations (T020-T022)
- Methods (T025-T028) depend on dispatcher (T023)
- Stability check (T029) depends on Region 3 (T022)
- Error handling (T030) last, depends on all P-T methods

**User Story 2**:
- Saturation equation (T033) and root-finding solver (T014 from Phase 2) are prerequisites
- T_sat/P_sat methods (T036-T037) depend on saturation equations (T033-T035)
- State detection (T038) depends on saturation implementation

**User Story 3**:
- Validation tests (T016-T018) can run in parallel after regions complete
- Accuracy report (T042) depends on all validation tests passing

**User Story 4**:
- CLI (T050-T052) depends on SteamTable API complete (US1, US2)
- Tests (T046-T048) can run after CLI implementation

### Parallel Opportunities

**Phase 1**: All [P] marked tasks (T002-T005) can run in parallel
**Phase 2**:
- Download reference tables (T009), unit registry (T010), dataclasses (T012), SciPy solver (T014) marked [P] - run in parallel
- Sequential requirement: T008 → T011, T013 → foundation complete

**Phase 3 (US1)**:
- Regions (T020-T022) marked [P] - implement in parallel on separate files
- Tests (T016-T018) marked [P] - write test fixtures in parallel, run tests together after regions complete

**Phase 4 (US2)**:
- Saturation property calcs (T035) marked [P] - separate h/s/rho calculations
- Can start immediately after Phase 2 (doesn't depend on US1 completion)

**Phase 5 (US3)**:
- Validation tests (T039-T042) can run in parallel
- Requires US1 complete for region implementations

**Phase 7**:
- All [P] marked tasks (T055-T057, T061-T062) run in parallel
- Documentation tasks sequential per standard workflow

### Parallel Team Strategy (Example: 4 Developers)

```
Timeline: Week 1-2
Developer A & B: Complete Phase 1 (Setup) + Phase 2 (Foundational) together [3-4 days]

Timeline: Week 2-4 (Parallel Stories)
Developer A: Complete User Story 1 (Phase 3) in parallel
Developer B: Complete User Story 2 (Phase 4) in parallel
Developer C: Complete User Story 3 (Phase 5) after US1 equations ready
Developer D: Complete User Story 4 (Phase 6) after US1+US2 ready

Timeline: Week 4-5
All developers: Phase 7 (Polish & testing) together
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Complete)

For **minimum viable product** delivering core P-T property calculations:

1. Complete Phase 1: Setup (1 day)
2. Complete Phase 2: Foundational (2 days)
3. Complete Phase 3: User Story 1 - P-T lookups (3-4 days)
4. **TEST US1 INDEPENDENTLY** - engineers can query properties at any P-T
5. Complete Phase 4: User Story 2 - Saturation (2-3 days)
6. **TEST US1 + US2 TOGETHER** - saturation queries work independently
7. Complete Phase 5: User Story 3 - Validation (2-3 days)
8. **RUN FULL VALIDATION SUITE** - all 1300+ points pass within tolerance

**MVP Checkpoint**: Deploy core library at this point. Basic P-T + saturation functionality works, validated against IAPWS.

### Incremental Delivery (Add US4 for Complete Release)

9. Complete Phase 6: User Story 4 - API & CLI (2 days)
10. **TEST US4** - SteamTable API works with Pint Quantities; CLI commands function
11. Complete Phase 7: Polish (2-3 days)
12. **RELEASE v1.0.0** with all features, documentation, passing quality gates

### Suggested Checkpoint Validations

After each phase/story, validate independently:

```bash
# After Phase 1: Dependencies installed
python -c "import numpy, scipy, pint, pydantic; print('Dependencies OK')"

# After Phase 2: Core libraries importable
python -c "from src.iapws_if97 import SteamTable, ureg; print('Foundation OK')"

# After Phase 3 (US1): Test P-T lookups
pytest tests/integration/test_pt_workflow.py -v

# After Phase 4 (US2): Test saturation
pytest tests/integration/test_saturation_workflow.py -v

# After Phase 5 (US3): Run validation
python tests/validation/validate_all_regions.py

# After Phase 6 (US4): Test API + CLI
pytest tests/integration/test_steamtable_api.py -v
pytest tests/integration/test_cli_commands.py -v

# After Phase 7: Full release readiness
pytest --cov=src/iapws_if97 --cov-report=html
mypy --strict src/
black --check src/
```

---

## Task Checklist Integrity

**Verification**: All tasks follow required format:
- [x] Every task has checkbox: `- [ ]`
- [x] Every task has Task ID: T001-T065
- [x] Parallel tasks marked [P] when safe
- [x] User story tasks marked [US1]-[US4]
- [x] Every task has description with file path
- [x] Tasks ordered by dependency
- [x] No circular dependencies
- [x] Each phase has clear purpose
- [x] Each story independently testable

---

## Summary Statistics

- **Total Tasks**: 65 (T001-T065)
- **Setup Phase**: 7 tasks
- **Foundational Phase**: 8 tasks
- **User Story 1 (P-T Lookups)**: 15 tasks
- **User Story 2 (Saturation)**: 8 tasks
- **User Story 3 (Validation)**: 4 tasks
- **User Story 4 (API/CLI)**: 10 tasks
- **Polish Phase**: 11 tasks
- **Future/Deferred**: 5 tasks (not in MVP)

**Parallel Opportunities**:
- Phase 1: 4 tasks can run in parallel
- Phase 2: 4 tasks can run in parallel
- Phase 3: 7 regions + tests can run in parallel
- Phase 7: 5 tasks can run in parallel
- **Maximum parallelization**: 3-4 developers can work simultaneously after Phase 2

**MVP Scope** (P1 Stories 1-3):
- Phases 1-5: 38 tasks
- Estimated effort: 10-12 developer-days
- Delivers: Full P-T and saturation calculations, validated against IAPWS

**Full Release** (All Stories 1-4):
- Phases 1-7: 55 tasks
- Estimated effort: 14-16 developer-days
- Delivers: Complete library, Python API, CLI, documentation, quality gates passed

---

## Notes

- Each task is specific enough for LLM execution without additional context
- File paths match project structure from plan.md
- Dependencies between tasks explicitly documented
- Validation tests intentionally early (TDD: write failing tests first)
- Each user story independently testable per spec.md requirements
- Parallel-safe [P] tasks don't modify same files or have dependencies
- Story labels [US1]-[US4] map exactly to spec.md user stories
- All exception handling (InputRangeError, NumericalInstabilityError) integrated throughout appropriate tasks
- Singularity detection and edge case handling (critical point, triple point) explicit in Task T029 (US1) and T040-T041 (US3)
