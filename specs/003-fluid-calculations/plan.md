# Implementation Plan: Core Fluid Calculations

**Branch**: `003-fluid-calculations` | **Date**: 2025-12-30 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-fluid-calculations/spec.md`

## Summary

Implement core fluid mechanics calculations (pipe flow analysis, pump sizing, valve sizing) as a Python library with Python API and CLI interfaces. The system provides dimensionally-aware calculations for engineering design with validation against Crane TP-410 reference data. Supports hybrid data sourcing: built-in reference libraries for common equipment plus user-provided specifications from datasheets. Single-item calculation design with configurable output verbosity (minimal/standard/detailed).

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: NumPy 1.24+, SciPy 1.10+ (Brent's method for friction factor), Pint 0.23+ (units), Pydantic 2.x (validation)
**Storage**: JSON configuration files for reference data (pumps, valves, pipe materials)
**Testing**: pytest with mypy --strict type checking
**Target Platform**: CLI + Python library (cross-platform: Linux, macOS, Windows)
**Project Type**: Single Python library (core) + CLI wrapper + data files
**Performance Goals**: Single calculations <100ms; CLI tool startup <500ms
**Constraints**: <200MB memory per calculation; no external API dependencies (fully offline)
**Scale/Scope**: 13 functional requirements, 3 user stories (P1/P2/P3), ~2000-3000 LOC core library expected

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with [ChemEng Toolbox Constitution](../../.specify/memory/constitution.md):

- [x] **I. Library-First**: Feature is standalone Python library in `src/fluids/` (self-contained, independently testable, dimensionally-aware)
- [x] **II. Multi-Interface**: Plan includes Python API (library imports) + CLI (command-line tool). Web interface deferred to Phase 2
- [x] **III. Validation-First**: Literature sources identified (Crane TP-410, engineering handbooks, Perry's Chemical Engineers' Handbook). Validation tests required for all calculations
- [x] **IV. Public Domain Data**: Reference libraries built from public sources (Crane TP-410, standard engineering data). No proprietary DIPPR or paid databases
- [x] **V. Cost-Free**: Fully offline, no external APIs, no cloud dependencies. JSON data files only
- [x] **VI. Developer Productivity**: Clear module structure, full type hints, comprehensive docstrings (NumPy style), documentation
- [x] **VII. Simplicity**: Single-item calculations (no batch support), no premature optimization, core calculations only, defer Phase 2 features (GUIs, optimizers, export)

**Violations**: None. Plan fully complies with all seven principles.

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
src/fluids/
├── __init__.py              # Package exports
├── core/
│   ├── __init__.py
│   ├── models.py            # Pydantic models (Pipe, Fluid, Pump, Valve, System)
│   ├── validators.py        # Input validation and physical reasonableness checks
│   └── calculations.py      # Core calculation engines
├── pipe/
│   ├── __init__.py
│   ├── reynolds.py          # Reynolds number calculation
│   ├── friction.py          # Friction factor (laminar, transitional, turbulent)
│   └── pressure_drop.py     # Darcy-Weisbach pressure drop
├── pump/
│   ├── __init__.py
│   ├── head.py              # Static, dynamic, total head calculations
│   ├── power.py             # Power requirement calculations
│   └── npsh.py              # NPSH required and available calculations
├── valve/
│   ├── __init__.py
│   ├── cv.py                # Cv calculations and flow coefficient
│   └── performance.py       # Valve sizing and performance curves
├── units/
│   ├── __init__.py
│   └── converter.py         # Unit conversion utilities using Pint
├── references/
│   ├── __init__.py
│   ├── pumps.json           # Reference pump database
│   ├── valves.json          # Reference valve database
│   ├── pipes.json           # Pipe roughness and material data
│   └── fluids.json          # Common fluid properties (water, oil, etc.)
├── output/
│   ├── __init__.py
│   └── formatter.py         # Verbosity-level output formatting (minimal/standard/detailed)
└── cli/
    ├── __init__.py
    ├── main.py              # CLI entry point and command routing
    ├── pipe_commands.py     # Pipe flow CLI commands
    ├── pump_commands.py     # Pump sizing CLI commands
    └── valve_commands.py    # Valve sizing CLI commands

tests/
├── conftest.py              # pytest fixtures (sample inputs, reference data)
├── unit/
│   ├── test_reynolds.py
│   ├── test_friction.py
│   ├── test_pressure_drop.py
│   ├── test_pump_head.py
│   ├── test_pump_power.py
│   ├── test_npsh.py
│   ├── test_valve_cv.py
│   ├── test_validators.py
│   └── test_units.py
├── validation/
│   ├── test_pipe_crane_410.py      # Validation against Crane TP-410
│   ├── test_pump_curves.py         # Validation against pump manufacturer data
│   └── test_valve_cv_data.py       # Validation against valve manufacturer data
└── integration/
    ├── test_cli_pipe.py
    ├── test_cli_pump.py
    └── test_cli_valve.py
```

**Structure Decision**: Single Python library with modular organization (pipe/pump/valve packages). CLI wrapper as thin interface to core library. Reference data as JSON files (user-extensible). Tests organized by type (unit/validation/integration) per Constitution principle III.

## Complexity Tracking

No violations. All seven constitutional principles are satisfied without exceptions.

---

## Phase 0: Research & Discovery

### Research Tasks

1. **Friction Factor Correlations**
   - Task: Evaluate Colebrook vs Churchill equations for turbulent friction factor calculation
   - Sources: Crane TP-410, Perry's Chemical Engineers' Handbook, fluid mechanics textbooks
   - Deliverable: Decision on preferred equation (or hybrid approach) with error bounds

2. **Pump NPSH Calculation Methods**
   - Task: Research NPSH required calculation approaches and cavitation margin strategies
   - Sources: Pump manufacturer standards, hydraulics engineering references
   - Deliverable: NPSH calculation method and warning thresholds

3. **Valve Cv Database Content**
   - Task: Identify publicly available valve Cv data for common valve types (ball, gate, globe)
   - Sources: Industry standards, manufacturer datasheets, engineering references
   - Deliverable: JSON schema for valve reference data with sample entries

4. **Transitional Zone (Re 2300-4000) Best Practice**
   - Task: Research industry practice for handling transitional flow zone calculations
   - Sources: Crane TP-410, engineering standards, textbooks
   - Deliverable: Validation of Q3 decision (warn + use laminar) or alternatives

5. **Unit Conversion with Pint**
   - Task: Research Pint library best practices for engineering calculations
   - Sources: Pint documentation, engineering Python examples
   - Deliverable: Unit strategy (dimensional analysis throughout, convert at I/O, or hybrid)

### Expected Research Output

File: `research.md` (Phase 0 deliverable)
- Decision on friction factor method
- NPSH calculation approach
- Valve/pump database schema decisions
- Unit handling strategy
- Validation data sources and tolerance thresholds

---

## Phase 1: Design & Contracts

### Data Model Design

**File**: `data-model.md`

Entity definitions with Pydantic schema:

```text
Fluid
├── density: float (kg/m³) with temperature dependency
├── dynamic_viscosity: float (Pa·s) with temperature dependency
├── specific_gravity: float (dimensionless)
└── properties: dict (extensible for custom fluids)

Pipe
├── diameter: float (m)
├── length: float (m)
├── absolute_roughness: float (m)
├── material: str (lookup to reference data)
└── fluid: Fluid

Pump
├── name: str
├── type: str (centrifugal, positive-displacement, etc.)
├── design_point: PumpPoint (Q, H, efficiency)
├── npsh_required: float (m)
├── efficiency_curve: dict (Q vs η points)
└── source: str (reference_library or user_provided)

Valve
├── name: str
├── type: str (ball, gate, globe, etc.)
├── nominal_size: str (1", 2", etc.)
├── cv_rating: float or dict (CV vs opening %)
├── rangeability: float
└── source: str (reference_library or user_provided)

System
├── pipes: list[Pipe]
├── pumps: list[Pump]
├── valves: list[Valve]
├── elevation_changes: list[float]
└── operating_conditions: dict
```

### API Contracts

**File**: `contracts/api.md` (Python library interface)

Core module exports:

```python
fluids.pipe.calculate_reynolds(density, velocity, diameter, viscosity) -> float
fluids.pipe.calculate_friction_factor(reynolds, roughness) -> dict (f, method, warnings)
fluids.pipe.calculate_pressure_drop(friction, length, diameter, velocity, density) -> float

fluids.pump.calculate_total_head(static_head, dynamic_head, friction_losses) -> float
fluids.pump.calculate_power(flow_rate, density, gravity, head, efficiency) -> float
fluids.pump.calculate_npsh_available(inlet_pressure, vapor_pressure, height) -> float
fluids.pump.calculate_npsh_required(pump_type, flow_rate) -> float

fluids.valve.calculate_cv_required(flow_rate, pressure_drop, specific_gravity) -> float
fluids.valve.calculate_flow_rate(cv, pressure_drop, specific_gravity) -> float

fluids.references.load_pump_library(custom_json=None) -> dict
fluids.references.load_valve_library(custom_json=None) -> dict

fluids.output.format_calculation(result, verbosity='standard') -> str | dict
```

### CLI Contracts

**File**: `contracts/cli.md` (Command-line interface)

```bash
# Pipe flow calculations
fluids pipe reynolds --density 1000 --velocity 2 --diameter 0.05 --viscosity 0.001

# Pump sizing
fluids pump head --static 10 --dynamic 0.5 --friction 5

# Valve sizing
fluids valve cv --flow 100 --pressure-drop 50 --specific-gravity 1.0

# Output control
--output-format [json|text]
--verbosity [minimal|standard|detailed]
```

### API Documentation

**File**: `quickstart.md`

- Installation and setup
- Basic usage examples (pipe flow, pump, valve)
- Common workflows
- Error handling
- Reference data customization

### Agent Context Update

Run: `.specify/scripts/bash/update-agent-context.sh claude`

Updates agent with:
- New technologies: NumPy, SciPy, Pint, Pydantic usage patterns
- Calculation validation approach
- Unit handling strategy
- Reference data structure

---

## Gate 2: Constitution Re-Check

After Phase 1 design completion:

- [x] **Library-First**: Core calculations isolated in `src/fluids/` with no external I/O
- [x] **Multi-Interface**: Python API + CLI fully specified in contracts
- [x] **Validation-First**: Literature sources identified in research phase
- [x] **Public Domain Data**: JSON reference files from public sources only
- [x] **Cost-Free**: No external dependencies, fully self-contained
- [x] **Developer Productivity**: Modular structure with clear responsibilities
- [x] **Simplicity**: Single-item design, no batch/UI features in Phase 1

**Result**: PASS - Ready to proceed to task decomposition phase

---

## Next Steps

1. Run `/speckit.tasks` to generate detailed task breakdown (tasks.md)
2. Implement Phase 1 artifacts (data-model.md, contracts/, quickstart.md)
3. Begin implementation with research phase outputs
4. Phase 2 enhancements deferred (batch processing, GUI, optimization)
