# Feature Specification: Thermodynamic Extension

**Feature Branch**: `002-thermodynamic-models`
**Created**: 2025-12-30
**Status**: Draft
**Input**: User description: "Thermodynamic Extension with Van der Waals EOS, Ideal Gas Law, and Basic Flash Calculation implementations"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Calculate Van der Waals Properties (Priority: P1)

Engineers and researchers need to predict real gas behavior using the Van der Waals equation of state, which accounts for molecular interactions and finite molecular volume - critical for systems where ideal gas assumptions fail (high pressures, low temperatures, near-critical conditions).

**Why this priority**: Van der Waals is a fundamental improvement over ideal gas for real-world chemical engineering calculations. It's a direct parallel to the existing Peng-Robinson implementation and provides broader coverage of thermodynamic models.

**Independent Test**: Can be fully tested by calculating Van der Waals properties for a pure compound (pressure, volume, temperature relationships) and validating against published reference data. Delivers value for engineers needing non-ideal gas behavior predictions.

**Acceptance Scenarios**:

1. **Given** a compound with critical properties (Tc, Pc) and T, P conditions, **When** calculating Van der Waals volume, **Then** the result matches published reference values within 2% error
2. **Given** Van der Waals volume is calculated, **When** deriving compressibility factor, **Then** Z = PV/nRT matches expected behavior (Z < 1 for attractive forces, Z > 1 for repulsive forces)
3. **Given** invalid input (negative absolute temperature, negative pressure), **When** attempting calculation, **Then** the system raises a clear validation error with descriptive message

---

### User Story 2 - Calculate Ideal Gas Properties with Cross-Model Comparison (Priority: P1)

Engineers need a reference model (ideal gas law) to compare against more complex equations of state. The ideal gas model serves as a baseline and benchmark for evaluating when more sophisticated models are necessary.

**Why this priority**: Ideal Gas Law is the simplest thermodynamic model and essential for educational purposes, quick estimates, and validating that more complex models produce reasonable results. Cross-model comparison enables engineers to understand the impact of non-ideality.

**Independent Test**: Can be fully tested by calculating ideal gas properties (P, V, T relationships) and comparing outputs against Van der Waals and Peng-Robinson for the same conditions. Delivers value as a reference model and learning tool.

**Acceptance Scenarios**:

1. **Given** ideal gas parameters (n moles, T, P), **When** calculating volume, **Then** V = nRT/P is returned
2. **Given** ideal gas volume is calculated, **When** deriving compressibility factor, **Then** Z = 1.0 exactly (by definition)
3. **Given** three EOS models (Ideal, Van der Waals, Peng-Robinson), **When** comparing compressibility factors at same T, P, **Then** all three values are returned and displayable for comparison

---

### User Story 3 - Perform Pressure-Temperature Flash Calculation (Priority: P2)

Process engineers need to determine vapor-liquid equilibrium (phase split composition and amounts) at specified pressure and temperature. Flash calculations are essential for distillation, separation processes, and phase stability analysis.

**Why this priority**: Flash calculations enable phase behavior predictions needed for unit operations design. PT flash is the most straightforward variant and provides practical value for basic separation process modeling.

**Independent Test**: Can be fully tested by performing a two-phase flash at specified P and T and validating that resulting liquid and vapor compositions satisfy energy and material balances within numerical precision. Delivers value for separation process design.

**Acceptance Scenarios**:

1. **Given** feed composition and T, P conditions, **When** performing PT flash, **Then** system returns extended output: phase amounts (L, V), composition vectors (x_i, y_i), K-values, iteration count, success flag, and convergence tolerance achieved (or indicates single-phase if applicable, returning L=0/V=1 or L=1/V=0)
2. **Given** PT flash is complete, **When** checking material balance, **Then** overall composition equals weighted average of liquid and vapor: z_i = L*x_i + V*y_i (within 1e-6 tolerance)
3. **Given** equilibrium fugacities calculated using Peng-Robinson EOS, **When** comparing vapor and liquid fugacities, **Then** |f_i^vapor / f_i^liquid - 1| < 1e-6 for all components (indicating equilibrium)

### Edge Cases

- **Single-phase detection**: When system is above critical temperature (T > Tc) or feed is pure component (n_components == 1), flash MUST detect this before Rachford-Rice iteration and return early: L=0/V=1 for vapor region or L=1/V=0 for liquid region based on pressure relative to saturation
- **Temperature/pressure bounds**: When temperature < 0K or pressure < 0 Pa, system MUST reject with validation error; when T > Tc and P < Pc, system returns single-phase vapor; when T near Tc with P near Pc, numerical precision may fail (see below)
- **Convergence failure**: When Rachford-Rice iteration does not converge within 50 iterations at 1e-6 tolerance, system MUST return failure flag and last known K-values; do not force convergence or return partial results
- **Missing compound data**: When Tc, Pc, or ω unavailable from database, system MUST raise clear error identifying missing property; do not assume values or continue with incomplete data
- **Critical point proximity**: When system state approaches critical point (T ≈ Tc, P ≈ Pc), iteration may be slow or numerically unstable; specification does not guarantee convergence in critical region

## Clarifications

### Session 2025-12-30

- Q: Flash calculation input/output interface structure? → A: Extended output includes phase amounts (L, V), composition vectors (x_i, y_i), success flag, K-values, iteration count, and convergence tolerance achieved
- Q: Single-phase flash behavior (pure components or supercritical)? → A: Early detection before iteration; returns L=0/V=1 (vapor) or L=1/V=0 (liquid) based on pressure region and critical temperature
- Q: Convergence tolerance for equilibrium condition f_i^vapor ≈ f_i^liquid? → A: Fugacity ratio error |f_i^v / f_i^l - 1| must be < 1e-6

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST provide Van der Waals equation of state implementation with module interface matching Peng-Robinson pattern (vdw.py module)
- **FR-002**: System MUST calculate Van der Waals compressibility factor Z and molar volume given T and P for a specified compound
- **FR-003**: System MUST provide Ideal Gas Law implementation with consistent module interface (ideal.py module)
- **FR-004**: System MUST calculate ideal gas volume and compressibility factor (Z=1.0) given n moles, T, and P
- **FR-005**: System MUST enable side-by-side comparison of compressibility factors from Ideal, Van der Waals, and Peng-Robinson models for identical conditions
- **FR-006**: System MUST provide PT (pressure-temperature) flash calculation for binary or multicomponent mixtures, returning extended output: phase amounts (L, V), composition vectors (x_i, y_i), success flag, K-values (partitioning ratios), iteration count, and convergence tolerance achieved
- **FR-007**: System MUST use Peng-Robinson EOS for fugacity calculations during flash iterations
- **FR-008**: System MUST validate input parameters (absolute temperature ≥ 0K, absolute pressure ≥ 0 Pa) and provide clear error messages for invalid inputs; flash calculations MUST enforce fugacity equilibrium tolerance: |f_i^vapor / f_i^liquid - 1| < 1e-6
- **FR-009**: System MUST include validation tests comparing results against published thermodynamic reference data (NIST, literature values)
- **FR-010**: System MUST update documentation with examples showing Van der Waals, Ideal Gas, and Flash calculation usage

### Key Entities

- **Compound Properties**: Critical temperature (Tc), critical pressure (Pc), acentric factor (ω) - define physical substance behavior
- **State Variables**: Temperature (T), Pressure (P), composition (mole fractions z_i) - define thermodynamic conditions
- **Equilibrium Results**: Liquid mole fraction (L), vapor mole fraction (V), phase compositions (x_i, y_i) - output of flash calculation
- **Fugacity**: Effective pressure of component in phase - measure of escaping tendency, used for equilibrium condition f_i^liquid = f_i^vapor

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: Van der Waals compressibility factors match NIST reference data within 2% for test compounds across diverse T, P ranges
- **SC-002**: Ideal Gas Law calculations are exact (Z = 1.0 always) and demonstrate baseline against non-ideal models
- **SC-003**: PT flash calculations converge in under 50 iterations for standard binary mixtures with typical convergence tolerance
- **SC-004**: Flash results satisfy material balance (composition error < 1e-6 mol basis), fugacity equilibrium (|f_i^v / f_i^l - 1| < 1e-6), and energy balance requirements
- **SC-005**: All three EOS models (Ideal, VDW, PR) are directly comparable in single function call/output, enabling engineers to evaluate model selection impact
- **SC-006**: Module interfaces follow established Peng-Robinson pattern, enabling consistent API across all thermodynamic models
- **SC-007**: Documentation includes worked examples for each calculation with expected outputs and validation against reference data

## Assumptions

1. **Thermodynamic Model Scope**: Calculations assume binary or simple multicomponent mixtures (2-5 components); full hydrocarbon mixtures (C1-C20+) may require enhanced fugacity model
2. **Convergence Behavior**: PT flash convergence assumes typical behavior near bubble/dew points; convergence may be slow or fail very close to critical point
3. **Property Data**: Compound critical properties (Tc, Pc, ω) are available from existing JSON database or provided by user
4. **Unit Consistency**: All calculations assume consistent SI units (K for temperature, Pa for pressure); unit conversion handled by Pint integration
5. **Validation Reference**: Reference data for validation sourced from NIST or peer-reviewed thermodynamic databases; some compounds may lack complete reference data
6. **Flash Algorithm**: PT flash uses iterative approach (Rachford-Rice) with standard Peng-Robinson fugacity model; more advanced approaches (adaptive, hybrid) not in scope
