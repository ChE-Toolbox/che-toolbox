# Feature Specification: Core Fluid Calculations

**Feature Branch**: `003-fluid-calculations`
**Created**: 2025-12-30
**Status**: Draft
**Input**: User description: "Core fluid calculations - Pipe Flow Module, Pump Sizing, Valve Sizing"

## Clarifications

### Session 2025-12-30

- Q1: Interaction Model → A: Hybrid (API + CLI) - System provides both programmatic Python library interface and command-line tool for direct engineer use
- Q2: Pump & Valve Data Sources → A: Hybrid (hardcoded + user input) - System ships with reference library of common pump types and valve models; engineers can override or add custom equipment specifications
- Q3: Transitional Flow Zone (Re 2300–4000) → A: Warn and use laminar - System issues warning when Reynolds number falls in transitional zone, then applies laminar friction factor (f = 64/Re) as conservative approach
- Q4: Calculation Transparency Format → A: Configurable verbosity - System supports multiple output styles (minimal, standard, detailed) selectable by user at runtime; JSON for API, formatted text for CLI
- Q5: Batch Processing & Workflows → A: No batch support initially - Each API call or CLI invocation performs single-item calculation; batch operations handled externally by user scripts. Batch/workflow features deferred to Phase 2 based on user demand

## Scope & Out-of-Scope

**In Scope (Phase 1)**:
- Single-item calculations (one pipe flow, one pump size, one valve check per invocation)
- Python API and CLI interfaces
- Built-in reference libraries for common pump types and valve models
- User-provided custom equipment specifications
- Configurable calculation transparency (minimal/standard/detailed)
- Unit conversion and validation

**Out of Scope (Deferred to Phase 2)**:
- Batch processing of multiple items in a single call
- Workflow orchestration (e.g., automatically sizing an entire system)
- Persistent project storage or design iteration history
- Export to PDF, Excel, or other document formats
- Optimization (e.g., "find the optimal pump given these constraints")
- Real-time interactive UI / GUI interfaces
- Non-Newtonian fluid behavior
- Transient or unsteady-state flow analysis
- Multiphase flow (e.g., gas-liquid mixtures)

## Interface & API Contract

The system exposes two primary interfaces:

1. **Python API**: Core calculations available as importable Python functions/classes for integration into larger engineering workflows, data pipelines, and third-party applications
2. **CLI**: Command-line interface accepting JSON or parameter-based inputs, returning formatted calculation results for standalone engineer use

Both interfaces expose the same underlying calculation engines to ensure consistency. Batch operations are handled externally by user scripts, shells, or workflow orchestration tools.

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

### User Story 1 - Calculate Pipe Flow Properties (Priority: P1)

Engineers and system designers need to determine if a fluid can be transported through a pipe at a given flow rate. They need to calculate the Reynolds number, friction factor, and pressure drop across the pipe to ensure:
- The flow regime (laminar, turbulent, or transitional) is appropriate
- The friction factor is accurately determined based on pipe roughness and flow conditions
- The pressure drop doesn't exceed system capacity

This is foundational for all piping system design and is the most critical capability.

**Why this priority**: Pipe flow calculations are the fundamental building block for fluid system design. Without accurate pipe flow analysis, all downstream calculations (pump sizing, valve sizing) cannot be properly specified. This is essential for any fluid engineering application.

**Independent Test**: Can be fully tested by providing pipe diameter, fluid properties, flow rate, and pipe roughness, then validating calculated Reynolds number, friction factor (against Crane TP-410 reference), and pressure drop against known reference values.

**Acceptance Scenarios**:

1. **Given** a pipe with known diameter, fluid viscosity, density, and flow rate, **When** the Reynolds number is calculated, **Then** the result matches the standard formula (ρVD/μ) and is correctly classified as laminar (Re < 2300), transitional, or turbulent (Re > 4000)

2. **Given** turbulent flow conditions and a known pipe roughness, **When** the friction factor is calculated using Churchill or Colebrook equation, **Then** the result falls within ±5% of Crane TP-410 tabulated values

3. **Given** calculated friction factor, pipe diameter, length, fluid density, and velocity, **When** Darcy-Weisbach pressure drop is calculated, **Then** the result matches the reference formula and is validated against Crane TP-410 data

4. **Given** laminar flow conditions (Re < 2300), **When** friction factor is calculated, **Then** the system uses the analytical solution f = 64/Re regardless of roughness

---

### User Story 2 - Size Pump for System Requirements (Priority: P2)

Equipment engineers need to select or specify pumps that will move fluid through a system while overcoming various resistances. They need to calculate:
- The total head required (static, dynamic, friction losses)
- The power requirements to determine motor sizing
- The NPSH (Net Positive Suction Head) required to prevent cavitation

This enables proper pump selection and ensures reliable system operation.

**Why this priority**: Pump sizing depends on pipe flow calculations (to determine friction losses) but is distinct enough to be a separate engineering task. Many applications need pump sizing once pipe characteristics are known. This is essential for any system that transports fluids.

**Independent Test**: Can be fully tested by providing system elevation changes, fluid properties, total pipe friction losses, desired flow rate, and pump specifications. System can calculate required head, power, and NPSH requirements and validate against pump performance curves and industry standards.

**Acceptance Scenarios**:

1. **Given** system elevation changes, friction losses, and desired flow rate, **When** total head is calculated, **Then** the result correctly accounts for static head (elevation difference), dynamic head (velocity head), and friction losses

2. **Given** total head, volumetric flow rate, fluid density, and pump efficiency, **When** power requirement is calculated, **Then** the result matches the standard formula (Q × ρ × g × H / η) and is expressed in appropriate units

3. **Given** pump inlet conditions, fluid properties, and flow rate, **When** NPSH required is calculated, **Then** the system identifies whether cavitation risk exists and suggests corrective measures

4. **Given** variable flow rates and system conditions, **When** power requirements are recalculated, **Then** the results demonstrate accurate scaling with flow rate and head

---

### User Story 3 - Size Valves for Flow Control (Priority: P3)

Control system engineers need to select valves that will control or restrict flow to the desired rate. They need to calculate:
- The Cv (flow coefficient) needed for a given flow rate and pressure drop
- The flow coefficient available from valve datasheets
- The pressure drop across different valve configurations

This ensures proper valve selection to achieve desired control objectives.

**Why this priority**: Valve sizing is important but depends on prior knowledge of desired flow rate and acceptable pressure drop (which typically comes from pipe flow and pump analysis). This is needed for complete system design but builds on earlier calculations.

**Independent Test**: Can be fully tested by providing desired flow rate, fluid properties, inlet/outlet pressures, and valve type. System can calculate required Cv, determine if standard valve sizes meet requirements, and calculate actual pressure drop across selected valve.

**Acceptance Scenarios**:

1. **Given** desired flow rate, fluid specific gravity, and pressure drop across valve, **When** required Cv is calculated, **Then** the result matches the standard formula (Q = Cv × √(ΔP/SG)) with proper unit conversions

2. **Given** a valve with known Cv and operating pressure drop, **When** actual flow rate is calculated, **Then** the result accurately predicts valve performance across the operating range

3. **Given** multiple valve size options, **When** pressure drops are calculated for each, **Then** the system identifies which sizes provide acceptable pressure drop and control characteristics

---

### Edge Cases

- **Transitional flow zone (Re 2300–4000)**: System identifies zone via Reynolds number classification and issues a warning, then applies laminar friction factor (f = 64/Re) as conservative estimate (see FR-004a)
- **Very low Reynolds numbers (laminar flow with negligible friction)**: System correctly applies f = 64/Re; pressure drop approaches zero as expected in very viscous flows at low velocity
- **Over-sizing valve condition** (required Cv exceeds available sizes): System identifies the mismatch in comparison logic and returns an error indicating which standard sizes are available and recommends using the largest available or implementing parallel valves
- **Non-Newtonian fluids** (high viscosity, thixotropic, pseudoplastic behavior): System defaults to Newtonian assumption; engineers must manually adjust viscosity input or request out-of-scope analysis
- **Cavitation risk** (NPSH available < NPSH required): System calculates the deficit, issues a warning, and returns the cavitation margin; suggests corrective measures (increase inlet pressure, reduce flow rate, or select pump with lower NPSH requirement)

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST calculate Reynolds number using the formula Re = ρVD/μ, where ρ is fluid density, V is flow velocity, D is pipe diameter, and μ is dynamic viscosity

- **FR-002**: System MUST correctly classify flow regime as laminar (Re < 2300), transitional (2300 ≤ Re ≤ 4000), or turbulent (Re > 4000)

- **FR-003**: System MUST calculate friction factor for laminar flow using f = 64/Re regardless of pipe roughness

- **FR-004**: System MUST calculate friction factor for turbulent flow using either the Colebrook equation (implicit) or Churchill equation (explicit), with results validated against Crane TP-410 within ±5%

- **FR-004a**: System MUST handle transitional flow zone (2300 ≤ Re ≤ 4000) by issuing a warning and applying the laminar friction factor solution (f = 64/Re) as a conservative estimate, since transitional regime lacks universal correlation

- **FR-005**: System MUST calculate Darcy-Weisbach pressure drop using ΔP = f × (L/D) × (ρV²/2), where L is pipe length, D is pipe diameter, f is friction factor, ρ is fluid density, and V is flow velocity

- **FR-006**: System MUST calculate total pump head as the sum of static head, dynamic (velocity) head, and friction losses in the system

- **FR-007**: System MUST calculate pump power requirement using Power = Q × ρ × g × H / η, where Q is volumetric flow rate, ρ is fluid density, g is gravitational acceleration, H is total head, and η is pump efficiency

- **FR-008**: System MUST calculate NPSH required based on pump type and flow rate, and compare against available NPSH to identify cavitation risk

- **FR-009**: System MUST calculate required Cv (flow coefficient) using the formula Cv = Q / √(ΔP/SG), where Q is volumetric flow rate, ΔP is pressure drop across valve, and SG is fluid specific gravity

- **FR-010**: System MUST predict actual flow rate through a valve given Cv and pressure drop using Q = Cv × √(ΔP/SG)

- **FR-011**: System MUST handle unit conversions between different unit systems (SI, US customary) and ensure results are expressed in user-specified units

- **FR-012**: System MUST validate input parameters for physical reasonableness (positive pipe diameters, positive viscosity, valid flow regimes) and provide clear error messages for invalid inputs

- **FR-013**: System MUST provide reference calculations (showing intermediate results) to allow engineers to verify calculations and understand the analysis. Output format MUST support configurable verbosity levels:
  - *Minimal*: Final results only with brief calculation summary (e.g., "Re = 2500 (turbulent)")
  - *Standard* (default): Intermediate values, key equations with substituted values, units, and warnings
  - *Detailed*: Complete calculation tree with all dependencies, alternative formulas considered, and reference data sources

### Key Entities *(include if feature involves data)*

- **Pipe**: Represents a pipe section with diameter, length, absolute roughness, material, and fluid properties
- **Fluid**: Contains properties needed for calculations (density, dynamic viscosity, specific gravity) with temperature and pressure dependencies
- **Pump**: Specifications including design point (flow, head, power), efficiency curve, NPSH required, and pump type. Data sourced from reference library (common industrial pump models) or user-provided equipment specifications (from manufacturer datasheets)
- **Valve**: Specifications including nominal size, Cv rating across different opening positions, rangeability, and valve type. Data sourced from reference library (standard commercial valve models) or user-provided specifications (from vendor datasheets)
- **System**: Complete piping system with multiple pipes, elevation changes, pumps, valves, and overall operating conditions

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: Pipe flow calculations (Reynolds, friction factor, pressure drop) match Crane TP-410 reference data within ±5% for a comprehensive validation dataset covering laminar, transitional, and turbulent regimes across multiple pipe sizes and materials

- **SC-002**: Pump sizing calculations (head, power, NPSH) produce results consistent with manufacturer pump curves and industry standard methods for at least 10 representative pump types and system configurations

- **SC-003**: Valve sizing calculations correctly predict valve flow performance within ±10% of valve manufacturer data across at least 3 different valve types (ball, gate, globe)

- **SC-004**: All input validation catches invalid parameters and provides clear, actionable error messages that engineers can use to correct inputs without ambiguity about what failed

- **SC-005**: Engineers can complete a full pipe-pump-valve sizing analysis (minimum 5 pipes, 1 pump, 2 valves) and obtain all results in under 2 minutes with the system providing step-by-step calculation breakdowns

- **SC-006**: Automated regression tests validate all calculations against reference datasets on every code change, preventing calculation accuracy degradation

## Assumptions

- **Flow behavior**: All fluids are assumed to be Newtonian (constant viscosity under shear stress) unless specified otherwise
- **Pipe properties**: Absolute roughness values follow standard engineering references (e.g., Crane TP-410) for common materials
- **Units**: System will default to SI units (meters, kilograms, seconds, Pascals) with configurable output to other unit systems
- **Steady-state flow**: All calculations assume steady-state, incompressible flow conditions
- **Reference standards**: Friction factor calculations and validation will use Crane TP-410 as the primary reference authority
- **Pump performance**: Pump efficiency values default to manufacturer data or industry standard relationships if not provided
- **Cavitation**: NPSH calculations assume dissolved gas content typical of water systems; other fluids may need adjustments
- **Valve characteristics**: Valve Cv values are assumed constant across the operating range (linear behavior) unless specified as variable
