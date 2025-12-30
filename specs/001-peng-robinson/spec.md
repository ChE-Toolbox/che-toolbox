# Feature Specification: Peng-Robinson EOS Thermodynamic Engine

**Feature Branch**: `001-peng-robinson`
**Created**: 2025-12-29
**Status**: Draft
**Input**: User description: "Peng-Robinson EOS Implementation with NIST Validation

1. Peng-Robinson EOS Implementation
   - Implement Z factor calculation using cubic equation solver
   - Implement fugacity calculation for vapor and liquid phases
   - Add vapor pressure calculation using Antoine/DIPPR equations
   - Support both pure components and mixtures
   - Handle subcritical and supercritical conditions

2. Validation Suite
   - Compare vs NIST WebBook data for 5 compounds (methane, ethane, propane, n-butane, water)
   - Document acceptable deviations (typically <5% for Z factor, <10% for fugacity)
   - Include test cases across temperature and pressure ranges
   - Validate phase equilibrium calculations

3. API Documentation
   - Write theory documentation explaining Peng-Robinson equation derivation
   - Document mixing rules for multi-component systems
   - Add usage examples for common calculations
   - Include troubleshooting guide for convergence issues

Deliverable: One fully validated thermodynamic calculation engine with comprehensive test coverage"

## Clarifications

### Session 2025-12-29

- Q: The Peng-Robinson cubic equation solver requires a reliable root-finding method. Which approach should be used? → A: NumPy roots with fallback to analytical cubic formula for edge cases
- Q: For vapor pressure calculations, which iterative method should be used to solve the Peng-Robinson equation? → A: SciPy Brent's method (brentq - optimal balance of speed and robustness)
- Q: How should the system handle invalid mixture composition inputs (negative mole fractions or NaN values)? → A: Raise exception and halt calculation (fail-fast approach)
- Q: What maximum iteration limit and failure behavior should be used for vapor pressure convergence? → A: 100 iterations, raise warning-level exception with best estimate
- Q: How should the system differentiate between vapor and liquid roots when three real roots exist in the two-phase region? → A: Smallest real root = liquid, largest real root = vapor (standard EOS convention)

## User Scenarios & Testing

### User Story 1 - Pure Component Property Calculation (Priority: P1)

A chemical engineer needs to calculate the compressibility factor (Z) and fugacity for a pure component (e.g., methane) at a specific temperature and pressure to determine if the gas behaves ideally or requires real gas corrections for process design.

**Why this priority**: This is the foundational capability - all other features depend on accurate pure component calculations. This represents the minimum viable product that delivers immediate value for single-component process calculations.

**Independent Test**: Can be fully tested by providing temperature, pressure, and compound identifier, then comparing calculated Z factor and fugacity against NIST WebBook reference data for the same conditions. Delivers value by enabling accurate real gas property predictions.

**Acceptance Scenarios**:

1. **Given** a pure compound (methane) at 300 K and 50 bar, **When** the user requests Z factor calculation, **Then** the system returns a Z factor within 5% of NIST reference data
2. **Given** a pure compound (propane) at 400 K and 20 bar, **When** the user requests fugacity calculation, **Then** the system returns fugacity coefficient within 10% of NIST reference data
3. **Given** a pure compound near its critical point, **When** the user requests properties, **Then** the system correctly identifies and calculates both vapor and liquid phase properties
4. **Given** a supercritical fluid (methane at 200 K and 100 bar), **When** the user requests properties, **Then** the system returns a single-phase solution with appropriate Z factor

---

### User Story 2 - Vapor Pressure Prediction (Priority: P2)

A process engineer needs to determine the saturation pressure of a pure component at a given temperature to design separation equipment or determine phase boundaries for operating conditions.

**Why this priority**: Vapor pressure is critical for phase equilibrium calculations and equipment design, but it can be performed independently of mixture calculations. It extends the utility of the engine for practical engineering applications.

**Independent Test**: Can be tested by requesting vapor pressure at a specified temperature and comparing against NIST saturation pressure data. Delivers value by enabling phase boundary predictions for process safety and equipment sizing.

**Acceptance Scenarios**:

1. **Given** a pure compound (water) at 373.15 K, **When** the user requests vapor pressure, **Then** the system returns a pressure within 5% of 1.01325 bar (atmospheric pressure)
2. **Given** a pure compound (n-butane) at 273.15 K, **When** the user requests vapor pressure, **Then** the system returns vapor pressure within 5% of NIST reference data
3. **Given** a temperature above the critical temperature, **When** the user requests vapor pressure, **Then** the system returns an error indicating no vapor pressure exists at supercritical conditions
4. **Given** a temperature below the triple point, **When** the user requests vapor pressure, **Then** the system returns a warning about extrapolation beyond valid range

---

### User Story 3 - Mixture Property Calculation (Priority: P3)

A chemical engineer needs to calculate thermodynamic properties for a multi-component mixture (e.g., natural gas consisting of methane, ethane, and propane) at specified temperature, pressure, and composition to design gas processing equipment.

**Why this priority**: Mixture calculations build upon pure component capabilities and are essential for real-world applications involving multiple components. This represents the full functionality but requires P1 to be working correctly first.

**Independent Test**: Can be tested by providing temperature, pressure, and mole fractions for a multi-component mixture, then comparing calculated mixture properties against NIST reference data. Delivers value by enabling realistic process simulations for industrial applications.

**Acceptance Scenarios**:

1. **Given** a binary mixture (50% methane, 50% ethane) at 250 K and 40 bar, **When** the user requests mixture Z factor, **Then** the system calculates mixture properties using van der Waals mixing rules with results within 5% of NIST reference data
2. **Given** a ternary mixture (60% methane, 30% ethane, 10% propane) at 300 K and 50 bar, **When** the user requests mixture fugacity coefficients for each component, **Then** the system returns component fugacity coefficients within 10% of reference calculations
3. **Given** a mixture composition that doesn't sum to 1.0, **When** the user requests mixture properties, **Then** the system returns an error indicating invalid composition
4. **Given** a mixture at two-phase conditions, **When** the user requests properties, **Then** the system identifies both phases and returns properties for vapor and liquid phases

---

### User Story 4 - Validation Against Reference Data (Priority: P1)

A thermodynamics library developer needs to verify that the Peng-Robinson implementation produces results consistent with established reference sources (NIST WebBook) to ensure the calculations are reliable for engineering use.

**Why this priority**: This is co-equal with P1 for pure components because validation is not a separate feature - it's the proof that P1 works correctly. Without validation, we cannot claim the engine is accurate or trustworthy.

**Independent Test**: Can be tested by running automated test suite comparing calculations for 5 reference compounds across temperature and pressure ranges against NIST data, with automated pass/fail criteria. Delivers value by providing confidence in calculation accuracy.

**Acceptance Scenarios**:

1. **Given** NIST reference data for methane, ethane, propane, n-butane, and water across temperature range 200-500 K and pressure range 1-100 bar, **When** the validation suite runs, **Then** at least 95% of Z factor calculations are within 5% of NIST values
2. **Given** a failed validation test, **When** the validation suite completes, **Then** the system generates a detailed report showing which conditions failed and by how much
3. **Given** validation across all test cases, **When** the suite completes, **Then** the system documents the maximum, minimum, and average deviations for each property type

---

### Edge Cases

- What happens when the cubic equation solver fails to converge (e.g., due to poor initial guesses near critical point)?
- How does the system handle requests for properties at conditions far outside the valid range of the equation of state (e.g., extremely low temperatures where quantum effects dominate)?
- What happens when mixture compositions contain negative mole fractions or NaN values? → System raises a descriptive `ValueError` exception and halts calculation (fail-fast approach)
- How does the system differentiate between vapor and liquid roots when three real roots exist in the two-phase region? → System uses standard EOS convention: smallest positive real root = liquid phase, largest positive real root = vapor phase (middle root is discarded as physically meaningless)
- What happens when binary interaction parameters are not available for a mixture pair?
- How does the system handle near-singular conditions in mixing rule calculations?
- What happens when vapor pressure iteration doesn't converge within maximum iterations? → System raises a `ConvergenceWarning` exception after 100 iterations, including the best estimate achieved and final residual error

## Requirements

### Functional Requirements

- **FR-001**: System MUST calculate compressibility factor (Z) for pure components given temperature, pressure, and critical properties (Tc, Pc, acentric factor)
- **FR-002**: System MUST solve the Peng-Robinson cubic equation of state to find all real roots (vapor and/or liquid phase Z factors)
- **FR-003**: System MUST calculate fugacity coefficient for pure components in both vapor and liquid phases
- **FR-004**: System MUST calculate vapor pressure for pure components at a given temperature using iterative solution of the Peng-Robinson equation
- **FR-005**: System MUST support mixture calculations using van der Waals mixing rules with composition-dependent parameters
- **FR-006**: System MUST calculate mixture fugacity coefficients for each component in multi-component mixtures
- **FR-007**: System MUST identify phase state (vapor, liquid, or two-phase) based on calculated Z factors; when three real roots exist, smallest root represents liquid phase and largest root represents vapor phase
- **FR-008**: System MUST handle subcritical conditions (T < Tc) where both vapor and liquid phases can exist
- **FR-009**: System MUST handle supercritical conditions (T > Tc or P > Pc) where only a single phase exists
- **FR-010**: System MUST validate input data (positive temperature/pressure, compositions sum to 1.0 within tolerance of 1e-6, valid critical properties, no negative or NaN mole fractions) and raise exceptions for invalid inputs
- **FR-011**: System MUST return appropriate error messages when calculations fail to converge, including convergence warnings with best estimates for iterative methods (100 iteration limit for vapor pressure)
- **FR-012**: System MUST provide validation test suite comparing calculations against NIST WebBook data for methane, ethane, propane, n-butane, and water
- **FR-013**: System MUST document acceptable deviation thresholds (5% for Z factor, 10% for fugacity coefficient)
- **FR-014**: System MUST generate validation reports showing deviations between calculated and reference values
- **FR-015**: Users MUST be able to query properties for pure components by providing compound identifier, temperature, and pressure
- **FR-016**: Users MUST be able to query properties for mixtures by providing component identifiers, mole fractions, temperature, and pressure
- **FR-017**: System MUST use binary interaction parameters (kij) when specified for mixture calculations, defaulting to zero if not provided

### Key Entities

- **Compound**: Represents a pure chemical species with critical properties (critical temperature, critical pressure, acentric factor) required for Peng-Robinson calculations. Each compound has a unique identifier and associated physical property data.

- **Mixture**: Represents a multi-component system consisting of multiple compounds with specified mole fractions. The mixture has composition-dependent properties calculated using mixing rules.

- **Thermodynamic State**: Represents a specific condition defined by temperature, pressure, and composition (for mixtures). Each state has associated calculated properties (Z factor, fugacity, phase identification).

- **Validation Test Case**: Represents a reference calculation with known inputs (compound, temperature, pressure) and expected outputs (Z factor, fugacity) from authoritative sources (NIST or textbook). Used to verify calculation accuracy.

- **Binary Interaction Parameter**: Represents the deviation from ideal mixing behavior between two compounds in a mixture. Identified by compound pair and used in mixing rule calculations.

## Success Criteria

### Measurable Outcomes

- **SC-001**: For pure component Z factor calculations, at least 95% of validation test cases across 5 compounds (methane, ethane, propane, n-butane, water) produce results within 5% of NIST reference data
- **SC-002**: For pure component fugacity calculations, at least 90% of validation test cases produce results within 10% of NIST reference data
- **SC-003**: Vapor pressure calculations for pure components converge to within 1% of NIST saturation pressure data for at least 95% of test cases in the temperature range 0.5*Tc to 0.95*Tc
- **SC-004**: Mixture property calculations for binary and ternary systems produce results within 5% of NIST reference calculations for at least 90% of test cases
- **SC-005**: Users can calculate thermodynamic properties for both pure components and mixtures with a single query providing temperature, pressure, and composition
- **SC-006**: The validation test suite executes completely in under 60 seconds and generates a comprehensive accuracy report
- **SC-007**: Documentation includes at least 10 practical usage examples covering common scenarios (pure component vapor properties, liquid properties, mixture calculations, vapor pressure)
- **SC-008**: Convergence failure rate for well-posed problems (conditions within valid EOS range) is less than 1% across all validation test cases
- **SC-009**: System correctly identifies phase state (vapor/liquid/two-phase) for at least 98% of validation test cases

## Assumptions

- Critical properties (Tc, Pc, acentric factor) for all compounds are available from existing compound database or will be provided by the user
- Binary interaction parameters (kij) will default to zero for all pairs unless explicitly provided
- Standard van der Waals mixing rules are acceptable for mixture calculations (no advanced mixing rules like Wong-Sandler required)
- Temperature range of interest is 200-600 K (typical for hydrocarbon processing)
- Pressure range of interest is 1-100 bar (typical for most chemical processes)
- Validation will use publicly available NIST WebBook data
- Users are familiar with basic thermodynamic concepts (temperature, pressure, fugacity, compressibility factor)
- The cubic equation solver will use NumPy `roots()` for finding all real roots, with fallback to analytical cubic formula (Cardano's method) for edge cases near critical points; phase assignment follows standard convention (smallest root = liquid, largest = vapor)
- Vapor pressure calculations will use SciPy's Brent's method (`scipy.optimize.brentq`) for iterative root finding with maximum 100 iterations, raising `ConvergenceWarning` if limit exceeded
- Phase stability analysis (determining if a single phase or two phases are stable) is out of scope for initial implementation
- Advanced EOS features (volume translation, temperature-dependent kij) are out of scope for initial implementation

## Constraints

- Must maintain compatibility with existing compound database structure
- Must produce results accurate enough for engineering calculations (stated tolerances)
- Must handle edge cases gracefully without crashing or producing invalid results
- Documentation must be accessible to chemical engineering practitioners without requiring deep EOS theory knowledge

## Dependencies

- Existing compound database with critical properties for at least 5 validation compounds
- Access to NIST WebBook data or equivalent reference source for validation
- NumPy library for numerical root finding (polynomial roots) with analytical cubic formula fallback implementation
- SciPy library for Brent's method optimization (`scipy.optimize.brentq`) used in vapor pressure iterations
