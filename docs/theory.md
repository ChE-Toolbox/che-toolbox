# Peng-Robinson Equation of State: Theory and Implementation

## Overview

The Peng-Robinson (PR) equation of state is a cubic equation that relates pressure (P), temperature (T), and molar volume (V) for real gases and liquids. Unlike the ideal gas law (PV = RT), the PR-EOS accounts for molecular interactions and finite molecular size.

## Peng-Robinson Equation

### Fundamental Form

$$P = \frac{RT}{V_m - b} - \frac{a(T)}{V_m^2 + 2bV_m - b^2}$$

Where:
- **P**: Pressure (Pa)
- **T**: Temperature (K)
- **V_m**: Molar volume (m³/mol)
- **R**: Gas constant (8.314462618 J/(mol·K))
- **a(T)**: Temperature-dependent attraction parameter (Pa·m⁶·mol⁻²)
- **b**: Repulsion parameter (m³·mol⁻¹)

### Parameter Calculation

#### Parameter 'b'

$$b = 0.07780 \frac{RT_c}{P_c}$$

Where T_c is critical temperature and P_c is critical pressure.

**Meaning:** Represents excluded volume due to finite molecular size

#### Parameter 'a(T)'

$$a(T) = a_0 \cdot \alpha(T_r, \omega)$$

Where:
$$a_0 = 0.45724 \frac{R^2T_c^2}{P_c}$$

$$\alpha(T_r, \omega) = \left[1 + \left(0.37464 + 1.54226\omega - 0.26992\omega^2\right)(1 - \sqrt{T_r})\right]^2$$

And T_r = T/T_c (reduced temperature), ω is acentric factor

**Meaning:** Accounts for intermolecular attractions; temperature-dependent

## Compressibility Factor

The compressibility factor Z is the ratio of real to ideal gas behavior:

$$Z = \frac{PV_m}{RT}$$

- Z = 1 for ideal gas
- Z < 1 for attractive forces dominating
- Z > 1 for repulsive forces dominating

### Cubic Form

Converting the PR-EOS to a cubic polynomial in Z:

$$Z^3 - (1-B)Z^2 + (A - 3B^2 - 2B)Z - (AB - B^2 - B^3) = 0$$

Where:
$$A = \frac{aP}{R^2T^2}$$
$$B = \frac{bP}{RT}$$

### Root Selection

For a given T and P, this cubic may have:
- **3 real roots:** Two-phase region (smallest = liquid, largest = vapor)
- **1 real root:** Single-phase region

We select only positive physical roots (Z > 0).

## Fugacity and Fugacity Coefficient

### Definition

Fugacity (f) measures the effective pressure or chemical potential of a component:

$$f_i = \phi_i \cdot x_i \cdot P$$

Where:
- φᵢ is the fugacity coefficient
- xᵢ is the mole fraction
- P is pressure

### Fugacity Coefficient Calculation

For the PR-EOS:

$$\ln(\phi_i) = \frac{B_i}{B}(Z-1) - \ln(Z-B) + \frac{A}{2\sqrt{2}B} \left(\frac{2\sum_j x_j a_{ij}}{a} - \frac{B_i}{B}\right) \ln\left(\frac{Z + B(1+\sqrt{2})}{Z + B(1-\sqrt{2})}\right)$$

For pure components, this simplifies significantly.

### Phase Equilibrium

At equilibrium: $f_{liquid} = f_{vapor}$

This equality is used to find vapor pressure by solving:

$$\phi_{vapor}(T, P_{sat}) \cdot P_{sat} = \phi_{liquid}(T, P_{sat}) \cdot P_{sat}$$

## Mixing Rules

For multi-component mixtures, we use van der Waals mixing rules:

### Mixing Rule for 'a'

$$a_{mix} = \sum_i \sum_j x_i x_j a_{ij}$$

Where:
$$a_{ij} = (1 - k_{ij}) \sqrt{a_i a_j}$$

- k_{ij} is the binary interaction parameter
- k_{ij} accounts for non-ideal mixing
- Typical values: -0.05 < k_{ij} < 0.15

### Mixing Rule for 'b'

$$b_{mix} = \sum_i x_i b_i$$

Linear mixing rule (simple and effective)

## Vapor Pressure Calculation

### Definition

Vapor pressure (P_sat) is the pressure at which liquid and vapor are in equilibrium at a given temperature.

### Calculation Method

1. **Bracketing:** Find bounds where liquid and vapor fugacities change sign
   - Lower bound: ε (very small)
   - Upper bound: 0.999 × P_c

2. **Root Finding:** Use Brent's method to find P where:
   $$\phi_{vapor} = \phi_{liquid}$$

3. **Convergence:** Iterate until residual < 1e-8

## Phase Identification

The algorithm determines the thermodynamic phase based on:

1. **Critical Point Check:**
   - If T ≥ T_c: **SUPERCRITICAL**

2. **Two-Phase Region:**
   - If P_sat < P < P_c and three real roots: **TWO_PHASE**
   - Select Z_liquid = smallest root
   - Select Z_vapor = largest root

3. **Single-Phase:**
   - If only one real root: **VAPOR**
   - If only one real root and low T: **LIQUID**

## Numerical Considerations

### Cubic Solver

1. **NumPy approach:** numpy.roots() for polynomial coefficients
   - Fast and robust for most cases
   - May have issues with numerical precision edge cases

2. **Analytical fallback:** Cardano's method
   - Exact for cubic polynomials
   - Used when NumPy fails or for validation

### Vapor Pressure Convergence

- **Max iterations:** 100
- **Tolerance:** 1e-8 Pa (residual)
- **Initial bracket:** [1e-6 × P_c, 0.999 × P_c]

If convergence fails:
- Return best estimate with ConvergenceWarning
- Residual and iterations available for debugging

### Stability

The implementation is stable for:
- Temperature range: 100 K to 2000 K (typical industrial range)
- Pressure range: 1 Pa to 10⁸ Pa
- All acentric factors: -1 < ω < 2

## Validation Against NIST

The implementation is validated against NIST WebBook data for five reference compounds:

| Compound | Temperature Range | Pressure Range | Target Accuracy |
|----------|-------------------|-----------------|-----------------|
| Methane  | 90-560 K          | 0.1-200 MPa     | ±5% (Z), ±10% (φ) |
| Ethane   | 135-560 K         | 0.1-200 MPa     | ±5% (Z), ±10% (φ) |
| Propane  | 230-580 K         | 0.1-200 MPa     | ±5% (Z), ±10% (φ) |
| n-Butane | 272-600 K         | 0.1-200 MPa     | ±5% (Z), ±10% (φ) |
| Water    | 273-650 K         | 0.1-220 MPa     | ±5% (Z), ±10% (φ) |

## Advantages and Limitations

### Advantages

1. **Cubic equation:** Relatively simple for analytical and numerical treatment
2. **Two parameters:** Only a(T) and b, easy to fit to critical properties
3. **Two-phase capability:** Can handle both liquid and vapor roots
4. **Physical basis:** Derived from statistical mechanics principles
5. **Wide applicability:** Works well for hydrocarbons and non-polar fluids

### Limitations

1. **Polar fluids:** Less accurate for water and alcohols (our implementation gives acceptable accuracy)
2. **Complex mixtures:** Binary interaction parameters (k_{ij}) needed for accurate predictions
3. **Critical point accuracy:** Slightly overestimates density near critical point
4. **Associating liquids:** Not suitable for strongly hydrogen-bonded systems

## References

1. Peng, D. Y., & Robinson, D. B. (1976). "A new two-constant equation of state." *Industrial & Engineering Chemistry Fundamentals*, 15(1), 59-64.

2. Reid, R. C., Prausnitz, J. M., & Poling, B. E. (1987). *The Properties of Gases and Liquids*. McGraw-Hill.

3. Smith, J. M., Van Ness, H. C., & Abbott, M. M. (2005). *Introduction to Chemical Engineering Thermodynamics*. McGraw-Hill.

4. NIST Chemistry WebBook. https://webbook.nist.gov/chemistry/

## Mathematical Notation

- **T**: Absolute temperature (K)
- **P**: Absolute pressure (Pa)
- **V_m**: Molar volume (m³/mol)
- **T_c**: Critical temperature
- **P_c**: Critical pressure
- **ω**: Acentric factor
- **φ**: Fugacity coefficient
- **f**: Fugacity (Pa)
- **Z**: Compressibility factor
- **R**: Universal gas constant
- **k_{ij}**: Binary interaction parameter
- **x_i**: Mole fraction of component i
- **T_r = T/T_c**: Reduced temperature
- **P_r = P/P_c**: Reduced pressure

## Computational Complexity

- **Z factor calculation:** O(1) - single cubic solve
- **Fugacity coefficient:** O(1) for pure, O(n²) for mixtures with n components
- **Vapor pressure:** O(100) iterations × O(1) per iteration = O(100)
- **Validation suite (NIST):** O(250 points) × O(1) = ~0.1 seconds per compound
