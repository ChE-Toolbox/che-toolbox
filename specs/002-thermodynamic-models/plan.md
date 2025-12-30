# Implementation Plan: Thermodynamic Extension

**Branch**: `002-thermodynamic-models` | **Date**: 2025-12-30 | **Spec**: [Feature Spec](./spec.md)
**Input**: Feature specification from `/specs/002-thermodynamic-models/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Extend the existing Peng-Robinson EOS library with two additional equations of state (Van der Waals and Ideal Gas Law) and implement a basic PT flash calculation. The feature delivers three independently testable components: (1) Van der Waals solver matching PR pattern, (2) Ideal Gas reference model with cross-model comparison, (3) PT flash using Rachford-Rice iteration. All calculations validated against NIST reference data; fugacity equilibrium enforced at 1e-6 tolerance; single-phase detection prevents unnecessary iterations.

## Technical Context

**Language/Version**: Python 3.11+ (matches existing Peng-Robinson implementation)
**Primary Dependencies**: NumPy 1.24+ (polynomial roots), SciPy 1.10+ (Brent optimization), Pint 0.23+ (unit handling), Pydantic 2.x (validation)
**Storage**: JSON files for compound database (existing infrastructure); NIST reference data for validation
**Testing**: pytest with >80% coverage, mypy --strict type checking, validation tests against NIST
**Target Platform**: Python library (server/CLI/web calculator)
**Project Type**: Single library with multi-interface (library API, CLI, web)
**Performance Goals**: Single EOS calculations <10ms, flash calculations <500ms for binary mixtures
**Constraints**: Van der Waals cubic solver must match PR pattern; flash convergence in <50 iterations at 1e-6 tolerance
**Scale/Scope**: Van der Waals + Ideal Gas modules (~300 lines each), PT flash implementation (~400 lines), validation tests (~200 lines)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with [ChemEng Toolbox Constitution](../../.specify/memory/constitution.md):

- [x] **I. Library-First**: Feature extends existing `src/eos/` library; new modules (vdw.py, ideal.py, flash.py) follow PR pattern
- [x] **II. Multi-Interface**: Library API exposed via vdw/ideal/flash modules; CLI wrapper via pr_calc pattern; web calculator integration planned
- [x] **III. Validation-First**: NIST reference data and literature examples identified; validation tests <2% error vs published values
- [x] **IV. Public Domain Data**: NIST WebBook and CoolProp (MIT licensed) used for validation; no proprietary databases
- [x] **V. Cost-Free**: No new paid services; NIST data is free, PyPI dependencies all open-source
- [x] **VI. Developer Productivity**: Clear module structure, NumPy docstrings, type hints, comprehensive test coverage
- [x] **VII. Simplicity**: No premature optimization; Rachford-Rice is standard algorithm; Van der Waals closely mirrors PR implementation

**Violations**: None identified. Feature fully complies with all seven principles.

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
src/eos/
├── __init__.py                  # Exports PengRobinsonEOS, VanDerWaalsEOS, IdealGasEOS
├── peng_robinson.py             # Existing PR implementation (no changes)
├── van_der_waals.py             # NEW: Van der Waals cubic solver
├── ideal_gas.py                 # NEW: Ideal Gas Law reference model
├── flash_pt.py                  # NEW: PT flash (Rachford-Rice iteration)
├── models.py                    # Existing models (Mixture, ThermodynamicState, etc.)
├── cubic_solver.py              # Existing cubic solver (reused by VDW)
├── exceptions.py                # Existing exceptions
├── units.py                     # Existing unit handling
└── mixing_rules.py              # Existing mixing rules

tests/unit/
├── test_peng_robinson.py        # Existing PR tests
├── test_van_der_waals.py        # NEW: VDW validation tests (2% NIST tolerance)
├── test_ideal_gas.py            # NEW: Ideal Gas tests (Z=1.0 verification)
├── test_flash_pt.py             # NEW: PT flash tests (convergence, balances)
└── test_integration.py          # NEW: Cross-EOS comparison tests

tests/validation/
├── vdw_nist_validation.py       # NEW: VDW vs NIST WebBook (literature examples)
├── flash_balance_tests.py       # NEW: Material/energy balance verification
└── reference_data/              # NEW: NIST reference data snapshots
```

**Structure Decision**: Extend existing single-project library structure. New modules follow established PR pattern (static methods, validation in __init__, logging). No new directories required; all code extends `src/eos/` namespace.

## Complexity Tracking

No violations identified. All principles satisfied by design.

---

## Phase 0: Research & Validation

**Objectives**: Resolve technical unknowns and identify reference data sources.

### Research Tasks

1. **Van der Waals Validation Data**
   - Source: NIST WebBook, Perry's Chemical Engineer's Handbook
   - Find: 5-10 compounds with P-V-T data at varying pressures/temperatures
   - Objective: Establish ±2% tolerance baselines for test cases

2. **PT Flash Algorithm Best Practices**
   - Review: Rachford-Rice stability analysis, convergence acceleration methods
   - Decision: Confirm Rachford-Rice is appropriate for 2-5 component mixtures
   - Constraint: Convergence must complete in <50 iterations

3. **Cubic Equation Root Selection**
   - Verify: Existing cubic_solver.py compatibility with Van der Waals
   - Both PR and VDW are cubic equations; confirm reusability

### Output: `research.md`
- Van der Waals validation tolerance confirmed (2% NIST)
- Reference data sources and literature citations
- Rachford-Rice implementation strategy confirmed
- Cubic solver reusability verified

---

## Phase 1: Design & Module Contracts

**Objectives**: Define data models, API contracts, and module interfaces.

### 1.1 Data Model (`data-model.md`)

**Flash Calculation Output** (clarified in spec):
```python
@dataclass
class FlashResult:
    L: float                    # Liquid phase mole fraction [0, 1]
    V: float                    # Vapor phase mole fraction [0, 1]
    x: np.ndarray              # Liquid compositions [mole fraction]
    y: np.ndarray              # Vapor compositions [mole fraction]
    K_values: np.ndarray       # Partitioning ratios [dimensionless]
    iterations: int            # Rachford-Rice iteration count
    tolerance_achieved: float  # Final |f_i^v / f_i^l - 1| value
    success: bool              # Convergence flag
```

**Van der Waals State**:
```python
@dataclass
class VDWState(ThermodynamicState):
    a: float                   # Pa*m^6*mol^-2
    b: float                   # m^3*mol^-1
    z: float                   # Compressibility factor
    v_molar: float             # Molar volume [m^3/mol]
```

### 1.2 Module Contracts (`contracts/`)

**ideal_gas.py**:
```python
class IdealGasEOS:
    @staticmethod
    def calculate_volume(n: float, T: float, P: float) -> float:
        """V = nRT/P"""

    @staticmethod
    def calculate_Z(P: float, T: float, V: float) -> float:
        """Z = PV/nRT (always 1.0 for ideal gas)"""
```

**van_der_waals.py**:
```python
class VanDerWaalsEOS:
    @staticmethod
    def calculate_a(tc: float, pc: float, T: float) -> float:
        """a = 27*R^2*Tc^2/(64*Pc)"""

    @staticmethod
    def calculate_b(tc: float, pc: float) -> float:
        """b = R*Tc/(8*Pc)"""

    def calculate_volume(self, tc: float, pc: float, T: float, P: float) -> float:
        """Solve cubic: (P + a/V^2)(V - b) = RT"""
```

**flash_pt.py**:
```python
class FlashPT:
    def calculate(
        self,
        feed: Mixture,
        T: float,
        P: float,
        eos: PengRobinsonEOS,
        tolerance: float = 1e-6,
        max_iterations: int = 50
    ) -> FlashResult:
        """PT flash using Rachford-Rice iteration"""
```

### 1.3 Quick Start (`quickstart.md`)

Example showing:
- Single-component VDW calculation (matches PR pattern)
- Ideal Gas comparison
- Binary mixture PT flash
- Cross-EOS compressibility factor comparison

### 1.4 Agent Context Update

Run `.specify/scripts/bash/update-agent-context.sh claude` to register:
- Van der Waals module pattern
- PT flash implementation approach
- Validation data sources

---

## Phase 2: Implementation & Testing

**Note**: Phase 2 execution deferred to `/speckit.tasks` command (NOT created by /speckit.plan).

Phase 2 will generate `tasks.md` with:
- Task T001-T010: Van der Waals implementation + tests
- Task T011-T015: Ideal Gas implementation + tests
- Task T016-T025: PT flash implementation + convergence tests
- Task T026-T035: Validation tests (NIST, literature, cross-EOS)
- Task T036-T040: CLI integration + documentation
