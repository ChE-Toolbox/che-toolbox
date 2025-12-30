# Feature Specification: IAPWS-IF97 Steam Properties

**Feature Branch**: `002-steam-properties`
**Created**: 2025-12-30
**Status**: Draft
**Input**: User description: "IAPWS-IF97 Implementation with validation suite and SteamTable user interface"

## Clarifications

### Session 2025-12-30

- Q: What is the scope of SteamTable convenience methods? → A: Core P-T lookups only (h_pt, s_pt, u_pt, rho_pt); saturation methods T_sat(P), P_sat(T); no quality-based inputs in MVP
- Q: How should numerical singularities near critical point be handled? → A: Explicit fail strategy; raise RuntimeError with clear diagnostic when singularity is detected; prevents silent errors in scientific calculations
- Q: What exception types and message format for error handling? → A: ValueError for input validation, RuntimeError for convergence failures; message format: "[Type]: [violation/reason]. [valid range or suggestion]"
- Q: How should units be represented in SteamTable API? → A: Return Pint Quantity objects with embedded unit metadata; provides full unit awareness without forcing external wrapping
- Q: Should SteamTable include built-in result caching? → A: No built-in caching; users can wrap with @lru_cache or implement caching layer; 10ms target is achievable with fresh computation

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

### User Story 1 - Engineers Calculate Thermodynamic Properties at Known Pressure-Temperature Conditions (Priority: P1)

Engineers and thermodynamics researchers need to quickly retrieve steam/water properties at any given pressure and temperature conditions. This is the most common use case in industrial applications, process design, and research.

**Why this priority**: This is the fundamental capability that all downstream features depend on. Without accurate P-T property lookups, nothing else is possible.

**Independent Test**: Can be tested by providing a set of known P-T conditions and validating results against official IAPWS-IF97 tables.

**Acceptance Scenarios**:

1. **Given** a pressure of 10 MPa and temperature of 500°C (Region 1), **When** a user queries steam properties, **Then** the system returns enthalpy ≈ 3373.7 kJ/kg with ±0.1% accuracy
2. **Given** a pressure of 0.1 MPa and temperature of 200°C (Region 2), **When** a user queries steam properties, **Then** the system returns entropy ≈ 7.5064 kJ/(kg·K) with ±0.1% accuracy
3. **Given** a pressure of 25 MPa and temperature of 640°C (Region 3), **When** a user queries steam properties, **Then** the system returns density with ±0.1% accuracy
4. **Given** invalid inputs (negative pressure, temperature below absolute zero), **When** a user queries properties, **Then** the system returns clear error messages

---

### User Story 2 - Engineers Find Saturation Properties at Saturation Line (Priority: P1)

Engineers need to determine saturation properties (where liquid and vapor coexist) for design of condensers, boilers, and steam systems.

**Why this priority**: Saturation line calculations are essential for most practical steam system designs and are frequently accessed alongside region calculations.

**Independent Test**: Can be tested by providing saturation temperatures or pressures and validating results against IAPWS saturation tables.

**Acceptance Scenarios**:

1. **Given** a saturation pressure of 0.1 MPa, **When** a user queries saturation properties, **Then** the system returns saturation temperature ≈ 99.63°C with ±0.01°C accuracy
2. **Given** a saturation temperature of 100°C, **When** a user queries saturation properties, **Then** the system returns saturation pressure ≈ 0.101 MPa with ±0.1% accuracy
3. **Given** saturation state at any valid condition, **When** a user queries, **Then** the system returns both liquid (f) and vapor (g) properties

---

### User Story 3 - Users Validate Implementation Against Official IAPWS Tables (Priority: P1)

Researchers and quality assurance teams need to verify that the implementation matches official IAPWS-IF97 reference values across all regions to ensure correctness and certification.

**Why this priority**: Validation against official standards is essential for scientific credibility and regulatory compliance. This must work before any public release.

**Independent Test**: Can be tested by running comprehensive test suite comparing against IAPWS supplementary tables.

**Acceptance Scenarios**:

1. **Given** a comprehensive set of test points from IAPWS official tables, **When** validation suite runs, **Then** all Region 1 points pass within ±0.03% (per IAPWS standard)
2. **Given** Region 2 test points, **When** validation suite runs, **Then** all points pass within ±0.06% accuracy
3. **Given** Region 3 test points, **When** validation suite runs, **Then** all points pass within ±0.2% accuracy (wider tolerance due to computational complexity)
4. **Given** critical point conditions (P=22.064 MPa, T=373.946 K), **When** validation runs, **Then** properties converge correctly with no singularities
5. **Given** triple point conditions (P=611.657 Pa, T=273.16 K), **When** validation runs, **Then** system handles this edge case correctly

---

### User Story 4 - Python Applications Access Steam Properties Via Convenient API (Priority: P2)

Developers integrating steam properties into larger thermodynamic or process simulation applications need a clean, intuitive Python interface that feels natural to use.

**Why this priority**: While the underlying calculations are essential (P1), the ergonomic API enables broader adoption and integration.

**Independent Test**: Can be tested by creating a simple simulation script that uses the SteamTable API without looking at implementation details.

**Acceptance Scenarios**:

1. **Given** a SteamTable instance, **When** calling `steam.h_pt(pressure=10, temperature=500)`, **Then** returns enthalpy as Pint Quantity with units (kJ/kg)
2. **Given** a SteamTable instance, **When** calling `steam.s_pt(pressure=0.1, temperature=200)`, **Then** returns entropy as Pint Quantity with units (kJ/(kg·K))
3. **Given** convenience methods available, **When** a developer accesses `steam.T_sat(pressure=1)`, **Then** returns saturation temperature as Pint Quantity with units (K)
4. **Given** property calculations for P-T inputs, **When** results are returned, **Then** all values are Pint Quantity objects with proper units embedded

### Edge Cases

- **Critical Point (22.064 MPa, 373.946 K)**: System raises `RuntimeError` with diagnostic message when singularity is detected; provides guidance on alternative conditions
- **Region Boundaries**: System correctly routes to appropriate region equations; raises `RuntimeError` if convergence fails at boundary transition
- **Saturation Line Precision**: Near saturation where properties change rapidly, system computes with full numerical precision; if stability cannot be guaranteed, raises `RuntimeError` with bounds information
- **Triple Point Conditions (611.657 Pa, 273.16 K)**: System handles correctly as valid saturation state; raises `ValueError` if user provides T < 273.16 K (below triple point)
- **Numerical Singularities in Region 3**: System detects approaching singularity near critical point and raises `RuntimeError` before result becomes unreliable; includes diagnostic: "Conditions too close to critical point for reliable computation"
- **Saturation Line Boundary Crossings**: System explicitly detects two-phase state attempts and raises `ValueError` specifying valid input ranges for single-phase queries

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST implement IAPWS-IF97 Region 1 equations for liquid water (6.8 MPa ≤ P ≤ 863.91 MPa, 273.15 K ≤ T ≤ 863.15 K)
- **FR-002**: System MUST implement IAPWS-IF97 Region 2 equations for steam (P ≤ 100 MPa, 273.15 K ≤ T ≤ 863.15 K, with lower pressure limits)
- **FR-003**: System MUST implement IAPWS-IF97 Region 3 equations for supercritical fluid (P ≥ 16.6 MPa, 623.15 K ≤ T ≤ 863.15 K)
- **FR-004**: System MUST calculate saturation properties at the saturation line (611.657 Pa ≤ P ≤ 22.064 MPa)
- **FR-005**: System MUST return fundamental properties: pressure (P), temperature (T), density (ρ), enthalpy (h), entropy (s), and internal energy (u)
- **FR-006**: System MUST handle P-T input combinations as MVP (P and T both specified); quality-based inputs (P-h, T-s, etc.) deferred to future phases
- **FR-007**: System MUST provide a SteamTable class with convenience methods for P-T lookups: `h_pt()`, `s_pt()`, `u_pt()`, `rho_pt()` returning derived quantities; saturation methods: `T_sat(P)`, `P_sat(T)` returning saturation properties; all return values as Pint Quantity objects with units
- **FR-008**: System MUST validate all input conditions and raise exceptions with structured error messages: `ValueError` for out-of-range inputs (message format: `"[Parameter]: [violation]. Valid range: [min-max]"`); `RuntimeError` for numerical convergence failures or singularities (message format: `"[Error]: [reason]. Suggestion: [action]"`)
- **FR-009**: System MUST correctly identify which region applies to given P-T conditions and use appropriate equations; raise `RuntimeError` if conditions lie on two-phase region boundary
- **FR-010**: System MUST include comprehensive test suite validating against official IAPWS-IF97 reference data
- **FR-011**: System MUST handle unit conversions and support both SI units (Pa, K, kJ/kg, kJ/(kg·K)) internally
- **FR-012**: System MUST document all region boundaries, input constraints, and accuracy information

### Key Entities *(include if feature involves data)*

- **Region 1 (Liquid Water)**: Represents compressed liquid water with defined boundaries and equations
- **Region 2 (Steam)**: Represents water vapor and superheated steam with defined boundaries and equations
- **Region 3 (Supercritical)**: Represents supercritical fluid states where distinct liquid/vapor phases don't exist
- **Saturation Line**: The boundary where liquid and vapor phases coexist, with unique properties for each phase
- **SteamTable**: The main user interface class providing convenient property calculation methods
- **ThermodynamicProperty**: Represents individual properties (enthalpy, entropy, etc.) with units and accuracy metadata

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: All Region 1 property calculations match IAPWS reference tables within ±0.03% across the entire valid domain
- **SC-002**: All Region 2 property calculations match IAPWS reference tables within ±0.06% across the entire valid domain
- **SC-003**: All Region 3 property calculations match IAPWS reference tables within ±0.2% across the entire valid domain
- **SC-004**: Saturation line property calculations match IAPWS tables within ±0.1% for both liquid and vapor phases
- **SC-005**: Test suite validates minimum 100 reference points per region with 100% pass rate before release
- **SC-006**: System correctly handles all documented edge cases (critical point, triple point, region boundaries) without numerical errors
- **SC-007**: Properties can be retrieved for any valid P-T combination in under 10 milliseconds on standard hardware (fresh computation; caching is user responsibility)
- **SC-008**: SteamTable API is usable by developers without reference to internal equations or region logic; all results include embedded unit metadata as Pint Quantity objects
- **SC-009**: All error conditions return appropriate exception types (`ValueError` for input validation; `RuntimeError` for numerical failures) with structured diagnostic messages following format `"[Error]: [reason]. [Suggestion or valid range]"`
- **SC-010**: Documentation includes complete region definitions, input constraints, accuracy claims, validation results, and exception handling guide (when each exception type is raised and how to handle)

## Assumptions

1. **IAPWS-IF97 Standard**: We will implement the full IAPWS-IF97 formulation as published by the International Association for the Properties of Water and Steam
2. **Unit System**: All calculations use SI units internally (Pa, K, kJ/kg, kJ/(kg·K)); unit conversion is the user's responsibility or handled by convenience wrappers
3. **Validation Source**: Official IAPWS-IF97 supplementary tables and reference data are the source of truth for validation
4. **Numerical Methods**: Root-finding for saturation properties and region boundary intersections can use standard optimization (Newton-Raphson, Brent's method)
5. **Accuracy Trade-offs**: Region 3 has wider tolerance (0.2%) due to the computational complexity of solving coupled nonlinear equations
6. **Quality vs Convenience**: The SteamTable convenience API is optional scaffolding; core requirement is accurate region calculations
7. **Python Implementation**: Using NumPy for polynomial evaluations and SciPy for optimization aligns with existing thermodynamics work

## Dependencies & Integration Points

- **NumPy 1.24+**: For polynomial evaluation and array operations in property calculations
- **SciPy 1.10+**: For root-finding and optimization (Brent's method for saturation properties)
- **Pint 0.23+**: For unit handling if property results need unit-aware outputs
- **Pydantic 2.x**: For input validation in SteamTable and convenience methods
- **Testing**: Pytest with reference NIST/IAPWS data for validation

## Out of Scope

- Implementation of other water formulations (IAPWS-95, IAPWS-06, etc.) - this is specifically IAPWS-IF97
- Two-phase flow properties or quality-dependent calculations beyond saturation
- Transport properties (viscosity, thermal conductivity)
- Graphical interface or web service
- Integration with thermodynamic databases beyond embedded reference data
- Real-time data updates to reference tables
