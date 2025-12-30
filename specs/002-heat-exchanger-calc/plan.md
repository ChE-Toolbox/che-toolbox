# Implementation Plan: Heat Exchanger Calculations

**Branch**: `002-heat-exchanger-calc` | **Date**: 2025-12-30 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-heat-exchanger-calc/spec.md`

**Note**: This plan is filled in by the `/speckit.plan` command execution. Phases: 0 (Research), 1 (Design & Contracts), 2 (Task generation via `/speckit.tasks`).

## Summary

Implement comprehensive heat exchanger calculation library with four core modules: LMTD method (counterflow, parallel, crossflow with correction factors), NTU-effectiveness method (multiple configurations), convection correlations (flat plate, pipes, cylinders, natural convection), and insulation sizing (economic optimization). Expose via Python library API + CLI wrapper with Pydantic input/output and JSON/YAML I/O. Validate against Incropera textbooks and NIST reference data (stored locally in JSON format). Depends on existing properties abstraction from 001-data-foundations.

## Technical Context

**Language/Version**: Python 3.11+ (per project constraint in CLAUDE.md)
**Primary Dependencies**: NumPy 1.24+ (polynomial roots, numerical methods), SciPy 1.10+ (Brent's method optimization), Pint 0.23+ (unit handling), Pydantic 2.x (data validation), pytest (testing), mypy (type checking)
**Storage**: JSON/CSV files for validation reference test cases (no database)
**Testing**: pytest (>80% coverage required per Constitution III); validation tests comparing against Incropera + NIST references
**Target Platform**: Linux/macOS/Windows (Python 3.11+)
**Project Type**: Single Python library with CLI wrapper
**Performance Goals**: All calculations complete within 100ms (per SC-007); most well under 10ms
**Constraints**: <100ms latency, <100MB memory per calculation; numerical stability for edge cases (LMTD → 0, NTU → ∞)
**Scale/Scope**: 4 calculation modules, 20+ correlations, 10+ validation test cases, 100% type coverage (mypy --strict)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with [ChemEng Toolbox Constitution](../../.specify/memory/constitution.md):

- [x] **I. Library-First**: Feature will be standalone Python library in `src/heat_calc/` (or `packages/core/src/` per Constitution); independently testable without external project dependencies
- [x] **II. Multi-Interface**: Plan includes Python library API, CLI wrapper, and prepares for web interface integration (Phase 2+)
- [x] **III. Validation-First**: Incropera textbook + NIST sources identified for validation; JSON test fixtures with source citations documented
- [x] **IV. Public Domain Data**: Validation data from publicly available Incropera textbook examples + NIST; no proprietary property data required (properties module handles CoolProp optionally via abstraction)
- [x] **V. Cost-Free**: No paid services; validation data stored in repo; optional CoolProp (MIT licensed) via existing 001-data-foundations module
- [x] **VI. Developer Productivity**: Clear module structure, 100% type hints (mypy --strict), NumPy-style docstrings, pytest validation tests
- [x] **VII. Simplicity**: Library provides only core calculations; no enterprise features; depends on existing properties abstraction (no new coupling)

**Violations**: None. All principles satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/heat_calc/
├── __init__.py                          # Library public API exports
├── lmtd.py                              # LMTD method calculations
├── ntu.py                               # NTU-effectiveness method
├── convection.py                        # Convection correlations
├── insulation.py                        # Insulation sizing calculations
├── models/
│   ├── __init__.py
│   ├── lmtd_input.py                    # Pydantic input models (LMTD)
│   ├── lmtd_results.py                  # Pydantic results objects (LMTD)
│   ├── ntu_input.py                     # Pydantic input models (NTU)
│   ├── ntu_results.py                   # Pydantic results objects (NTU)
│   ├── convection_input.py              # Pydantic input models (convection)
│   ├── convection_results.py            # Pydantic results objects (convection)
│   ├── insulation_input.py              # Pydantic input models (insulation)
│   └── insulation_results.py            # Pydantic results objects (insulation)
├── cli/
│   ├── __init__.py
│   └── main.py                          # CLI entry points (calculate-lmtd, calculate-ntu, etc.)
└── utils/
    ├── __init__.py
    ├── validation.py                    # Input validation helpers
    └── constants.py                     # Physical constants, reference correlations

tests/
├── unit/
│   ├── test_lmtd.py                     # Unit tests for LMTD calculations
│   ├── test_ntu.py                      # Unit tests for NTU calculations
│   ├── test_convection.py               # Unit tests for convection correlations
│   ├── test_insulation.py               # Unit tests for insulation sizing
│   └── test_models.py                   # Pydantic model validation tests
├── validation/
│   ├── test_lmtd_incropera.py           # Validation tests: LMTD vs Incropera examples
│   ├── test_ntu_correlations.py         # Validation tests: NTU vs published correlations
│   ├── test_convection_correlations.py  # Validation tests: convection vs literature
│   └── test_insulation_economics.py     # Validation tests: economic insulation
└── fixtures/
    └── validation_references.json       # Reference test cases (inputs + expected outputs with sources)

data/
└── reference_test_cases.json            # Validation reference data (Incropera page#, NIST ID, etc.)
```

**Structure Decision**: Single Python library (per Constitution I: Library-First) with 4 calculation modules (lmtd, ntu, convection, insulation), Pydantic models for I/O (per clarification Q2), CLI wrapper module, and comprehensive test suite (>80% coverage per Constitution III, with dedicated validation test directory)

## Complexity Tracking

No violations. All complexity decisions aligned with Constitution principles.

---

## Phase 0: Research & Unknowns Resolution

**Status**: Complete. No critical NEEDS CLARIFICATION items in Technical Context or from clarification session.

**Decisions Made** (from specification clarifications):

1. **Interface Model**: Library + CLI (Q1) ✓
   - Primary: Python library for direct programmatic access
   - Secondary: CLI wrapper for command-line / scripting use
   - Future: Web interface (Phase 2+)

2. **Data Format**: Pydantic + JSON/YAML (Q2) ✓
   - Library API: Pydantic models with automatic unit validation via Pint
   - CLI/batch: JSON/YAML file input, structured output (JSON + human-readable)
   - Result objects: Comprehensive Pydantic models (primary result + intermediates + source reference)

3. **Properties Module**: Abstraction from 001-data-foundations (Q3) ✓
   - Heat module depends on properties module abstraction
   - No direct CoolProp coupling; properties module owns strategy decisions
   - Allows fluid properties (constant or dynamic) transparently

4. **Validation Data**: JSON/CSV in repo (Q4) ✓
   - Reference test cases stored in `data/reference_test_cases.json`
   - Sources: Incropera "Fundamentals of Heat and Mass Transfer" (textbook + page numbers), NIST database identifiers
   - Deterministic testing; no runtime external dependencies

5. **Output Structure**: Comprehensive results objects (Q5) ✓
   - All calculation functions return Pydantic results objects
   - Contents: primary result, intermediate values, correlation/method used, source reference, confidence bounds
   - Enables full traceability for validation and reproducibility

**Research Topics Addressed**:

- ✓ LMTD method: Counterflow, parallel flow, crossflow algorithms + correction factor application (standard heat transfer domain)
- ✓ NTU-effectiveness: Standard correlations for multiple configurations (Perry's, GPSA references)
- ✓ Convection correlations: Laminar/turbulent flat plate, Dittus-Boelert for pipes, cylinder crossflow, natural convection (Incropera standard)
- ✓ Insulation economics: Economic thickness optimization (payback analysis with energy + material costs)
- ✓ Numerical stability: Handling LMTD → 0, NTU → ∞ via SciPy Brent's method + epsilon guards

**Technology Choices**:
- NumPy: Polynomial root-finding (LMTD solution), numerical arrays
- SciPy: Brent's method for nonlinear NTU solving
- Pint: Unit validation & conversion (all inputs/outputs dimensionally checked)
- Pydantic 2.x: Data validation, serialization (JSON/YAML)
- pytest: Unit + validation tests
- mypy --strict: 100% type coverage

---

## Phase 1: Design & Contracts (Complete)

### Generated Artifacts

**1. Data Model** (`data-model.md`):
- Core data types for each of 4 calculation domains
- Pydantic models: Input, Output, supporting entities
- Validation rules and constraints
- Relationships and state transitions
- Serialization formats (JSON/YAML)

**2. Quickstart Guide** (`quickstart.md`):
- 4 Python library API examples (one per calculation module)
- 4 CLI examples (command-line usage)
- Error handling patterns
- Performance profiles
- Integration with properties module

**3. API Contracts** (`contracts/`):
- **python_library_api.md**: Function signatures, docstrings, error handling, type hints
  - `calculate_lmtd()`
  - `calculate_ntu()`
  - `calculate_convection()`
  - `calculate_insulation()`
  - Input/output models, shared structures

- **cli_interface.md**: Command-line tool specifications
  - `calculate-lmtd`, `calculate-ntu`, `calculate-convection`, `calculate-insulation`
  - Input/output formats (JSON, YAML, table)
  - Exit codes, error messages, options
  - Streaming & piping support

### Project Structure Confirmed

```
src/heat_calc/
├── Calculation modules (4): lmtd.py, ntu.py, convection.py, insulation.py
├── Models (8): Input/Result pairs for each domain
├── CLI wrapper: cli/main.py with 4 sub-commands
└── Utils: validation, constants

tests/
├── Unit tests (80% of effort): test_*.py for each module
├── Validation tests (15%): Incropera + NIST examples
└── Fixtures: reference_test_cases.json (10+ cases)

data/
└── reference_test_cases.json (validation data with sources)
```

### Constitution Re-Check (Post-Design)

All principles remain satisfied:

- [x] **I. Library-First**: Standalone library with clear module boundaries
- [x] **II. Multi-Interface**: Library + CLI; web interface prep in design
- [x] **III. Validation-First**: 10+ validation tests; JSON fixture-based
- [x] **IV. Public Domain Data**: Incropera textbook + NIST; no proprietary data
- [x] **V. Cost-Free**: No paid services; JSON data files in repo
- [x] **VI. Developer Productivity**: Type hints, NumPy docstrings, clear structure
- [x] **VII. Simplicity**: Core calculations only; no enterprise features

**Status**: Phase 1 Design Complete; Ready for Phase 2 (Task Generation)

---

## Next Steps

**Phase 2**: Run `/speckit.tasks` to generate actionable, dependency-ordered tasks from this design

This will decompose the feature into implementable work units with clear acceptance criteria.
