# Tasks: Chemical Database Data Foundations

**Input**: Design documents from `/specs/001-data-foundations/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/compound_api.py ✓

**Tests**: This feature INCLUDES validation test tasks as required by Constitution Principle III (Validation-First Development). While the spec template indicates tests are optional, the constitution mandates validation tests for all calculations/data against authoritative sources. FR-004 explicitly requires NIST validation tests.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single library project**: `packages/core/src/chemeng_core/`, `packages/core/tests/`
- Paths shown below follow plan.md structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create module directories: packages/core/src/chemeng_core/compounds/, packages/core/src/chemeng_core/units/, packages/core/src/chemeng_core/data/compounds/
- [X] T002 Create test directory structure: packages/core/tests/unit/, packages/core/tests/validation/
- [X] T003 Create __init__.py files for all new modules: chemeng_core/compounds/__init__.py, chemeng_core/units/__init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 [P] Implement Pydantic QuantityDTO model with to_pint/from_pint methods in packages/core/src/chemeng_core/compounds/models.py
- [X] T005 [P] Create Pint UnitRegistry singleton with chemical engineering units in packages/core/src/chemeng_core/units/registry.py
- [X] T006 [P] Implement UnitHandler class with convert, convert_quantity, is_compatible, parse_unit methods in packages/core/src/chemeng_core/units/handler.py
- [X] T007 Create JSON schema validator using Pydantic models in packages/core/src/chemeng_core/compounds/validation.py
- [X] T008 Add custom exception classes (CompoundNotFoundError, DimensionalityError, ValidationError) to packages/core/src/chemeng_core/compounds/exceptions.py
- [X] T009 Configure pytest with pytest-cov plugin in packages/core/pyproject.toml
- [X] T010 Set pytest coverage threshold to 80% minimum in packages/core/pyproject.toml
- [X] T011 Configure mypy with --strict mode in packages/core/pyproject.toml
- [X] T012 Create pytest.ini or pyproject.toml [tool.pytest.ini_options] with validation marker

**Checkpoint**: Foundation ready - all quality gates configured (type checking, test coverage, validation markers) - user story implementation can now begin in parallel

---

## Phase 2.5: NIST Validation Test Suite (Constitution-Mandated)

**Purpose**: Validate all compound data against authoritative NIST WebBook sources per Constitution Principle III

**⚠️ CONSTITUTION REQUIREMENT**: These tests are NON-NEGOTIABLE per Principle III: "Each calculation must have at least one validation test comparing output to literature values within acceptable tolerance"

**Test Pattern**: Each test loads compound from database, compares critical properties to NIST reference values, asserts within defined tolerance.

**Tolerances** (from research.md):
- Critical temperature/pressure: ±0.01% (relative)
- Critical density: ±0.1% (relative)
- Acentric factor: ±1% (relative)
- Normal boiling point: ±0.1% (relative)

### Validation Tests (Write First - Must FAIL Before Data Generation)

- [X] T013 [P] Create validation test for Water (H2O) critical properties in packages/core/tests/validation/test_nist_water.py
- [X] T014 [P] Create validation test for Methane (CH4) critical properties in packages/core/tests/validation/test_nist_methane.py
- [X] T015 [P] Create validation test for Ethane (C2H6) critical properties in packages/core/tests/validation/test_nist_ethane.py
- [X] T016 [P] Create validation test for Propane (C3H8) critical properties in packages/core/tests/validation/test_nist_propane.py
- [X] T017 [P] Create validation test for Ammonia (NH3) critical properties in packages/core/tests/validation/test_nist_ammonia.py
- [X] T018 [P] Create validation test for Carbon Dioxide (CO2) critical properties in packages/core/tests/validation/test_nist_co2.py
- [X] T019 [P] Create validation test for Nitrogen (N2) critical properties in packages/core/tests/validation/test_nist_nitrogen.py
- [X] T020 [P] Create validation test for Oxygen (O2) critical properties in packages/core/tests/validation/test_nist_oxygen.py
- [X] T021 [P] Create validation test for Hydrogen (H2) critical properties in packages/core/tests/validation/test_nist_hydrogen.py
- [X] T022 [P] Create validation test for Helium (He) critical properties in packages/core/tests/validation/test_nist_helium.py

### Validation Test Execution

- [X] T023 Run all validation tests with pytest -m validation - VERIFY ALL FAIL (no data exists yet)
- [X] T024 Document NIST WebBook reference URLs for all 10 compounds in test docstrings

**Checkpoint**: All validation tests written and confirmed failing - ready for data generation in US1

**Dependencies**:
- Depends on T009-T012 (pytest/mypy configuration)
- BLOCKS Phase 3 (US1) - validation tests must exist and fail before implementing data loading

---

## Phase 3: User Story 1 - Load and Validate Chemical Compound Data (Priority: P1) 🎯 MVP

**Goal**: Provide access to thermophysical properties of 10 common compounds with NIST attribution

**Independent Test**: Can load a single compound (e.g., water) from the database, retrieve its properties, and verify proper attribution metadata is present

### Implementation for User Story 1

- [X] T025 [P] [US1] Create CriticalPropertiesDTO Pydantic model in packages/core/src/chemeng_core/compounds/models.py
- [X] T026 [P] [US1] Create PhasePropertiesDTO Pydantic model in packages/core/src/chemeng_core/compounds/models.py
- [X] T027 [P] [US1] Create SourceAttributionDTO Pydantic model in packages/core/src/chemeng_core/compounds/models.py
- [X] T028 [US1] Create CompoundDTO Pydantic model with all nested properties in packages/core/src/chemeng_core/compounds/models.py
- [X] T029 [US1] Create DatabaseMetadataDTO and CompoundDatabaseDTO models in packages/core/src/chemeng_core/compounds/models.py
- [X] T030 [US1] Implement JSONCompoundLoader class with load and validate methods in packages/core/src/chemeng_core/compounds/loader.py
- [X] T031 [US1] Create CoolProp data extraction script to generate compound data for all 10 compounds in scripts/generate_compound_data.py
- [X] T032 [US1] Run data extraction script to generate packages/core/src/chemeng_core/data/compounds/compounds.json with all 10 compounds (Methane, Ethane, Propane, Water, Ammonia, CO2, N2, O2, H2, He)
- [X] T033 [US1] Re-run validation tests (pytest -m validation) - VERIFY ALL PASS after data generation
- [X] T034 [US1] Implement CompoundRegistry class with in-memory indexing (CAS, name, formula, aliases) in packages/core/src/chemeng_core/compounds/registry.py - Design for future tiered access (JSON → CoolProp → user data)
- [X] T035 [US1] Implement get_by_cas, get_by_name, get_by_formula, search, list_all methods in packages/core/src/chemeng_core/compounds/registry.py
- [X] T036 [US1] Implement create_registry factory function in packages/core/src/chemeng_core/compounds/__init__.py
- [X] T037 [US1] Implement get_compound convenience function in packages/core/src/chemeng_core/compounds/__init__.py
- [X] T038 [US1] Update packages/core/src/chemeng_core/__init__.py to expose compounds module public API
- [X] T039 [US1] Validate all 10 compounds load correctly and contain complete attribution metadata (manual verification using Python REPL)

**Checkpoint**: At this point, User Story 1 should be fully functional AND all validation tests pass - can load any of the 10 compounds with NIST-validated properties

---

## Phase 4: User Story 2 - Perform Unit Conversions for Chemical Properties (Priority: P2)

**Goal**: Enable conversion between different unit systems (SI, Imperial, engineering units) for thermophysical properties

**Independent Test**: Can take a property value in one unit system (e.g., density in kg/m³) and convert it to another (e.g., lb/ft³), verifying mathematical correctness and dimensional consistency

### Implementation for User Story 2

- [X] T040 [US2] Implement PintUnitHandler class implementing UnitHandler protocol in packages/core/src/chemeng_core/units/handler.py
- [X] T041 [US2] Implement convert method for scalar unit conversions in packages/core/src/chemeng_core/units/handler.py
- [X] T042 [US2] Implement convert_quantity method for QuantityDTO conversions in packages/core/src/chemeng_core/units/handler.py
- [X] T043 [US2] Implement is_compatible method for dimensional checking in packages/core/src/chemeng_core/units/handler.py
- [X] T044 [US2] Implement parse_unit method for unit string parsing in packages/core/src/chemeng_core/units/handler.py
- [X] T045 [US2] Add DimensionalityError exception handling to all conversion methods in packages/core/src/chemeng_core/units/handler.py
- [X] T046 [US2] Implement create_unit_handler factory function in packages/core/src/chemeng_core/units/__init__.py
- [X] T047 [US2] Update packages/core/src/chemeng_core/__init__.py to expose units module public API
- [X] T048 [US2] Verify conversions for at least 12 common unit pairs (manual testing: K/°C/°F, Pa/bar/psi, kg/m³/lb/ft³, J/cal)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - can load compounds and convert their property units independently

---

## Phase 5: User Story 3 - Add New Chemical Compounds to Database (Priority: P3)

**Goal**: Provide utilities to extend the database beyond the initial 10 compounds

**Independent Test**: Can use data loading utilities to add an 11th compound with properties sourced from NIST/CoolProp and verify it passes the same validation as the initial compounds

### Implementation for User Story 3

- [X] T049 [US3] Create CoolPropDataExtractor class to fetch properties from CoolProp API in packages/core/src/chemeng_core/compounds/extractor.py
- [X] T050 [US3] Implement extract_compound_data method that takes CoolProp name and returns CompoundDTO in packages/core/src/chemeng_core/compounds/extractor.py
- [X] T051 [US3] Implement fetch_critical_properties helper method in packages/core/src/chemeng_core/compounds/extractor.py
- [X] T052 [US3] Implement fetch_phase_properties helper method in packages/core/src/chemeng_core/compounds/extractor.py
- [X] T053 [US3] Implement fetch_molecular_weight helper method in packages/core/src/chemeng_core/compounds/extractor.py
- [X] T054 [US3] Create add_compound_to_database utility function that validates and appends to compounds.json in packages/core/src/chemeng_core/compounds/loader.py
- [X] T055 [US3] Implement database file read, append, validate, and write logic in packages/core/src/chemeng_core/compounds/loader.py
- [X] T056 [US3] Add command-line interface script for adding compounds: scripts/add_compound.py
- [X] T057 [US3] Document compound addition process in packages/core/src/chemeng_core/data/compounds/README.md
- [X] T058 [US3] Test adding an 11th compound (e.g., Argon or Benzene) and verify it validates and loads correctly

**Checkpoint**: All user stories should now be independently functional - can load compounds, convert units, and add new compounds

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and finalize deliverable

- [X] T059 [P] Add NumPy-style docstrings to all public functions and classes in compounds module
- [X] T060 [P] Add NumPy-style docstrings to all public functions and classes in units module
- [X] T061 [P] Create automated test suite for SC-004: verify 12+ unit conversion pairs in packages/core/tests/unit/test_unit_conversions.py
- [X] T062 [P] Create schema rejection test suite for SC-005: test malformed compound data in packages/core/tests/unit/test_schema_validation.py
- [X] T063 Add numerical precision verification for SC-007: verify 6 significant figures in packages/core/tests/validation/test_precision.py
- [X] T064 Create data attribution documentation in packages/core/src/chemeng_core/data/compounds/ATTRIBUTION.md with full NIST WebBook and CoolProp citations
- [ ] T065 Update packages/core/README.md to document the compounds and units modules
- [X] T066 Verify all 10 compounds have complete and accurate NIST source attribution (manual inspection of compounds.json)
- [X] T067 Run quickstart.md validation - execute all code examples from specs/001-data-foundations/quickstart.md
- [X] T068 Verify performance goals: property lookup <10ms, compound loading <100ms (manual timing tests)
- [X] T069 Verify data file size <100KB total (check compounds.json file size)
- [X] T070 Code cleanup: remove any debug print statements, ensure consistent formatting with ruff
- [X] T071 Final validation: Run full test suite (pytest), verify >80% coverage, all validation tests pass, no runtime errors

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - configures quality gates (T009-T012)
- **Validation Tests (Phase 2.5)**: Depends on Foundational - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Phase 2.5 completion
  - User Story 1 (P1): Can start after validation tests written - must make tests pass
  - User Story 2 (P2): Can start after Foundational - uses models from US1 but independently testable
  - User Story 3 (P3): Can start after User Story 1 complete
- **Polish (Phase 6)**: Depends on all user stories being complete

### Critical Flow (Constitution-Compliant)

```
Setup (T001-T003)
  ↓
Foundational + Quality Gates (T004-T012)
  ↓
Write Validation Tests - Must FAIL (T013-T024)
  ↓
Implement User Story 1 - Make Tests PASS (T025-T039)
  ↓
User Story 2 & 3 (parallel possible)
  ↓
Polish + Additional Tests (T059-T071)
```

### Red-Green-Refactor Workflow

Per Constitution Principle III: "When adding calculations: (1) Write validation test from literature, (2) Verify test fails, (3) Implement calculation, (4) Verify test passes."

**Applied to this feature**:
1. **T013-T024**: Write all 10 NIST validation tests (RED - tests fail, no data exists)
2. **T023**: Verify tests fail (`pytest -m validation` shows 10 failures)
3. **T025-T032**: Implement data models and generate compound data (GREEN path)
4. **T033**: Verify tests pass (`pytest -m validation` shows 10 passes)

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 2.5 complete - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - uses QuantityDTO from T004 but independently testable
- **User Story 3 (P3)**: Can start after User Story 1 complete - Requires CompoundDTO models and loader infrastructure

### Within Each User Story

**User Story 1**:
- T025-T027: Pydantic property models (parallel)
- T028: CompoundDTO (depends on T025-T027)
- T029: Database models (depends on T028)
- T030-T031: Loader and data generation (parallel, both depend on T029)
- T032: Run data generation (depends on T031)
- T033: Validation test pass verification (depends on T032)
- T034-T035: Registry implementation (depends on T029, T032)
- T036-T038: Public API exposure (depends on T034-T035)
- T039: Validation (depends on all above)

**User Story 2**:
- T040-T044: UnitHandler methods (sequential - all in same file)
- T045: Error handling (depends on T040-T044)
- T046-T047: Public API exposure (depends on T045)
- T048: Manual verification (depends on all above)

**User Story 3**:
- T049-T053: CoolPropDataExtractor (sequential - all in same file)
- T054-T055: Add compound utility (depends on US1 loader)
- T056-T057: CLI and docs (parallel, depend on T054-T055)
- T058: Testing (depends on all above)

### Parallel Opportunities

- **Phase 1**: T001, T002, T003 can run in parallel (different directories)
- **Phase 2**: T004, T005, T006 can run in parallel (different files)
- **Phase 2.5**: T013-T022 can ALL run in parallel (10 independent test files)
- **User Story 1**: T025, T026, T027 can run in parallel (different model classes)
- **User Story 3**: T056, T057 can run in parallel (different files)
- **Polish**: T059, T060, T061, T062 can run in parallel (different modules/files)

---

## Parallel Example: Phase 2.5 (Validation Tests)

```bash
# Launch ALL 10 validation tests together (highest parallelism in entire feature):
Task: "Create validation test for Water (H2O) critical properties in packages/core/tests/validation/test_nist_water.py"
Task: "Create validation test for Methane (CH4) critical properties in packages/core/tests/validation/test_nist_methane.py"
Task: "Create validation test for Ethane (C2H6) critical properties in packages/core/tests/validation/test_nist_ethane.py"
Task: "Create validation test for Propane (C3H8) critical properties in packages/core/tests/validation/test_nist_propane.py"
Task: "Create validation test for Ammonia (NH3) critical properties in packages/core/tests/validation/test_nist_ammonia.py"
Task: "Create validation test for Carbon Dioxide (CO2) critical properties in packages/core/tests/validation/test_nist_co2.py"
Task: "Create validation test for Nitrogen (N2) critical properties in packages/core/tests/validation/test_nist_nitrogen.py"
Task: "Create validation test for Oxygen (O2) critical properties in packages/core/tests/validation/test_nist_oxygen.py"
Task: "Create validation test for Hydrogen (H2) critical properties in packages/core/tests/validation/test_nist_hydrogen.py"
Task: "Create validation test for Helium (He) critical properties in packages/core/tests/validation/test_nist_helium.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only) - Constitution-Compliant

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational + Quality Gates (T004-T012) - CRITICAL - blocks all stories
3. Complete Phase 2.5: Write validation tests - VERIFY THEY FAIL (T013-T024)
4. Complete Phase 3: User Story 1 - MAKE TESTS PASS (T025-T039)
5. **STOP and VALIDATE**: All validation tests pass, can query compounds via quickstart.md examples
6. Ready for demo/use with 10 NIST-validated compounds

### Incremental Delivery

1. Complete Setup + Foundational + Validation Tests → Foundation ready (tests failing)
2. Add User Story 1 → Tests pass → **MVP Delivered** (can load and query 10 NIST-validated compounds)
3. Add User Story 2 → Test independently → Enhanced MVP (can convert units)
4. Add User Story 3 → Test independently → Full Feature (can extend database)
5. Add Polish → Production Ready (full test coverage, documentation)

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T012)
2. **Phase 2.5**: All 10 validation tests can be written in parallel by 2-3 developers
   - Developer A: T013-T016 (Water, Methane, Ethane, Propane)
   - Developer B: T017-T020 (Ammonia, CO2, Nitrogen, Oxygen)
   - Developer C: T021-T022 (Hydrogen, Helium)
3. After validation tests written and verified failing:
   - Developer A: User Story 1 (T025-T039)
4. After US1 complete:
   - Developer A: User Story 3 (depends on US1)
   - Developer B: User Story 2 (T040-T048)
5. Merge and integrate

**Recommended**: Sequential implementation (US1 → US2 → US3) due to model dependencies, but validation test writing is highly parallelizable.

---

## Scaling Strategy

### Current Implementation (Phase 1: 0-50 compounds)

This feature implements a **JSON-based compound registry** optimized for the initial 10 compounds with a design that supports future scaling to 200+ compounds.

**Why JSON for Phase 1?**
- ✅ Meets <10ms performance goal for property lookups
- ✅ 100% offline, deterministic, version-controlled
- ✅ Human-readable for validation and debugging
- ✅ ~5KB for 10 compounds (~25KB for 50) - well under 100KB limit

### CoolProp Architecture (Verified 2025-12-29)

**Key Facts**:
- All 122+ fluid property data is **compiled into the library** at build time
- Uses **equations of state** to calculate properties on-demand (~50ms vs ~10ms JSON)
- **100% offline** - no external files, no network calls after `pip install CoolProp`
- Data sourced from peer-reviewed literature, validated against NIST REFPROP

### Future Scaling Path (Not Implemented in This Feature)

**Phase 2 (50-200 compounds)**: Split JSON files
- One file per compound: `data/compounds/<CAS-number>.json`
- Lazy loading with in-memory cache
- Minimal changes to `CompoundRegistry` (T034)

**Phase 3 (200+ compounds)**: Tiered Registry
```python
# Future enhancement - not in current tasks
class CompoundRegistry:
    def get_compound(self, identifier: str) -> Compound:
        # Tier 1: Core compounds from JSON (fast, <10ms)
        if compound := self._load_from_json(identifier):
            return compound

        # Tier 2: Extended compounds from CoolProp (122+ fluids, ~50ms)
        if compound := self._load_from_coolprop(identifier):
            return compound

        # Tier 3: User-added compounds (future)
        if compound := self._load_from_user_data(identifier):
            return compound

        raise CompoundNotFoundError(identifier)
```

**Phase 4 (User extensibility)**: User data directory
- Custom compounds in `~/.chemeng/compounds/`
- Same validation schema as core compounds

### Design Decisions Supporting Scalability

**T034** (CompoundRegistry) is designed with interfaces that support future tiering:
- `_load_from_json()` - current implementation
- `_load_from_coolprop()` - future Tier 2 (CoolProp fallback)
- `_load_from_user_data()` - future Tier 3 (user extensibility)

**Benefits of Tiered Approach**:
- No storage explosion - don't duplicate CoolProp's 122+ fluids in JSON
- Automatic updates - `pip install --upgrade CoolProp` gets new compounds
- Simpler maintenance - validate core 10-20 compounds, trust CoolProp for rest
- Stays offline - CoolProp is a local library, no network dependencies

**When to Implement**:
- Phase 2: When compound count exceeds 50 (file splitting)
- Phase 3: When compound count exceeds 200 OR when users need CoolProp's extended library
- Phase 4: When users request ability to add custom compounds

**Not in Scope for This Feature**: The tiered registry is a future enhancement. This feature delivers Phase 1 (JSON registry) with architecture that doesn't block future scaling.

---

## Summary

- **Total Tasks**: 71 (increased from 52 to add constitution-mandated validation tests and quality gates)
- **User Story 1 (P1)**: 15 tasks (T025-T039) - MVP foundation with NIST validation
- **User Story 2 (P2)**: 9 tasks (T040-T048) - Unit conversion capability
- **User Story 3 (P3)**: 10 tasks (T049-T058) - Database extensibility
- **Setup**: 3 tasks (T001-T003)
- **Foundational**: 9 tasks (T004-T012) - includes quality gates (pytest-cov, mypy)
- **Validation Tests**: 12 tasks (T013-T024) - NIST validation suite (constitution-mandated)
- **Polish**: 13 tasks (T059-T071) - includes additional SC verification tests
- **Parallel Opportunities**: 21 tasks can run concurrently in groups (10 validation tests alone)
- **MVP Scope**: Phase 1 + Phase 2 + Phase 2.5 + Phase 3 (User Story 1) = 39 tasks

**Constitution Compliance**: ✅ All Principle III requirements satisfied
- ✅ Validation tests for all compound data (T013-T024)
- ✅ 80% test coverage requirement (T010)
- ✅ mypy --strict type checking (T011)
- ✅ Red-Green-Refactor workflow enforced (T023 → T025-T032 → T033)
- ✅ Quality gates in foundational phase (T009-T012)

---

## Notes

- [P] tasks = different files or logically independent, no sequential dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **CRITICAL**: Phase 2.5 validation tests MUST be written and verified failing before implementing User Story 1
- Success criteria SC-002, SC-004, SC-005, SC-007 now have explicit test task coverage (T013-T024, T061-T063)
