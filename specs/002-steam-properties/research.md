# Research: IAPWS-IF97 Steam Properties Implementation

**Feature**: 002-steam-properties | **Date**: 2025-12-30 | **Status**: Research Phase

All research items from plan.md are documented below with findings and implementation decisions.

---

## R1: IAPWS-IF97 Standard Implementation Details

**Decision**: Use official IAPWS-IF97 polynomial equations and region boundaries as defined in the standard.

**Rationale**: IAPWS-IF97 is the international standard for thermodynamic properties of water and steam. It provides:
- Explicit polynomial approximations (not iterative definitions) for fast computation
- Well-documented region boundaries and transition criteria
- Validated against extensive experimental data
- Public domain equations available from IAPWS (free to implement)

**Alternatives considered**:
- IAPWS-95 (more accurate but slower, requires iteration; deferred to future)
- CoolProp library (proprietary MIT license; considered but library-first approach requires implementing core equations)

**Implementation approach**:
- **Region 1** (6.8 MPa ≤ P ≤ 863.91 MPa, 273.15 K ≤ T ≤ 863.15 K): Explicit equations γ(π,τ) in Helmholtz free energy form
- **Region 2** (0 ≤ P ≤ 100 MPa, 273.15 K ≤ T ≤ 863.15 K): Explicit ideal gas + residual terms
- **Region 3** (16.6 MPa ≤ P ≤ 100 MPa, 623.15 K ≤ T ≤ 863.15 K): Cubic equation of state ρ(P,T)
- **Saturation line**: Use Wagner-Pruss saturation temperature equation; iterate P→T via Newton-Raphson for T_sat(P)

**Source material**:
- IAPWS-IF97 Release on the Functional Specifications and Critical Equations of State for Common Water Substance (official document)
- Supplementary Release on the Demands on an Accurate Thermodynamic Database for Thermodynamic Properties of Water and Steam (reference tables for validation)
- All coefficients and boundaries from official IAPWS technical documents (public domain)

**Status**: ✅ Ready to implement

---

## R2: Numerical Stability & Singularities Near Critical Point

**Decision**: Detect singularity approach and raise RuntimeError with diagnostic guidance before computation becomes unreliable.

**Rationale**:
- At critical point (22.064 MPa, 373.946 K), thermodynamic derivatives diverge and equations become singular
- Silent numerical errors would invalidate scientific calculations
- Explicit fail allows users to either avoid critical region or use alternative approaches
- Matches engineering practice: fail explicitly rather than return garbage results

**Singularity detection strategy**:
- **Distance metric**: Euclidean distance in normalized (P, T) space from critical point
  - P_normalized = (P - P_critical) / P_critical
  - T_normalized = (T - T_critical) / T_critical
  - Distance = sqrt(ΔP_norm² + ΔT_norm²)
- **Threshold**: Raise RuntimeError if Distance < 0.05 (5% from critical point)
  - Rationale: Region 3 equations become unreliable within ~1-2% of critical point
  - 5% threshold provides safety margin while allowing valid Region 3 calculations

**Diagnostic message format**:
```
RuntimeError: "Conditions too close to critical point (22.064 MPa, 373.946 K) for reliable computation. Distance: 3.2%. Suggestion: Move at least 5% away (e.g., P > 22.6 MPa or T > 382 K)."
```

**Alternatives considered**:
- Graceful degradation (return results with "accuracy uncertain" flag) - rejected because uncertainty margin is too large
- Return NaN/infinity - rejected because silent propagation of invalid values is dangerous
- Apply regularization/smoothing near critical point - rejected because it introduces bias and false precision

**Status**: ✅ Ready to implement

---

## R3: IAPWS Reference Data & Validation Tables

**Decision**: Embed official IAPWS supplementary table values as JSON fixtures; organize by region with property type categorization.

**Rationale**:
- Ensures tests always validate against authoritative source
- JSON format is language-agnostic and human-readable
- Reduces test suite dependency on external services (offline validation)
- Enables incremental test development (add test points as more regions complete)

**Data organization**:
```json
{
  "regions": {
    "region1": [
      {
        "point_id": "R1_001",
        "pressure_Pa": 3000000,
        "temperature_K": 300,
        "enthalpy_kJ_per_kg": 115.331273,
        "entropy_kJ_per_kg_K": 0.393062326,
        "density_kg_per_m3": 80.5,
        "source": "IAPWS Table 5"
      },
      ...
    ],
    "region2": [...],
    "region3": [...],
    "saturation": [...]
  }
}
```

**Test point counts** (minimum from spec):
- Region 1: 400 points (covers pressure/temperature grid)
- Region 2: 400 points (includes low-pressure steam region)
- Region 3: 200 points (supercritical region)
- Saturation: 300 points (liquid, vapor, and saturation temperatures)
- **Total**: 1300+ validation points

**Data sources**:
- Official IAPWS-IF97 Supplementary Release (Tables 1-14)
- NIST WebBook (cross-validation)
- Published engineering thermodynamics textbooks (Perry's, GPSA) for spot checks

**Status**: ✅ Ready to implement (external data collection)

---

## R4: Pint Integration for Unit Handling

**Decision**: Use Pint Quantity objects for all return values; initialize UnitRegistry as module-level singleton.

**Rationale**:
- Pint Quantity embeds unit metadata preventing unit conversion errors
- Singleton UnitRegistry ensures consistent unit definitions across library
- Standard SI units (Pa, K, kJ/kg) are Pint built-ins; no custom definitions needed
- Users can call `.magnitude` to extract raw float if needed

**Implementation pattern**:
```python
# src/iapws_if97/__init__.py
from pint import UnitRegistry

_ureg = UnitRegistry()
ureg = _ureg  # Export for users who need to create compatible quantities

# In steam_table.py
def h_pt(self, pressure: Quantity, temperature: Quantity) -> Quantity:
    p_pa = pressure.to('Pa').magnitude  # Convert input to Pa internally
    t_k = temperature.to('K').magnitude

    # ... computation ...
    h_result = computed_value * ureg.kJ / ureg.kg
    return h_result
```

**Unit definitions**:
- Pressure: Pa (pascals) internal; MPa, bar, atm handled by Pint
- Temperature: K (kelvin) internal; °C handled by Pint offset
- Energy: kJ/kg internal (kilojules per kilogram)
- Entropy: kJ/(kg·K) internal
- Density: kg/m³ internal

**Unit conversion strategy**:
- Accept any Pint-compatible unit on input (user can provide MPa, the library converts to Pa)
- Always return SI units (Pa, K, kJ/kg) with Quantity wrapper
- Document in API that units are fixed on output (return always in SI)

**Alternatives considered**:
- Return raw floats with documented units - rejected because silent unit errors are common
- Use typed Decimals for precision - rejected because Pint is standard in scientific Python

**Status**: ✅ Ready to implement

---

## R5: Exception Hierarchy & Message Formatting

**Decision**: Use standard Python exceptions (ValueError, RuntimeError); define exception subclasses for domain-specific errors; all messages follow structured format.

**Rationale**:
- Standard exceptions integrate naturally with Python error handling and testing frameworks
- Structured message format provides actionable guidance to users
- Custom subclasses enable precise error recovery (try/except for specific error types)

**Exception definitions**:
```python
# src/iapws_if97/exceptions.py

class SteamTableError(Exception):
    """Base exception for all IAPWS-IF97 calculations."""
    pass

class InputRangeError(ValueError, SteamTableError):
    """Raised when input pressure or temperature out of valid range."""
    pass

class NumericalInstabilityError(RuntimeError, SteamTableError):
    """Raised when calculation region is too close to singularity or convergence fails."""
    pass
```

**Message format specification**:
```
Format: "[ErrorType]: [Description of violation]. [Valid range or suggestion]"

Examples:
  InputRangeError: "Pressure out of range. Valid: 0.611657 MPa ≤ P ≤ 863.91 MPa. Got: 0.001 MPa"
  NumericalInstabilityError: "Region 3 singularity near critical point. Distance: 2.1%. Suggestion: P ≥ 22.6 MPa or T ≥ 382 K"
  RuntimeError: "Saturation iteration failed to converge after 100 iterations. Last error: 0.00012 K. Suggestion: Try different input pressure."
```

**Testing strategy**:
- Test each exception type is raised in correct condition (assertRaises in pytest)
- Validate message contains key information (assertIn for parameter names, ranges)
- Integration tests verify exception propagation through public API

**Alternatives considered**:
- Silent fallback with return of NaN - rejected because invalid results propagate silently
- Custom exception with status code (HTTP-style) - rejected as over-engineering for library

**Status**: ✅ Ready to implement

---

## R6: SciPy Root-Finding for Saturation Properties

**Decision**: Use scipy.optimize.brentq for saturation property calculations; bracket search before calling root-finder.

**Rationale**:
- Brent's method is robust, handles bracketing, and doesn't require derivative (saturation derivatives are complex)
- SciPy is already a required dependency (Constitution IV)
- No need for custom Newton-Raphson when Brent is proven and fast

**Implementation approach**:

For **T_sat(P)**: Given pressure, find saturation temperature
```python
def T_sat(self, pressure: Quantity) -> Quantity:
    p_pa = pressure.to('Pa').magnitude

    # Validate input pressure is in saturation range
    if not (611.657 <= p_pa <= 22.064e6):
        raise InputRangeError(...)

    # Define saturation equation (function to find root of)
    def saturation_eq(T):
        # Wagner-Pruss saturation pressure at temperature T
        p_sat_calc = calc_saturation_pressure(T)
        return p_sat_calc - p_pa

    # Bracket search: saturation temperature range
    T_lower = 273.16  # Triple point
    T_upper = 647.096  # Critical point

    # Use scipy.optimize.brentq
    T_sat_result = scipy.optimize.brentq(saturation_eq, T_lower, T_upper, xtol=1e-6)
    return T_sat_result * ureg.K
```

For **P_sat(T)**: Given temperature, find saturation pressure
- Direct evaluation via Wagner-Pruss equation (doesn't require root-finding, only polynomial)

**Convergence criteria**:
- Absolute tolerance: xtol=1e-6 K for temperature
- Pressure tolerance: xtol=1e-3 Pa derived from temperature tolerance
- Max iterations: brentq default (typically 100) sufficient

**Error handling**:
- Check bracketing interval contains a root before calling brentq
- If brentq raises ValueError (no sign change in bracket), return diagnostic RuntimeError

**Alternatives considered**:
- Newton-Raphson with manual derivative - rejected because saturation derivatives are complex
- Tabular lookup with interpolation - rejected because explicit root-finding is more accurate
- CoolProp saturation functions - rejected because library-first requires own implementation

**Status**: ✅ Ready to implement

---

## R7: Performance Baseline & Profiling Strategy

**Decision**: Establish baseline (<10ms per call) through benchmark suite; profile Region 3 as likely hotspot; optimize if needed.

**Rationale**:
- 10ms target is specified in spec (SC-007); need baseline to verify achievement
- Region 3 cubic solve is most expensive operation; profile before premature optimization
- NumPy polynomial evaluation is fast; focus on iteration count (saturation, convergence)

**Profiling approach**:
```python
# tests/benchmark/test_performance.py
import timeit

def benchmark_property_lookup():
    steam = SteamTable()

    # Region 1 (typical case)
    t1 = timeit.timeit(
        lambda: steam.h_pt(10 * ureg.MPa, 500 * ureg.K),
        number=1000
    )
    avg_region1 = t1 / 1000

    # Region 3 (expensive case)
    t3 = timeit.timeit(
        lambda: steam.h_pt(30 * ureg.MPa, 700 * ureg.K),
        number=1000
    )
    avg_region3 = t3 / 1000

    # Saturation (iteration required)
    tsat = timeit.timeit(
        lambda: steam.T_sat(1 * ureg.MPa),
        number=1000
    )
    avg_saturation = tsat / 1000

    print(f"Region 1: {avg_region1*1000:.3f} ms")  # Should be <2 ms
    print(f"Region 3: {avg_region3*1000:.3f} ms")  # Should be <10 ms
    print(f"Saturation: {avg_saturation*1000:.3f} ms")  # Should be <5 ms
```

**Target performance** (measured on standard CPU):
- Region 1 property lookup: <2 ms (polynomial only)
- Region 2 property lookup: <3 ms (polynomial)
- Region 3 property lookup: <10 ms (cubic solve required)
- Saturation T/P lookup: <5 ms (1-2 iterations of root-finder)
- Overall goal: 100+ property calculations per second

**Optimization strategy** (if baseline not met):
1. Profile with cProfile to identify hotspots
2. Vectorize with NumPy if multiple calculations bundled
3. Cache polynomial coefficients (minimal memory overhead)
4. Consider Numba JIT compilation for tight loops (if profiling shows polynomial eval is bottleneck)

**Alternatives considered**:
- Pre-computed lookup tables - rejected because occupies memory; interpolation introduces error
- C extension for region equations - rejected as library-first requires pure Python initially

**Status**: ✅ Ready to implement

---

## Research Summary

| Research Item | Status | Deliverable | Notes |
|---------------|--------|-------------|-------|
| R1: IAPWS Standard | ✅ | Region definitions, coefficients from official source | Use IAPWS-IF97 public equations |
| R2: Singularity Detection | ✅ | Euclidean distance threshold (5% from critical point) | RuntimeError with diagnostic guidance |
| R3: Validation Tables | ✅ | JSON with 1300+ reference points organized by region | Embed as test fixtures |
| R4: Pint Integration | ✅ | Singleton UnitRegistry, Quantity return values | Standard SI units on output |
| R5: Exception Handling | ✅ | Custom exception subclasses, structured message format | InputRangeError, NumericalInstabilityError |
| R6: Root-Finding | ✅ | scipy.optimize.brentq for saturation calculations | Bracket search + Brent method |
| R7: Performance | ✅ | Benchmark suite (cProfile, timeit); baseline <10ms | Region 3 identified as optimization target |

**All research items complete. No blockers. Ready to proceed with Phase 1 design.**

---

## Outcomes for Implementation

1. **IAPWS-IF97 equations**: Collect official polynomial coefficients and region boundaries
2. **Reference data**: Download/format IAPWS supplementary tables as JSON
3. **Pint patterns**: Define UnitRegistry initialization and return value wrapping
4. **Exception definitions**: Create custom exception classes with structured messages
5. **Root-finding strategy**: SciPy brentq with bracketing for saturation calculations
6. **Performance baseline**: Benchmark suite to verify <10ms target
7. **Code structure**: Organize regions into separate modules (region1.py, region2.py, region3.py, saturation.py)

All deliverables feed directly into implementation tasks.
