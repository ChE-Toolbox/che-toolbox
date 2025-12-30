# Research: Peng-Robinson EOS Implementation

**Feature**: 001-peng-robinson
**Date**: 2025-12-29
**Status**: Complete

## Overview

This document consolidates research findings for implementing a production-grade Peng-Robinson equation of state (EOS) thermodynamic engine. All technical decisions have been evaluated against authoritative sources and best practices for numerical methods in chemical engineering calculations.

## Research Areas

### 1. Cubic Equation Solving Methods

**Context**: The Peng-Robinson EOS reduces to a cubic equation in compressibility factor (Z). A reliable root-finding method is critical for accurate property predictions.

**Decision**: NumPy `roots()` with analytical cubic formula fallback

**Rationale**:
- NumPy `roots()` uses eigenvalue decomposition of companion matrix (numerically stable for most cases)
- Analytical cubic formula (Cardano's method) provides fallback for edge cases near critical point where companion matrix may be ill-conditioned
- Combination approach balances speed (NumPy is optimized) with robustness (analytical formula handles singularities)
- Standard approach in computational thermodynamics (see Prausnitz et al., "Molecular Thermodynamics of Fluid-Phase Equilibria", 3rd ed.)

**Alternatives Considered**:
- **Newton-Raphson iteration**: Requires initial guess and can converge to wrong root in two-phase region (rejected due to robustness concerns)
- **Analytical cubic formula only**: Slower than NumPy for typical cases and more complex to implement correctly (rejected for performance)
- **SciPy `fsolve`**: Overkill for cubic equation and requires initial guess (rejected for simplicity)

**Implementation Notes**:
- NumPy `roots()` returns all roots (real and complex); filter for real positive roots only
- Analytical formula needed for validation tests near critical point (T > 0.95*Tc)
- Expected success rate: >99.5% with hybrid approach based on literature benchmarks

**References**:
- Prausnitz, J. M., Lichtenthaler, R. N., & de Azevedo, E. G. (1999). *Molecular Thermodynamics of Fluid-Phase Equilibria* (3rd ed.). Prentice Hall.
- NumPy documentation: `numpy.roots()` - Companion matrix eigenvalue method

---

### 2. Vapor Pressure Iteration Method

**Context**: Vapor pressure calculation requires iterative solution of the Peng-Robinson equation to find the pressure where fugacity of vapor equals fugacity of liquid at a given temperature.

**Decision**: SciPy Brent's method (`scipy.optimize.brentq`)

**Rationale**:
- Brent's method combines bisection, secant, and inverse quadratic interpolation for optimal balance of speed and robustness
- Guaranteed convergence if root is bracketed (vapor pressure always exists between 0 and critical pressure for subcritical temperatures)
- No derivative required (unlike Newton-Raphson), making implementation simpler
- Standard choice for root-finding in thermodynamic property calculations

**Alternatives Considered**:
- **Newton-Raphson**: Faster convergence when close to root, but requires analytical derivative of fugacity equation and can diverge with poor initial guess (rejected due to complexity and robustness)
- **Bisection only**: Guaranteed convergence but slower than Brent's method (rejected for performance)
- **SciPy `fsolve` (hybrid Newton)**: More general but overkill for 1D root-finding (rejected for simplicity)
- **Fixed-point iteration**: Can be unstable for vapor pressure calculations (rejected for robustness)

**Implementation Notes**:
- Bracket: [1e-6 * Pc, 0.999 * Pc] for subcritical temperatures (T < Tc)
- Convergence criterion: residual < 1e-6 in fugacity equality
- Maximum iterations: 100 (typical convergence in 5-15 iterations)
- Error handling: raise `ConvergenceWarning` with best estimate if max iterations exceeded

**Performance Expectations**:
- Typical convergence: 5-15 iterations for well-behaved cases
- Edge cases (near critical point): up to 50 iterations
- Success rate: >99% within 100 iterations based on NIST validation data

**References**:
- Brent, R. P. (1973). *Algorithms for Minimization without Derivatives*. Prentice-Hall.
- SciPy documentation: `scipy.optimize.brentq` - Brent's method implementation
- Reid, R. C., Prausnitz, J. M., & Poling, B. E. (1987). *The Properties of Gases and Liquids* (4th ed.). McGraw-Hill.

---

### 3. Phase Root Discrimination

**Context**: In the two-phase region (T < Tc, P < Psat), the cubic equation has three real roots. The system must correctly identify which root corresponds to vapor phase and which to liquid phase.

**Decision**: Smallest positive real root = liquid, largest positive real root = vapor

**Rationale**:
- Standard convention in equation of state theory (see Sandler, "Chemical, Biochemical, and Engineering Thermodynamics", 5th ed., Section 7.4)
- Physical interpretation: liquid has smaller molar volume (higher density) → smaller Z factor
- Middle root is mathematically valid but physically meaningless (unstable phase)
- Consistent with NIST calculation conventions

**Alternatives Considered**:
- **Gibbs energy minimization**: More rigorous but computationally expensive and unnecessary for well-behaved cubic EOS (rejected for simplicity)
- **Phase stability analysis**: Required for advanced applications (e.g., three-phase equilibrium) but out of scope for initial implementation (deferred to future version)

**Implementation Notes**:
- Filter complex roots: `root.imag == 0` and `root.real > 0`
- Sort real positive roots in ascending order
- Return: `Z_liquid = roots[0]`, `Z_vapor = roots[-1]`
- Single root case (supercritical): return single root as fluid phase

**Edge Cases**:
- Exactly two real roots (rare): use largest root (near-critical behavior)
- No positive real roots (invalid): raise `ValueError` indicating calculation failure

**References**:
- Sandler, S. I. (2017). *Chemical, Biochemical, and Engineering Thermodynamics* (5th ed.). Wiley.
- Michelsen, M. L., & Mollerup, J. M. (2007). *Thermodynamic Models: Fundamentals & Computational Aspects* (2nd ed.). Tie-Line Publications.

---

### 4. Invalid Input Handling Strategy

**Context**: The system must handle invalid inputs (negative mole fractions, NaN values, compositions not summing to 1.0) gracefully without producing incorrect results.

**Decision**: Fail-fast approach with descriptive exceptions

**Rationale**:
- Engineering calculations require correctness over fault tolerance
- Silent failures or auto-correction can mask upstream data quality issues
- Explicit exceptions force users to fix invalid inputs at the source
- Aligns with Pydantic validation philosophy (validate early, fail explicitly)

**Alternatives Considered**:
- **Auto-normalize compositions**: Sum to 1.0 by dividing by total (rejected - masks data quality issues)
- **Default to zero for invalid values**: Can produce plausible but wrong results (rejected - violates safety principle)
- **Warning-only approach**: Allows calculations to proceed with invalid data (rejected - too permissive for engineering use)

**Implementation Notes**:
- Use Pydantic validators for data validation at API boundary
- Check constraints:
  - Temperature > 0 (absolute)
  - Pressure > 0 (absolute)
  - Mole fractions ≥ 0 (physical constraint)
  - Sum of mole fractions = 1.0 ± 1e-6 (tolerance for floating-point precision)
  - Critical properties valid: Tc > 0, Pc > 0, -1 < omega < 2 (physical range)
- Raise `ValueError` with descriptive message indicating which constraint failed

**Exception Messages** (examples):
- `"Temperature must be positive, got T=-10.0 K"`
- `"Mole fractions must be non-negative, got x[2]=-0.05"`
- `"Mole fractions must sum to 1.0, got sum=1.15"`
- `"Invalid critical properties for compound 'methane': Tc must be positive"`

**References**:
- Pydantic documentation: Data validation and settings management
- Python exception handling best practices (PEP 20: "Errors should never pass silently")

---

### 5. Vapor Pressure Convergence Failure Handling

**Context**: Iterative vapor pressure calculations may fail to converge within maximum iterations for ill-conditioned problems (e.g., very close to critical point).

**Decision**: Raise warning-level exception with best estimate after 100 iterations

**Rationale**:
- Provides transparency about calculation quality (user knows result may be approximate)
- Allows users to decide whether to use best estimate or reject calculation
- Maximum iteration limit prevents infinite loops
- 100 iterations is generous (typical convergence in 5-15 iterations)

**Alternatives Considered**:
- **Silent return of best estimate**: Hides convergence issues from user (rejected - violates transparency)
- **Hard exception (ValueError)**: Too strict for cases where best estimate may be acceptable (rejected - reduces usability)
- **Retry with different initial bracket**: Adds complexity and may not improve convergence (rejected - over-engineering)

**Implementation Notes**:
- Custom exception class: `ConvergenceWarning` (inherits from `Warning`, not `Exception`)
- Include in exception message:
  - Best estimate of vapor pressure achieved
  - Final residual error in fugacity equality
  - Suggestion to check if temperature is near critical point
- Users can catch `ConvergenceWarning` specifically to handle non-convergence cases
- Log warning to standard Python logging system

**Example Exception Message**:
```
ConvergenceWarning: Vapor pressure iteration did not converge after 100 iterations.
Best estimate: P = 45.23 bar (residual = 1.2e-4)
Suggestion: Temperature T=190.0 K is close to critical temperature Tc=190.56 K. Consider using alternative method for near-critical conditions.
```

**References**:
- Python warnings module documentation
- Numerical Recipes in C (Press et al., 1992): Section 9.6 on convergence criteria

---

### 6. NIST Validation Data Sources

**Context**: Validation requires authoritative reference data for compressibility factor, fugacity, and vapor pressure across wide ranges of temperature and pressure.

**Decision**: NIST Chemistry WebBook (webbook.nist.gov) fluid properties database

**Rationale**:
- Public domain, freely accessible without licensing restrictions
- Comprehensive data for hydrocarbons and water (covers all 5 validation compounds)
- High-quality experimental data with documented uncertainty
- Standard reference in chemical engineering (widely cited in literature)
- Provides multiple properties: density, vapor pressure, enthalpy (enables cross-validation)

**Data Coverage**:
- **Methane**: 90-625 K, 0.1-1000 bar (extensive supercritical data)
- **Ethane**: 90-625 K, 0.01-900 bar
- **Propane**: 85-625 K, 0.001-800 bar
- **n-Butane**: 135-575 K, 0.0001-700 bar
- **Water**: 273-1273 K, 0.001-1000 bar (IAPWS-95 formulation)

**Alternatives Considered**:
- **DIPPR database**: Comprehensive but proprietary (requires expensive license) - rejected per Constitution Principle IV
- **CoolProp library**: Excellent Python library but uses reference EOS (Helmholtz energy), not useful for validating cubic EOS - considered for future augmentation
- **Literature textbook examples**: Limited data points, not comprehensive enough for statistical validation - useful for spot checks only

**Implementation Notes**:
- Download NIST fluid properties data as JSON (isothermal and isobaric datasets)
- Store in `data/nist_reference/` directory with compound name
- Include metadata: temperature range, pressure range, data source, uncertainty estimates
- Calculate Z factor from NIST density: Z = (P * V) / (R * T)
- Fugacity coefficient from NIST: requires integration of residual properties (use NIST-provided fugacity when available)

**Expected Deviations**:
- Z factor: <5% for 95% of test points (cubic EOS approximation vs. reference multiparameter EOS)
- Fugacity: <10% for 90% of test points (larger deviation expected due to error propagation)
- Vapor pressure: <5% for 95% of test points in range 0.5*Tc to 0.95*Tc

**References**:
- NIST Chemistry WebBook: https://webbook.nist.gov/chemistry/fluid/
- Linstrom, P. J., & Mallard, W. G. (Eds.). NIST Chemistry WebBook, NIST Standard Reference Database Number 69. National Institute of Standards and Technology.

---

### 7. Van der Waals Mixing Rules for Mixtures

**Context**: Multi-component mixtures require combining rules to calculate effective mixture parameters (a, b) from pure component properties.

**Decision**: Standard van der Waals mixing rules with binary interaction parameters (kij)

**Rationale**:
- Simplest and most widely used mixing rules for cubic equations of state
- Well-validated for hydrocarbon mixtures (acceptable accuracy for most engineering applications)
- Binary interaction parameters (kij) provide empirical correction for non-ideal mixing
- Supported by extensive literature data for common pairs

**Mixing Rules**:
```
a_mix = Σ_i Σ_j x_i x_j a_ij
b_mix = Σ_i x_i b_i

where:
a_ij = (1 - k_ij) * sqrt(a_i * a_j)  (geometric mean with correction)
k_ij = binary interaction parameter (default to 0 if not available)
```

**Alternatives Considered**:
- **Wong-Sandler mixing rules**: More accurate for highly non-ideal mixtures but requires excess Gibbs energy data (rejected - adds complexity, limited benefit for hydrocarbon systems)
- **MHV2 (Modified Huron-Vidal)**: Advanced mixing rule for polar/associating systems (rejected - out of scope for initial implementation)
- **Composition-dependent kij**: Temperature or composition dependency (rejected - insufficient data, over-engineering for v1)

**Implementation Notes**:
- Default kij = 0 for all pairs (ideal mixing assumption)
- Allow users to provide custom kij matrix for specific applications
- Store common kij values in database (e.g., methane-ethane, methane-propane from literature)
- Validate kij range: typically -0.2 < kij < 0.2 for physically meaningful values

**Expected Accuracy**:
- Hydrocarbon mixtures: ±5% for Z factor with optimized kij
- Hydrocarbon-water mixtures: ±10-15% (polar interactions less well-represented by van der Waals rules)

**References**:
- Prausnitz et al. (1999). *Molecular Thermodynamics of Fluid-Phase Equilibria*, Chapter 5.
- Walas, S. M. (1985). *Phase Equilibria in Chemical Engineering*. Butterworth-Heinemann.

---

## Implementation Dependencies

### Required Python Libraries

| Library | Version | Purpose | License |
|---------|---------|---------|---------|
| NumPy | 1.24+ | Polynomial root finding, array operations | BSD-3-Clause |
| SciPy | 1.10+ | Brent's method optimization (`brentq`) | BSD-3-Clause |
| Pint | 0.23+ | Unit handling and dimensional analysis | BSD-3-Clause |
| Pydantic | 2.x | Data validation and settings management | MIT |
| pytest | 7.x+ | Testing framework | MIT |
| mypy | 1.0+ | Static type checking | MIT |

All dependencies are open-source with permissive licenses (BSD/MIT), satisfying Constitution Principle IV.

---

## Validation Test Strategy

### Test Data Structure

```json
{
  "compound": "methane",
  "critical_properties": {
    "Tc": 190.564,  // K
    "Pc": 45.99,    // bar
    "omega": 0.011
  },
  "test_cases": [
    {
      "temperature": 200.0,  // K
      "pressure": 50.0,      // bar
      "nist_density": 160.5, // kg/m^3
      "nist_Z": 0.941,
      "nist_fugacity_coef": 0.892,
      "tolerance_Z": 0.05,
      "tolerance_fug": 0.10
    }
  ]
}
```

### Test Coverage Plan

1. **Pure Component Z Factor**: 50 test points per compound × 5 compounds = 250 tests
2. **Pure Component Fugacity**: 50 test points per compound × 5 compounds = 250 tests
3. **Vapor Pressure**: 20 test points per compound × 5 compounds = 100 tests
4. **Binary Mixtures**: 30 test points × 3 pairs = 90 tests
5. **Edge Cases**: Critical point, low pressure, high pressure = 50 tests

**Total Validation Tests**: ~740 test cases

**Acceptance Criteria**:
- Z factor: ≥95% of tests within ±5% of NIST values
- Fugacity: ≥90% of tests within ±10% of NIST values
- Vapor pressure: ≥95% of tests within ±5% of NIST values

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Cubic solver fails near critical point | Medium | High | Implement analytical fallback, validate edge cases |
| NIST data download/parsing errors | Low | Medium | Include data files in repository, validate schema |
| Vapor pressure non-convergence | Low | Medium | Use generous iteration limit (100), provide best estimate |
| Mixture kij data unavailable | High | Low | Default to kij=0, document limitation in API docs |
| Performance slower than target (<10ms) | Low | Low | NumPy/SciPy are highly optimized, profile if needed |

---

## Open Questions (Deferred to Future Work)

1. **Phase stability analysis**: How to determine if single phase or two phases are stable? (Deferred - use heuristics for v1: T > Tc → single phase)
2. **Multi-phase flash calculations**: How to solve for vapor-liquid equilibrium composition? (Deferred - out of scope for pure component focus)
3. **Temperature-dependent kij**: Should binary interaction parameters vary with temperature? (Deferred - insufficient data, use constant kij for v1)
4. **Volume translation**: Should Peneloux-type volume corrections be applied? (Deferred - adds complexity, benefit unclear for Z factor/fugacity)

---

## Conclusion

All technical decisions have been finalized with clear rationale based on authoritative sources and best practices. The implementation approach balances simplicity (NumPy/SciPy standard methods), robustness (hybrid solver with fallback, fail-fast validation), and accuracy (NIST validation with defined tolerance criteria). No blocking unknowns remain; ready to proceed to Phase 1 design.
