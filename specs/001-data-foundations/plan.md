# Implementation Plan: Chemical Database Data Foundations

**Branch**: `001-data-foundations` | **Date**: 2025-12-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-data-foundations/spec.md`

## Summary

Implement a validated chemical compound database with 10 compounds sourced from CoolProp (NIST-validated), storing thermophysical properties in JSON format with Pint-based unit handling and Pydantic data validation. The database provides the foundational data layer for all ChemEng Toolbox calculations.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: CoolProp 7.x, Pint 0.23+, Pydantic 2.x, NumPy 1.24+
**Storage**: JSON files in `packages/core/src/chemeng_core/data/compounds/`
**Testing**: pytest with `@pytest.mark.validation` marker for NIST validation tests
**Target Platform**: Cross-platform Python library (Linux, macOS, Windows)
**Project Type**: Single library package (chemeng-core)
**Performance Goals**: Property lookup <10ms; compound loading <100ms
**Constraints**: Data files <100KB total; no external API calls at runtime
**Scale/Scope**: 10 compounds initially; extensible to 100+ compounds

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with [ChemEng Toolbox Constitution](../../.specify/memory/constitution.md):

- [x] **I. Library-First**: Feature is a standalone library in `packages/core/src/chemeng_core/`
- [x] **II. Multi-Interface**: Data accessible via Python API; CLI/web exposure deferred to later features
- [x] **III. Validation-First**: NIST WebBook sources identified; validation tests planned with literature tolerances
- [x] **IV. Public Domain Data**: CoolProp (MIT) and NIST WebBook (Public Domain) only
- [x] **V. Cost-Free**: No paid services; all data from free sources
- [x] **VI. Developer Productivity**: Type hints, Pydantic models, NumPy-style docstrings planned
- [x] **VII. Simplicity**: JSON storage; no database; minimal dependencies

**Violations**: None. All principles satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/001-data-foundations/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 research findings
├── data-model.md        # Phase 1 entity definitions
├── quickstart.md        # Phase 1 usage guide
├── contracts/           # Phase 1 API contracts
│   └── compound_api.py  # Python interface definitions
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
packages/core/
├── src/chemeng_core/
│   ├── __init__.py
│   ├── compounds/               # NEW: Compound module
│   │   ├── __init__.py
│   │   ├── models.py           # Pydantic models for compounds
│   │   ├── registry.py         # Compound lookup and loading
│   │   └── validation.py       # Schema validation utilities
│   ├── units/                   # NEW: Unit handling module
│   │   ├── __init__.py
│   │   ├── registry.py         # Pint UnitRegistry configuration
│   │   └── quantity.py         # Pydantic-compatible quantity types
│   └── data/
│       ├── README.md           # Existing
│       └── compounds/           # NEW: Compound data files
│           └── compounds.json  # All 10 compounds
└── tests/
    ├── unit/
    │   ├── test_compound_model.py
    │   └── test_unit_handler.py
    ├── validation/
    │   └── test_nist_validation.py
    └── conftest.py
```

**Structure Decision**: Single package structure extending `packages/core/`. New modules for `compounds/` and `units/` follow library-first principle with clear boundaries.

## Complexity Tracking

> No violations to justify.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| - | - | - |

## Phase 1 Artifacts

### Generated Files

1. **research.md** - Completed (see [research.md](./research.md))
2. **data-model.md** - Entity definitions with Pydantic schemas
3. **contracts/compound_api.py** - Python API interface definitions
4. **quickstart.md** - Developer usage guide

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Data Source | CoolProp | MIT license, NIST-validated, Python native, **data baked into library** (offline) |
| Storage Format | JSON | Human-readable, git-friendly, <100KB |
| Unit Library | Pint | Constitution requirement, industry standard |
| Validation | Pydantic | Already in dependencies, type-safe |
| Primary Key | CAS Number | Globally unique, unambiguous |
| Scaling Strategy | Tiered Registry | JSON for core compounds (<10ms), CoolProp fallback for extended library (122+ fluids) |

## Scaling Strategy

### CoolProp Architecture

**How CoolProp Works** (research verified 2025-12-29):
- All 122+ fluid property data is **compiled directly into the library** at build time
- Source data stored as JSON in `dev/fluids/` folder, embedded during compilation
- Uses **equations of state** (Helmholtz energy formulations) to calculate properties on-demand
- **100% offline** - no external files, no network calls, no dependencies after `pip install`
- Data sourced from peer-reviewed literature and validated against NIST REFPROP ($325 commercial standard)

**Performance Characteristics**:
- JSON lookup: ~10ms (meets our performance goal)
- CoolProp calculation: ~50ms (solving equations of state)
- CoolProp is better for state-dependent properties (density at specific T/P)
- JSON is better for constant properties (critical temperature, molecular weight)

### Tiered Compound Registry

**Phase 1 (0-50 compounds)**: JSON in repo ✅ Current implementation
- Single `compounds.json` file (~5KB for 10 compounds, ~25KB for 50)
- Fast, simple, version-controlled
- Meets <10ms lookup performance goal
- Works offline, deterministic, reproducible

**Phase 2 (50-200 compounds)**: Split JSON files + lazy loading
- One file per compound: `data/compounds/<CAS-number>.json`
- Load on-demand, cache in memory
- Still ~100KB total, git-friendly
- Minimal code changes to `CompoundRegistry`

**Phase 3 (200+ compounds)**: Tiered registry with CoolProp fallback
```python
class CompoundRegistry:
    """Multi-tier compound lookup with graceful fallback."""

    def get_compound(self, identifier: str) -> Compound:
        # Tier 1: Core compounds from JSON (fast, always available)
        if compound := self._load_from_json(identifier):
            return compound

        # Tier 2: Extended compounds from CoolProp (on-demand, 122+ fluids)
        if compound := self._load_from_coolprop(identifier):
            return compound

        # Tier 3: User-added compounds (future extensibility)
        if compound := self._load_from_user_data(identifier):
            return compound

        raise CompoundNotFoundError(identifier)
```

**Benefits**:
- No storage explosion - don't duplicate CoolProp's 122+ fluids
- Stays offline - CoolProp is a local library
- Automatic updates - `pip install --upgrade CoolProp` gets new compounds
- Simpler maintenance - validate core 10-20 compounds, trust CoolProp for rest
- User extensibility - custom compounds in `~/.chemeng/compounds/`

**Migration Path**:
- ✅ **Phase 1 (current)**: Implement JSON registry for core 10 compounds
- 📋 **Phase 2 (at 50+ compounds)**: Split into individual JSON files
- 📋 **Phase 3 (at 200+ compounds)**: Add CoolProp tier 2 fallback
- 📋 **Phase 4 (user request)**: Add user data directory tier 3

### Data Refresh Strategy

For development-time updates:
```python
# scripts/refresh_compound_data.py
# Run manually when:
# - CoolProp updates with new/corrected data
# - Adding new compounds to core set
# - NIST publishes revised values
```

This separates **development-time extraction** (CoolProp → JSON) from **runtime access** (JSON → application), maintaining both performance and accuracy.

### Next Steps

Run `/speckit.tasks` to generate implementation tasks from this plan.
