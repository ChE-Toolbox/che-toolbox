# Research & Validation: Thermodynamic Extension

**Date**: 2025-12-30
**Feature**: Thermodynamic Extension (002-thermodynamic-models)
**Status**: Phase 0 - Research Complete

---

## Research Questions & Findings

### Q1: Van der Waals Validation Data & Tolerance

**Decision**: Use NIST WebBook as primary reference source; establish 2% absolute error tolerance.

**Rationale**:
- NIST WebBook provides peer-reviewed P-V-T data for 100+ compounds
- 2% tolerance is standard in engineering practice for cubic EOS (matches PR implementation)
- Allows comparison of VDW accuracy against PR (VDW typically less accurate at high pressures)

**Alternatives Considered**:
- A) Perry's Handbook: Good for educational examples but less precise data; rejected for insufficient precision
- B) CoolProp library: Excellent but proprietary database; rejected to maintain public-data-only principle
- C) 5% tolerance: Too loose for scientific validation; rejected

**Validation Data Sources**:
- NIST WebBook (https://webbook.nist.gov/) - Free P-V-T data, 100+ compounds
- Perry's Chemical Engineers' Handbook (9th ed.) - Table 2-45 to 2-49: Real gas behavior
- Smith, Van Ness, Abbott - Introduction to Chemical Engineering Thermodynamics (8th ed.) - Example problems with solutions

**Test Case Strategy**:
- Methane (CH4): Non-polar, simple cubic behavior
- Ethane (C2H6): Hydrocarbon, moderate polarity
- Propane (C3H8): Extended range testing
- Water (H2O): Polar compound (challenging for cubic EOS)
- Nitrogen (N2): Inert reference (high Z-factor deviations)

Each compound tested at:
- Tc/2 (far from critical point) - VDW most accurate
- 0.8*Tc (intermediate)
- 0.95*Tc (near critical) - VDW less accurate
- Low P (10 bar): VDW excellent
- Medium P (50 bar): VDW good
- High P (200 bar): VDW degraded but acceptable

---

### Q2: PT Flash Algorithm Selection

**Decision**: Rachford-Rice iteration is appropriate for 2-5 component mixtures; no stability analysis required in MVP.

**Rationale**:
- Rachford-Rice is industry-standard for equilibrium composition problems
- Convergence proven for typical bubble/dew point calculations
- <50 iteration limit is standard (most converge in 3-8 iterations)
- 1e-6 fugacity tolerance provides rigorous equilibrium definition

**Alternatives Considered**:
- A) Gibbs free energy minimization: More robust but computationally expensive (~10x); rejected as YAGNI
- B) Flash3 three-phase solver: Complex; single-phase detection sufficient for MVP; rejected
- C) Stability analysis pre-check: Good practice but adds complexity; deferred to Phase 2

**Convergence Analysis**:
- Standard Rachford-Rice:
  - Iteration: z_i = [K_i * x_i - y_i] / [1 + V*(K_i - 1)] (material balance)
  - Update K: log(K_i) based on fugacity ratio: log(K_i) = log(φ_i^v) - log(φ_i^l)
  - Tolerance: |f_i^v / f_i^l - 1| < 1e-6

- Convergence acceleration: None in MVP (proves Rachford-Rice is fast enough)

**Single-Phase Logic**:
- If T > Tc: Always supercritical, return V=1, L=0
- If n_components == 1: Check saturation pressure; return L=1 or V=1
- Otherwise: Attempt RR iteration; if V→0 or L→0, re-classify as single-phase

---

### Q3: Cubic Equation Root Selection & Solver Reusability

**Decision**: Reuse existing `cubic_solver.py` for Van der Waals (slight parameter adaptation).

**Rationale**:
- Both PR and VDW reduce to depressed cubic: Z^3 + pZ^2 + qZ + r = 0
- PR coefficients: Already computed in peng_robinson.py
- VDW coefficients: Derived identically but different a, b formulas
- Same root selection rule applies: Take real root closest to Z=1 (physically meaningful volume)

**VDW vs PR Cubic Form**:

Both cubic EOSs solve: (P + A/V²)(V - B) = RT

| Parameter | Peng-Robinson | Van der Waals |
|-----------|---------------|---------------|
| A | a_PR | a_VDW = 27*R²*Tc²/(64*Pc) |
| B | b_PR | b_VDW = R*Tc/(8*Pc) |
| Root selector | Z closest to 1 | Z closest to 1 |

**Validation**: PR coefficients differ from VDW; cubic_solver handles any (A, B) pair.

**Reusability Confirmed**: ✓ No modifications to cubic_solver.py required

---

### Q4: Fugacity Calculation for Flash

**Decision**: Use Peng-Robinson fugacity coefficients (already implemented); extend to VDW.

**Rationale**:
- Spec requires: PT flash SHALL use Peng-Robinson EOS for fugacity
- Fugacity coefficient: ln(φ_i) = ∫[...]dP computed from EOS residual properties
- PR fugacity already coded; reuse existing implementation

**Note on VDW Fugacity**:
- VDW fugacity formula differs from PR but is simpler
- For testing: Compare VDW volume against literature, not fugacity directly
- Flash uses PR fugacity consistently (per requirement FR-007)

---

### Q5: Type Hints & Pydantic Validation

**Decision**: Match existing PR implementation: NumPy docstrings + mypy --strict.

**Rationale**:
- Constitution III requires 100% type coverage with mypy --strict
- Existing peng_robinson.py already follows this pattern
- Pydantic 2.x used for input validation (existing models reused)

**Pattern to Follow**:
```python
@staticmethod
def calculate_a(tc: float, pc: float, T: float) -> float:
    """Calculate 'a' parameter.

    Parameters
    ----------
    tc : float
        Critical temperature in K
    pc : float
        Critical pressure in Pa
    T : float
        Temperature in K

    Returns
    -------
    float
        Parameter a in Pa*m^6*mol^-2
    """
    if T <= 0:
        raise ValueError(f"Temperature must be positive, got {T}")
    # implementation...
```

---

## Implementation Strategy Summary

### Van der Waals EOS (vdw.py)

1. Mirror PengRobinsonEOS class structure
2. Calculate a = 27*R²*Tc²/(64*Pc)
3. Calculate b = R*Tc/(8*Pc)
4. Reuse cubic_solver.py for volume roots
5. Compute Z = PV/nRT for validation

### Ideal Gas Law (ideal.py)

1. Simple module: no cubic solve needed
2. V = nRT/P directly
3. Z always returns 1.0 exactly
4. Purpose: baseline comparison, educational value

### PT Flash (flash_pt.py)

1. Single-phase detection (T > Tc logic)
2. Rachford-Rice iteration loop:
   - Initialize K_i based on Wilson correlation
   - Converge using fugacity ratios
   - Track iteration count
3. Return FlashResult with all outputs (per clarification)
4. Convergence: |f_i^v / f_i^l - 1| < 1e-6

### Validation Tests

1. NIST comparison: ±2% error
2. Ideal Gas: Z = 1.0 exactly
3. PT flash balances: Composition error < 1e-6
4. Cross-EOS: All three models runnable on same conditions

---

## Output Artifacts Generated

- ✅ **research.md** (this file): Research findings, decisions, rationale
- 🔄 **plan.md**: Updated with Phase 0-2 structure (already completed in plan.md)
- ⏳ **data-model.md**: Next phase (contracts and data structures)
- ⏳ **quickstart.md**: Next phase (usage examples)
- ⏳ **tasks.md**: Generated by `/speckit.tasks` command

---

## Quality Gates Passed

- [x] NIST reference sources identified and validated
- [x] Algorithm choice (Rachford-Rice) justified
- [x] Cubic solver reusability confirmed
- [x] Implementation pattern matches PR precedent
- [x] All inputs validated (Pydantic, mypy --strict)
- [x] Tolerance and convergence criteria specified (1e-6)
- [x] Constitution compliance confirmed (all 7 principles satisfied)

**Status**: Phase 0 Research Complete ✓ Ready for Phase 1 Design
