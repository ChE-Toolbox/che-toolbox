# Feature Specification: Heat Exchanger Calculations

**Feature Branch**: `002-heat-exchanger-calc`
**Created**: 2025-12-30
**Status**: Draft
**Input**: User description: "Heat exchanger calculations with LMTD method, NTU-effectiveness method, convection correlations, and insulation sizing"

## Clarifications

### Session 2025-12-30

- Q: User Interaction Model → A: Provide both Python library API and CLI wrapper for flexibility (scripting + command-line access)
- Q: Data Format & Input Specification → A: Use Pydantic data models for library API with JSON/YAML support for CLI/batch operations
- Q: Properties Module Dependency → A: Heat module depends on existing properties abstraction from 001-data-foundations; no direct CoolProp coupling
- Q: Validation Test Data Source & Format → A: Store reference test cases in JSON/CSV files within repo with source citations (Incropera, NIST IDs)
- Q: Output Data Structure → A: All calculation functions return comprehensive Pydantic results objects (primary value + intermediates + method/source info)

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

### User Story 1 - Calculate Heat Transfer using LMTD Method (Priority: P1)

Engineers need to size heat exchangers using the Log Mean Temperature Difference (LMTD) method, which is fundamental for counterflow, parallel flow, and crossflow configurations with correction factors for complex geometries.

**Why this priority**: LMTD is the foundational method for heat exchanger design across all industries. Most engineering projects require this calculation as the baseline approach.

**Independent Test**: Can be fully tested by calculating heat transfer rates for standard configurations (counterflow, parallel, crossflow) against published reference values from Incropera textbooks and validating correction factors.

**Acceptance Scenarios**:

1. **Given** fluid inlet/outlet temperatures and flow rate, **When** LMTD is calculated for counterflow, **Then** result matches Incropera reference values within 1%
2. **Given** parallel flow configuration parameters, **When** correction factor is applied, **Then** effective LMTD is computed correctly
3. **Given** crossflow configuration, **When** LMTD correction factor is applied, **Then** result accounts for temperature cross-effects
4. **Given** edge case of very small temperature differences, **When** LMTD is calculated, **Then** numerical stability is maintained

---

### User Story 2 - Calculate Effectiveness and NTU for Multiple Configurations (Priority: P1)

Engineers need alternative heat exchanger analysis using the Number of Transfer Units (NTU) method, which is more convenient when outlet temperatures are unknown, supporting parallel flow, counterflow, shell-and-tube, and cross-flow configurations.

**Why this priority**: NTU-effectiveness is equally critical as LMTD for practical design; required when outlet temperatures must be determined rather than given.

**Independent Test**: Can be fully tested by calculating effectiveness for standard configurations and validating against published NTU correlations and effectiveness charts.

**Acceptance Scenarios**:

1. **Given** inlet temperatures, UA product, and mass flow rates, **When** effectiveness is calculated, **Then** outlet temperature is determined correctly
2. **Given** counterflow configuration, **When** NTU is calculated, **Then** effectiveness matches standard correlations
3. **Given** shell-and-tube or cross-flow arrangement, **When** appropriate correction is applied, **Then** effectiveness accounts for configuration type
4. **Given** high NTU values, **When** effectiveness is calculated, **Then** result approaches theoretical maximum

---

### User Story 3 - Calculate Convection Heat Transfer Coefficients (Priority: P2)

Engineers need to estimate convection coefficients for various geometries and flow regimes (flat plates, cylinders, pipes, natural convection) to complement LMTD and NTU calculations with realistic film coefficients.

**Why this priority**: Convection correlations provide the critical link between fluid properties and heat transfer rates; essential for complete system design when combined with LMTD/NTU methods.

**Independent Test**: Can be fully tested by calculating coefficients for known configurations and comparing against published correlations (Dittus-Boelert for pipes, natural convection for vertical plates, cylinder in crossflow).

**Acceptance Scenarios**:

1. **Given** laminar flow over flat plate with known fluid properties, **When** Nusselt number is calculated, **Then** h coefficient is determined from correlation
2. **Given** turbulent pipe flow parameters, **When** Dittus-Boelert correlation is applied, **Then** h matches experimental validation data
3. **Given** cylinder in crossflow, **When** Reynolds number is calculated, **Then** appropriate correlation is selected and h is computed
4. **Given** vertical plate with natural convection, **When** Grashof and Rayleigh numbers are calculated, **Then** h is determined from natural convection correlation

---

### User Story 4 - Design Insulation for Cylindrical Pipes (Priority: P2)

Engineers need to calculate economic insulation thickness for cylindrical pipes, accounting for heat loss reduction and cost trade-offs, plus validation against industrial standards.

**Why this priority**: Insulation design is critical for operating cost optimization; often required by energy efficiency regulations and for equipment protection.

**Independent Test**: Can be fully tested by calculating optimal insulation thickness for standard pipe sizes and comparing economics against industrial guidelines.

**Acceptance Scenarios**:

1. **Given** pipe diameter, temperature difference, and thermal conductivity, **When** heat loss is calculated for uninsulated pipe, **Then** baseline loss is determined
2. **Given** insulation material properties and cost, **When** economic thickness is calculated, **Then** payback period is optimized
3. **Given** insulation thickness, **When** heat loss is recalculated, **Then** reduction is quantified
4. **Given** environmental or safety temperature limits, **When** insulation thickness is constrained, **Then** minimum required thickness meets specification

---

### Edge Cases

- What happens when inlet and outlet temperatures are very close (approaching zero LMTD)?
- How does the system handle retrograde flow or reversed temperature conditions?
- What occurs when NTU approaches zero or infinity in effectiveness calculations?
- How are numerical stability issues managed in natural convection with low Rayleigh numbers?
- What happens when insulation thickness exceeds practical limits?

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

**Interface & Integration:**

- **FR-001**: System MUST provide a Python library API with functions for each calculation method (LMTD, NTU, convection, insulation)
- **FR-002**: System MUST provide a CLI wrapper around the library for command-line access and scripting
- **FR-003**: System MUST accept input via Pydantic data models (library API) and JSON/YAML files (CLI/batch mode)
- **FR-004**: System MUST validate all inputs (unit compatibility, range checks) via Pydantic models before calculation
- **FR-005**: All calculation functions MUST return comprehensive Pydantic results objects containing: primary result value, all intermediate calculated values, calculation method/correlation used, source references, and confidence/accuracy bounds
- **FR-006**: System MUST depend on the properties abstraction module (from 001-data-foundations) for fluid property access; no direct CoolProp coupling in heat calculations

**Calculation Methods:**

- **FR-007**: System MUST calculate LMTD for counterflow, parallel flow, and crossflow configurations
- **FR-008**: System MUST apply correction factors (F_correction) for non-ideal heat exchanger geometries
- **FR-009**: System MUST calculate NTU and effectiveness for multiple configurations (parallel, counterflow, shell-and-tube, crossflow)
- **FR-010**: System MUST determine outlet temperatures when inlet conditions and UA are provided
- **FR-011**: System MUST calculate Nusselt number and convection coefficient for flat plate laminar flow
- **FR-012**: System MUST calculate Nusselt number and convection coefficient for flat plate turbulent flow
- **FR-013**: System MUST apply Dittus-Boelert correlation for turbulent pipe flow with h calculation
- **FR-014**: System MUST calculate convection coefficient for cylinder in crossflow using appropriate Reynolds correlation
- **FR-015**: System MUST calculate natural convection coefficient for vertical plates using Grashof/Rayleigh numbers
- **FR-016**: System MUST calculate cylindrical insulation heat loss with and without insulation
- **FR-017**: System MUST determine economic insulation thickness minimizing total cost (energy + material)
- **FR-018**: System MUST validate all calculations against published reference data (Incropera, NIST, industrial standards)
- **FR-019**: System MUST handle edge cases (near-zero temperature differences, retrograde flow, extreme NTU values) gracefully
- **FR-020**: System MUST provide unit conversion and validation for all inputs and outputs via Pint integration

### Key Entities *(include if feature involves data)*

- **Heat Exchanger Configuration**: Type (counterflow, parallel, shell-and-tube, crossflow), dimensions, material properties
- **Fluid Properties**: Temperature-dependent (density, specific heat, viscosity, thermal conductivity), phase (liquid/vapor)
- **Heat Transfer Parameters**: LMTD, NTU, effectiveness, UA product, convection coefficients (h)
- **Insulation Design**: Material properties, thickness, economic optimization parameters (energy cost, material cost)
- **Validation Reference**: Published correlations (Dittus-Boelert, natural convection), experimental data sources, manufacturer specifications

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: All LMTD calculations match Incropera reference values within 1% for standard test cases
- **SC-002**: NTU-effectiveness method produces outlet temperatures within 2% of LMTD method when both are applicable
- **SC-003**: Convection coefficients match published correlations within 5% for laminar and turbulent flows
- **SC-004**: Economic insulation thickness calculation reduces payback period analysis error to less than 10% vs. industry calculations
- **SC-005**: System successfully validates against at least 10 published reference test cases stored in JSON files with documented sources (Incropera page/table numbers, NIST database identifiers)
- **SC-006**: Edge cases (LMTD → 0, NTU → ∞, retrograde flow) are handled without numerical overflow/underflow
- **SC-007**: All calculations complete within 100ms for typical problem sizes (engineering design iterations)
- **SC-008**: Users can verify results by comparing against standard engineering references for heat exchanger design
- **SC-009**: Library API functions return Pydantic results objects with complete traceability (intermediate values, calculation method, source reference)

## Assumptions

- Fluid properties are obtained via the properties abstraction module (001-data-foundations); heat module does not directly couple to CoolProp or other property sources
- Users can provide either constant fluid properties or reference fluid names for dynamic property lookup via the properties module
- Heat exchangers operate in steady-state conditions
- No phase change occurs in the bulk fluids (saturated vapor/liquid edge cases excluded)
- Correction factors for heat exchanger geometry are based on published F-correction charts
- Natural convection calculations assume vertical flat plate geometry (most common case)
- Insulation economic analysis assumes constant energy cost over analysis period
- Validation reference test cases are stored in JSON/CSV files within the repository with full source citations (Incropera textbook identifiers, NIST database IDs); no runtime external data dependency
- All calculations use Pydantic for input validation and results serialization with Pint for unit handling

## Deliverable

4 heat transfer calculation modules: (1) LMTD Method with configurations and correction factors, (2) NTU-Effectiveness Method with multiple arrangements, (3) Convection Correlations for common geometries, (4) Insulation Sizing with economic optimization
