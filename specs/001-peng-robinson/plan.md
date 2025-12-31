# Implementation Plan: Peng-Robinson EOS Thermodynamic Engine

**Branch**: `001-peng-robinson` | **Date**: 2025-12-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-peng-robinson/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a production-grade Peng-Robinson equation of state (EOS) thermodynamic engine for calculating compressibility factors, fugacity coefficients, and vapor pressures for pure components and mixtures. The implementation will use NumPy for cubic equation solving with analytical fallback, SciPy Brent's method for vapor pressure iterations, and comprehensive validation against NIST WebBook data for 5 reference compounds (methane, ethane, propane, n-butane, water) with target accuracy of ±5% for Z factors and ±10% for fugacity.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: NumPy 1.24+ (polynomial roots), SciPy 1.10+ (Brent's method optimization), Pint 0.23+ (unit handling), Pydantic 2.x (data validation)
**Storage**: JSON files for compound database (critical properties: Tc, Pc, acentric factor); NIST reference data for validation
**Testing**: pytest (unit + validation tests), mypy --strict (type checking), target >80% code coverage
**Target Platform**: Cross-platform Python library (Linux/macOS/Windows), designed for library-first architecture with CLI/web interfaces
**Project Type**: Single project (standalone library)
**Performance Goals**: Single property calculations <10ms, validation suite complete in <60s, convergence success rate >99% for well-posed problems
**Constraints**: Calculations must be accurate to ±5% for Z factor and ±10% for fugacity vs NIST data, memory usage <200MB per calculation, no proprietary data sources
**Scale/Scope**: 5 validation compounds initially (methane, ethane, propane, n-butane, water), extensible to 50+ compounds, support pure components and mixtures up to 10 components

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with [ChemEng Toolbox Constitution](../../.specify/memory/constitution.md):

- [x] **I. Library-First**: Feature implemented as standalone library in `src/` with clear module boundaries (eos/, validation/, compounds/)
- [x] **II. Multi-Interface**: Python API for direct library use, CLI wrapper planned for scripting, web calculator component planned for interactive use
- [x] **III. Validation-First**: NIST WebBook identified as authoritative source for validation tests across 5 compounds with defined tolerance criteria (±5% Z factor, ±10% fugacity)
- [x] **IV. Public Domain Data**: All data from NIST WebBook (public domain) and critical properties from open literature sources
- [x] **V. Cost-Free**: Pure library implementation with no cloud services or paid dependencies
- [x] **VI. Developer Productivity**: Type hints (mypy --strict), NumPy-style docstrings, clear module structure following library-first architecture
- [x] **VII. Simplicity**: Standard NumPy/SciPy for numerical methods, no custom optimization frameworks, YAGNI applied (no phase stability analysis or advanced mixing rules in v1)

**Violations**: None - all principles satisfied.

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
src/
├── eos/
│   ├── __init__.py
│   ├── peng_robinson.py      # Core PR-EOS implementation (Z factor, fugacity)
│   ├── cubic_solver.py        # NumPy roots + analytical cubic fallback
│   └── mixing_rules.py        # Van der Waals mixing rules for mixtures
├── compounds/
│   ├── __init__.py
│   ├── database.py            # Compound data access layer
│   └── models.py              # Pydantic models for compound properties
├── validation/
│   ├── __init__.py
│   └── nist_data.py           # NIST reference data loader
└── cli/
    └── pr_calc.py             # CLI wrapper for calculations

data/
├── compounds.json             # Critical properties (Tc, Pc, omega)
└── nist_reference/            # NIST validation data
    ├── methane.json
    ├── ethane.json
    ├── propane.json
    ├── n_butane.json
    └── water.json

tests/
├── unit/
│   ├── test_peng_robinson.py
│   ├── test_cubic_solver.py
│   ├── test_mixing_rules.py
│   └── test_compounds.py
├── validation/
│   ├── test_nist_pure_components.py
│   └── test_nist_mixtures.py
└── integration/
    └── test_cli.py
```

**Structure Decision**: Single project structure selected (Option 1) - this is a standalone computational library with no web frontend or mobile components in Phase 1. The library-first architecture places all core logic in `src/` with clear separation of concerns: EOS calculations (`eos/`), compound data management (`compounds/`), and validation infrastructure (`validation/`). Tests are organized by type (unit/validation/integration) per constitution requirements.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations - all Constitution principles satisfied.

---

## Post-Design Constitution Re-Evaluation

**Date**: 2025-12-29
**Phase**: After Phase 1 design completion

### Re-Verification of Constitution Compliance

- [x] **I. Library-First**: Design confirms standalone library structure in `src/` with clear module boundaries (`eos/`, `compounds/`, `validation/`). No dependencies on web or CLI infrastructure. ✓
- [x] **II. Multi-Interface**: Design includes Python API (library functions), CLI wrapper (`pr-calc` command suite), and planned web calculator. All interfaces use same core library. ✓
- [x] **III. Validation-First**: Complete validation infrastructure designed with NIST reference data in `data/nist_reference/`, validation test suite, and automated pass/fail criteria. ✓
- [x] **IV. Public Domain Data**: All data sources confirmed public domain (NIST WebBook, open literature for critical properties). No proprietary databases. ✓
- [x] **V. Cost-Free**: Pure computational library with no cloud services, paid APIs, or ongoing costs. ✓
- [x] **VI. Developer Productivity**: Full type annotations (mypy --strict), Pydantic validation, NumPy-style docstrings, comprehensive API documentation. ✓
- [x] **VII. Simplicity**: Uses standard NumPy/SciPy methods (no custom frameworks), YAGNI applied (deferred phase stability analysis, advanced mixing rules to future). ✓

### Design Quality Assessment

**Strengths**:
1. Clear separation of concerns: EOS calculations, compound data, validation infrastructure
2. Comprehensive API contracts for both Python library and CLI
3. Detailed data models with Pydantic validation ensure type safety
4. Well-researched technical decisions with documented alternatives and rationale
5. Practical quickstart guide with real-world examples

**Potential Risks**:
1. Vapor pressure convergence near critical point (mitigated: 100 iteration limit, best estimate on failure)
2. NIST validation data availability (mitigated: data included in repository)
3. Mixture accuracy dependent on binary interaction parameters (mitigated: default kij=0, literature values available)

**Recommendation**: ✅ **APPROVED TO PROCEED TO IMPLEMENTATION**

All Constitution principles satisfied. Design is complete, well-documented, and ready for Phase 2 (task generation and implementation).
