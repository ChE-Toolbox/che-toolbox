# Implementation Plan: IAPWS-IF97 Steam Properties

**Branch**: `002-steam-properties` | **Date**: 2025-12-30 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-steam-properties/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement complete IAPWS-IF97 thermodynamic property calculations for steam/water across all three regions plus saturation line. Deliver as a Python library with Pint-based unit handling, comprehensive validation against official IAPWS tables, and SteamTable convenience API for P-T lookups. Core requirement: ±0.03-0.2% accuracy across all regions with explicit fail on numerical instability near critical point.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: NumPy 1.24+, SciPy 1.10+, Pint 0.23+, Pydantic 2.x
**Storage**: Embedded IAPWS-IF97 coefficients and reference validation tables in JSON/CSV
**Testing**: pytest with IAPWS official supplementary tables for validation
**Target Platform**: Linux/macOS/Windows (pure Python, no platform-specific code)
**Project Type**: Single Python library with CLI wrapper and web interface (library-first)
**Performance Goals**: Single property calculation <10ms; 100+ properties per second sustained
**Constraints**: ±0.03% accuracy Region 1, ±0.06% Region 2, ±0.2% Region 3, ±0.1% saturation line; explicit fail on singularities
**Scale/Scope**: ~2000 LOC library code, ~3000 LOC tests, 6 convenience methods (h_pt, s_pt, u_pt, rho_pt, T_sat, P_sat)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with [ChemEng Toolbox Constitution](../../.specify/memory/constitution.md):

- [x] **I. Library-First**: IAPWS-IF97 module as standalone library in `src/iapws_if97/`; independently testable without external project dependencies
- [x] **II. Multi-Interface**: Python API via SteamTable class; CLI wrapper for scripting; web interface via static calculator component
- [x] **III. Validation-First**: Official IAPWS-IF97 supplementary tables as validation source; minimum 100 test points per region; 80%+ code coverage with pytest
- [x] **IV. Public Domain Data**: IAPWS-IF97 equations are publicly available standards; validation tables from official IAPWS publications (public domain)
- [x] **V. Cost-Free**: No external services; all computation local; zero monthly cost
- [x] **VI. Developer Productivity**: Full type hints (mypy --strict), NumPy-style docstrings, conventional commits, clear module structure
- [x] **VII. Simplicity**: MVP scope = P-T lookups only; no caching overhead; explicit fail on instability (prevents silent errors); YAGNI applied throughout

**Violations**: None. All principles satisfied. Implementation strategy directly supports validation-critical scientific computing use case.

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
├── iapws_if97/                    # Core library
│   ├── __init__.py               # Public API exports (SteamTable, exceptions)
│   ├── steam_table.py            # SteamTable class (P-T convenience API)
│   ├── regions/
│   │   ├── __init__.py
│   │   ├── region1.py            # Region 1 (liquid water) IAPWS equations
│   │   ├── region2.py            # Region 2 (steam) IAPWS equations
│   │   ├── region3.py            # Region 3 (supercritical) IAPWS equations
│   │   └── saturation.py         # Saturation line calculations
│   ├── validation/
│   │   ├── __init__.py
│   │   └── iapws_tables.json     # Official IAPWS reference values
│   ├── exceptions.py             # ValueError, RuntimeError subclasses
│   └── utils.py                  # Helper functions (polynomial eval, root finding)
└── iapws_if97_cli/               # CLI wrapper (optional but included for multi-interface)
    ├── __init__.py
    ├── cli.py                    # Command-line interface
    └── formatters.py             # JSON/human output formatting

tests/
├── unit/
│   ├── test_region1.py           # Region 1 tests (~400 points from IAPWS tables)
│   ├── test_region2.py           # Region 2 tests (~400 points)
│   ├── test_region3.py           # Region 3 tests (~200 points)
│   ├── test_saturation.py        # Saturation line tests (~300 points)
│   ├── test_steam_table.py       # SteamTable API tests
│   └── test_exceptions.py        # Error handling tests
├── integration/
│   ├── test_region_routing.py    # Correct region selection
│   ├── test_boundary_transitions.py  # Region boundary handling
│   └── test_end_to_end.py        # Full property lookup workflows
└── conftest.py                   # pytest fixtures, IAPWS reference data loader
```

**Structure Decision**: Single Python library + CLI wrapper (Option 1). Library-first approach per Constitution Principle I; CLI wrapper enables scripting and automation per Principle II. Web interface developed separately as static web component using library as backend.

## Complexity Tracking

No violations. All Constitution principles satisfied. See Constitution Check above.

## Phase 0: Research & Knowledge Baseline

All technical context items are determined from specification clarifications. No NEEDS CLARIFICATION markers remain. This section documents the research tasks to resolve implementation details before coding begins.

### Research Tasks

**R1: IAPWS-IF97 Standard Implementation Details**
- **Context**: Implement equations for all 3 regions + saturation line
- **Questions to resolve**:
  - Exact polynomial coefficients for all regions (source: official IAPWS-IF97 tables)
  - Region boundary definitions and how to detect which region applies
  - Saturation line equation formulation (iterate P→T or T→P)
  - Treatment of two-phase region (what to do when user provides conditions on saturation line)
- **Deliverable**: Document region equations, boundaries, iteration methods; source all coefficients from official IAPWS publication

**R2: Numerical Stability & Singularities Near Critical Point**
- **Context**: Must raise RuntimeError with diagnostics when singularities detected
- **Questions to resolve**:
  - What distance from critical point (22.064 MPa, 373.946 K) triggers fail? (tolerance threshold)
  - How to detect convergence failure vs. legitimate singular region?
  - Diagnostic message content: what info helps users recover? (distance to critical point? suggested alternative region?)
- **Deliverable**: Numerical stability strategy document; pseudocode for singularity detection

**R3: IAPWS Reference Data & Validation Tables**
- **Context**: Need minimum 100 test points per region from official sources
- **Questions to resolve**:
  - Where to obtain official IAPWS-IF97 supplementary tables? (free public sources)
  - Format for embedding reference data (JSON, CSV, or Python fixtures)?
  - How to organize test points: by region? by property? by accuracy tier?
- **Deliverable**: Downloaded/formatted reference tables; test point classification scheme

**R4: Pint Integration for Unit Handling**
- **Context**: Must return Pint Quantity objects from SteamTable API
- **Questions to resolve**:
  - How to initialize Pint UnitRegistry in library (singleton vs. pass-through)?
  - Standard unit definitions: confirm Pa, K, kJ/kg, kJ/(kg·K) are Pint built-ins
  - How to handle unit conversion internally (Pa↔MPa, K↔°C)?
- **Deliverable**: Pint usage pattern document; unit initialization code snippet

**R5: Exception Hierarchy & Message Formatting**
- **Context**: ValueError for input validation, RuntimeError for convergence; structured format
- **Questions to resolve**:
  - Define custom exception subclasses or use built-ins?
  - Exact message format: include parameter name, min/max bounds, suggestion?
  - Test strategy for exception messages (regex match, exact string, or just type check)?
- **Deliverable**: Exception class definitions; message format specification with examples

**R6: SciPy Root-Finding for Saturation Properties**
- **Context**: Saturation temperature/pressure via Newton-Raphson or Brent's method
- **Questions to resolve**:
  - Which SciPy functions to use (scipy.optimize.brentq vs. newton)?
  - Convergence tolerance (absolute/relative)?
  - How to initialize root search (bracketing vs. starting guess)?
- **Deliverable**: SciPy root-finding pattern; pseudocode for T_sat(P) and P_sat(T) calculation

**R7: Performance Baseline & Profiling Strategy**
- **Context**: Target <10ms per property calculation
- **Questions to resolve**:
  - Typical NumPy polynomial evaluation time on standard hardware?
  - Which region equations are most expensive (Region 3)?
  - Profiling tools & strategy: cProfile, timeit, or benchmarking suite?
- **Deliverable**: Baseline performance metrics; identify hotspots before optimization

### Research Dispatch Summary

Total research tasks: 7 (all low-risk, design-level clarifications)
Timeline impact: 1-2 hours research before Phase 1 design
Blocker status: None; all can proceed in parallel

---

## Phase 1: Design & Contracts

### 1.1 Data Model (data-model.md)

**Entities**:
- **Region (enum)**: Region.REGION1, Region.REGION2, Region.REGION3, Region.SATURATION
- **SteamProperties (dataclass)**: pressure (Pa), temperature (K), enthalpy (kJ/kg), entropy (kJ/(kg·K)), density (kg/m³), internal_energy (kJ/kg); all as Pint Quantity
- **SaturationProperties (dataclass)**: T_sat (K), P_sat (Pa), h_f (enthalpy liquid), h_g (enthalpy vapor), s_f, s_g, rho_f, rho_g; all as Quantity

**Validation Rules**:
- Pressure: 611.657 Pa ≤ P ≤ 863.91 MPa (full range covering triple point to Region 1 max)
- Temperature: 273.15 K ≤ T ≤ 863.15 K (triple point to universal IAPWS limit)
- Region assignment: (P, T) → Region 1 | 2 | 3 | SATURATION via boundary checks
- Singularity guard: distance(P,T,critical_point) < threshold → RuntimeError

### 1.2 API Contracts (contracts/)

**Python API**:
```python
class SteamTable:
    def h_pt(self, pressure: Quantity, temperature: Quantity) -> Quantity
    def s_pt(self, pressure: Quantity, temperature: Quantity) -> Quantity
    def u_pt(self, pressure: Quantity, temperature: Quantity) -> Quantity
    def rho_pt(self, pressure: Quantity, temperature: Quantity) -> Quantity
    def T_sat(self, pressure: Quantity) -> Quantity  # Returns saturation temperature
    def P_sat(self, temperature: Quantity) -> Quantity  # Returns saturation pressure
```

**CLI Interface**:
```bash
steam-table --property h --pressure 10 MPa --temperature 500 C
# Output: enthalpy: 3373.7 kJ/kg (for example)

steam-table --json --property all --pressure 0.1 MPa --temperature 200 C
# Output: JSON with all properties
```

**Error Handling**:
- Raise `ValueError` if P or T out of bounds
- Raise `RuntimeError` if numerical instability detected
- All messages follow format: `"[Error]: [reason]. [valid_range_or_suggestion]"`

### 1.3 Agent Context Update

After Phase 1 design complete, run:
```bash
.specify/scripts/bash/update-agent-context.sh claude
```

This adds IAPWS-IF97 specific technology (NumPy polynomial evaluation, SciPy root-finding, Pint units) to the Claude agent context for consistent future assistance.

---

## Phase 1 Outputs (Generated by /speckit.plan)

- [x] **data-model.md**: Complete data model with regions, properties, validation rules
- [x] **contracts/python_api.md**: Python API contract for SteamTable class and data types
- [x] **contracts/cli_interface.md**: CLI command documentation (property, saturation, batch, info)
- [x] **quickstart.md**: Usage examples (Python API, CLI, unit handling, error handling)
- [x] **research.md**: Phase 0 research findings (7 research items resolved)

---

## Next Steps

1. **Phase 0 Complete**: All research items documented (no blocking unknowns)
2. **Ready for Phase 1**: Execute design generation and contracts
3. **Then Phase 2**: Generate tasks.md via `/speckit.tasks` command (after plan complete)
4. **Implementation**: Follow task breakdown to implement regions, validation suite, and API

---

## Status Summary

✅ Specification complete and clarified (5 Q&A resolutions)
✅ Constitution compliance verified (all 7 principles satisfied)
✅ Technical context determined (Python 3.11+, NumPy, SciPy, Pint, Pydantic)
✅ Project structure defined (src/iapws_if97, tests/, CLI wrapper)
✅ **Phase 0 Complete**: Research plan documented (7 research items, no blockers)
✅ **Phase 1 Complete**: Design & contracts generated
  - ✅ data-model.md: Regions, SteamProperties, SaturationProperties, validation rules
  - ✅ contracts/python_api.md: SteamTable API specification with all methods
  - ✅ contracts/cli_interface.md: CLI commands (property, saturation, batch, info)
  - ✅ quickstart.md: Usage examples (Python, CLI, error handling, workflows)
  - ✅ Agent context updated with IAPWS-IF97 technologies
⏳ **Phase 2 Pending**: Task generation via `/speckit.tasks` command

## Artifact Summary

**Specification & Planning** (Complete):
- spec.md (15 KB): Feature specification with 5 clarifications
- plan.md (13 KB): Implementation plan with architecture & Phase 0-1 planning
- research.md (15 KB): 7 research items resolved (singularities, validation, Pint, exceptions, root-finding, performance)
- data-model.md (12 KB): Region definitions, entity structures, validation rules
- quickstart.md (9 KB): Python API examples, CLI usage, error handling

**API Contracts** (Complete):
- contracts/python_api.md (14 KB): SteamTable, SteamProperties, SaturationProperties, exceptions
- contracts/cli_interface.md (9 KB): CLI subcommands, exit codes, scripting examples

**Quality Artifacts**:
- checklists/requirements.md: Specification quality checklist (all items passed)

**Total Generated**: ~90 KB of design documentation

## Architecture Summary

**Library Structure**:
- `src/iapws_if97/`: Core library (~2000 LOC expected)
  - `steam_table.py`: SteamTable class (P-T API)
  - `regions/`: region1.py, region2.py, region3.py, saturation.py
  - `validation/`: IAPWS reference tables (JSON)
  - `exceptions.py`: InputRangeError, NumericalInstabilityError
  - `utils.py`: Polynomial eval, root-finding helpers
- `src/iapws_if97_cli/`: CLI wrapper (optional, multi-interface support)
- `tests/`: ~3000 LOC validation tests (100+ points per region)

**Key Design Decisions**:
1. **Pint Quantities** for all property returns (full unit awareness)
2. **Explicit fail** on singularities (no silent errors near critical point)
3. **No built-in caching** (users manage; 10ms target achievable fresh)
4. **Structured exception messages** with parameter names and guidance
5. **SciPy brentq** for saturation root-finding (robust, derivative-free)
6. **Library-first** per Constitution (pure Python, ~2000 LOC, 80%+ test coverage)

## Quality Gates

All Constitution principles satisfied:
- ✅ I. Library-First: Standalone `iapws_if97` module
- ✅ II. Multi-Interface: Python API + CLI + web component
- ✅ III. Validation-First: 1300+ IAPWS reference points for validation
- ✅ IV. Public Domain Data: IAPWS-IF97 is public standard
- ✅ V. Cost-Free: No external services, zero monthly cost
- ✅ VI. Developer Productivity: Type hints, NumPy docstrings, clear structure
- ✅ VII. Simplicity: MVP scope, YAGNI applied, explicit fail on instability
