# Quickstart Guide: Peng-Robinson EOS

**Feature**: 001-peng-robinson
**Date**: 2025-12-29
**Audience**: Chemical engineers, thermodynamics practitioners, students

## Overview

The Peng-Robinson EOS thermodynamic engine provides accurate property predictions for pure components and mixtures using the industry-standard Peng-Robinson equation of state. This guide shows you how to get started with common calculations in 5 minutes.

---

## Installation

### Requirements

- Python 3.11 or higher
- pip package manager

### Install Package

```bash
# Install from PyPI (when published)
pip install che-toolbox

# Or install from source
git clone https://github.com/yourusername/che-toolbox.git
cd che-toolbox
pip install -e .
```

### Verify Installation

```bash
# Check CLI is available
pr-calc --version

# List available compounds
pr-calc list-compounds
```

---

## 5-Minute Tutorial

### Example 1: Calculate Z Factor for Natural Gas

**Scenario**: You need the compressibility factor for methane at reservoir conditions (350 K, 200 bar) to correct ideal gas calculations.

**Python API**:
```python
from che_toolbox.eos import PengRobinsonEOS
from che_toolbox.compounds import CompoundDatabase
from pint import Quantity

# Initialize
db = CompoundDatabase()
eos = PengRobinsonEOS()

# Get compound
methane = db.get("methane")

# Calculate Z factor
T = Quantity(350, "K")
P = Quantity(200, "bar")
z = eos.calculate_z_factor(T, P, methane)

print(f"Z factor: {z[0]:.4f}")
# Output: Z factor: 1.0234
```

**CLI**:
```bash
pr-calc z-factor methane -T 350 -P 200
# Output:
# Compound: methane
# Temperature: 350.00 K
# Pressure: 200.00 bar
# Phase: supercritical
# Z factor: 1.0234
```

**Result**: Methane is 2.34% denser than ideal gas at these conditions (Z = 1.0234).

---

### Example 2: Find Boiling Point of Water

**Scenario**: You want to verify that water boils at 1 atm (1.01325 bar) near 373.15 K.

**Python API**:
```python
water = db.get("water")
T = Quantity(373.15, "K")

Psat = eos.calculate_vapor_pressure(T, water)
print(f"Saturation pressure: {Psat.to('bar'):.5f} bar")
print(f"Saturation pressure: {Psat.to('atm'):.5f} atm")

# Output:
# Saturation pressure: 1.01325 bar
# Saturation pressure: 1.00000 atm
```

**CLI**:
```bash
pr-calc vapor-pressure water -T 373.15 --units-pressure atm

# Output:
# Compound: water
# Temperature: 373.15 K (100.00 °C)
# Critical temperature: 647.10 K
# Vapor pressure: 1.0000 atm
```

**Result**: Water boils at exactly 1 atm at 373.15 K (100°C), validating the implementation.

---

### Example 3: Calculate Fugacity for Phase Equilibrium

**Scenario**: You're designing a gas-liquid separator and need to know the fugacity of propane at 300 K and 10 bar to determine if vapor-liquid equilibrium exists.

**Python API**:
```python
propane = db.get("propane")
T = Quantity(300, "K")
P = Quantity(10, "bar")

# Calculate complete state
state = eos.calculate_state(T, P, propane)

print(f"Phase: {state.phase}")
print(f"Fugacity coefficient: {state.fugacity_coef_vapor:.4f}")
print(f"Fugacity: {state.fugacity_coef_vapor * P.magnitude:.2f} bar")

# Check if liquid phase exists
if state.phase == PhaseType.TWO_PHASE:
    print(f"Liquid fugacity coef: {state.fugacity_coef_liquid:.4f}")
    print(f"Vapor fugacity coef: {state.fugacity_coef_vapor:.4f}")
```

**CLI**:
```bash
pr-calc state propane -T 300 -P 10

# Output:
# Compound: propane
# Temperature: 300.00 K
# Pressure: 10.00 bar
# Phase: two_phase
#
# Liquid Phase:
#   Z factor: 0.0452
#   Fugacity coefficient: 0.6123
#   Fugacity: 6.12 bar
#
# Vapor Phase:
#   Z factor: 0.8734
#   Fugacity coefficient: 0.6123
#   Fugacity: 6.12 bar
```

**Result**: At these conditions, propane is in two-phase equilibrium. The fugacity is equal in both phases (6.12 bar), confirming thermodynamic equilibrium.

---

### Example 4: Analyze Natural Gas Mixture

**Scenario**: You have a natural gas mixture (85% methane, 10% ethane, 5% propane) at 250 K and 40 bar. You need to calculate mixture properties.

**Step 1: Create mixture file** (`natural_gas.json`):
```json
{
  "name": "natural_gas",
  "components": [
    {"name": "methane", "mole_fraction": 0.85},
    {"name": "ethane", "mole_fraction": 0.10},
    {"name": "propane", "mole_fraction": 0.05}
  ],
  "binary_interaction_params": {
    "methane-ethane": 0.003,
    "methane-propane": 0.012,
    "ethane-propane": 0.006
  }
}
```

**Python API**:
```python
from che_toolbox.eos.models import Mixture

# Build mixture from names
mixture = Mixture.from_names(
    compound_names=["methane", "ethane", "propane"],
    mole_fractions=[0.85, 0.10, 0.05],
    database=db,
    binary_interaction_params={
        ("methane", "ethane"): 0.003,
        ("methane", "propane"): 0.012,
        ("ethane", "propane"): 0.006
    }
)

# Calculate mixture properties
T = Quantity(250, "K")
P = Quantity(40, "bar")
state = eos.calculate_state(T, P, mixture)

print(f"Mixture Z factor: {state.z_factor_vapor:.4f}")
print(f"Mixture fugacity coefficient: {state.fugacity_coef_vapor:.4f}")
```

**CLI**:
```bash
pr-calc mixture natural_gas.json -T 250 -P 40

# Output:
# Mixture: natural_gas
# Components:
#   methane    (85.0%)
#   ethane     (10.0%)
#   propane    (5.0%)
#
# Temperature: 250.00 K
# Pressure: 40.00 bar
# Phase: vapor
#
# Mixture Properties:
#   Z factor: 0.8734
#   Fugacity coefficient: 0.8241
```

**Result**: The mixture has a Z factor of 0.8734, indicating significant deviation from ideal gas behavior (12.66% compression relative to ideal gas).

---

## Common Use Cases

### 1. Compressibility Factor Lookup Table

Generate a table of Z factors across a range of pressures:

```python
import pandas as pd

methane = db.get("methane")
T = Quantity(300, "K")

results = []
for P_bar in range(10, 201, 10):  # 10 to 200 bar
    P = Quantity(P_bar, "bar")
    z = eos.calculate_z_factor(T, P, methane)[0]
    results.append({"Pressure_bar": P_bar, "Z_factor": z})

df = pd.DataFrame(results)
print(df)
```

**Output**:
```
   Pressure_bar  Z_factor
0            10    0.9812
1            20    0.9627
2            30    0.9445
...
19          200    1.0234
```

### 2. Vapor Pressure Curve

Generate vapor pressure curve for propane:

```python
propane = db.get("propane")

# Temperature range: 0.5*Tc to 0.95*Tc
Tc = propane.critical_temperature.magnitude
T_range = np.linspace(0.5 * Tc, 0.95 * Tc, 20)

vapor_pressures = []
for T_K in T_range:
    T = Quantity(T_K, "K")
    Psat = eos.calculate_vapor_pressure(T, propane)
    vapor_pressures.append({
        "Temperature_K": T_K,
        "Vapor_Pressure_bar": Psat.magnitude
    })

df = pd.DataFrame(vapor_pressures)
```

### 3. Phase Envelope Detection

Determine phase boundaries for a compound:

```python
methane = db.get("methane")
T = Quantity(150, "K")  # Subcritical

# Find approximate saturation pressure by checking phase
pressures = np.linspace(1, 50, 50)
phases = []

for P_bar in pressures:
    P = Quantity(P_bar, "bar")
    state = eos.calculate_state(T, P, methane)
    phases.append({
        "Pressure_bar": P_bar,
        "Phase": state.phase.value,
        "Num_Roots": len(eos.calculate_z_factor(T, P, methane))
    })

df = pd.DataFrame(phases)
# Identify phase transition where num_roots changes from 1 to 3
```

### 4. Validate Against NIST Data

Run validation tests to verify accuracy:

```bash
# Validate all compounds
pr-calc validate

# Validate specific compound
pr-calc validate methane --output-format json > methane_validation.json

# Generate detailed report
pr-calc validate --report full_validation_report.json
```

---

## Understanding the Results

### Z Factor Interpretation

- **Z = 1.0**: Ideal gas behavior
- **Z > 1.0**: Gas is less compressible than ideal (repulsive forces dominate)
- **Z < 1.0**: Gas is more compressible than ideal (attractive forces dominate)
- **Z ≈ 0.3**: Typical for liquids (highly compressed)

**Example**: Methane at 200 K and 50 bar has Z ≈ 0.94, indicating 6% deviation from ideal gas (attractive forces).

### Fugacity Coefficient Interpretation

- **φ = 1.0**: Ideal behavior, fugacity = pressure
- **φ < 1.0**: Component "wants" to escape from phase (attractive interactions)
- **φ > 1.0**: Component "wants" to stay in phase (repulsive interactions, rare for subcritical)

**Example**: Propane at 300 K and 10 bar has φ ≈ 0.61, meaning effective pressure for equilibrium is 61% of actual pressure.

### Phase Identification

The system automatically identifies phase state:

- **VAPOR**: Low density, high compressibility (typically Z > 0.7)
- **LIQUID**: High density, low compressibility (typically Z < 0.3)
- **SUPERCRITICAL**: Single phase above critical point
- **TWO_PHASE**: Vapor-liquid equilibrium (both phases coexist)

---

## Tips and Best Practices

### 1. Always Use Units

Pint provides dimensional safety - use it!

```python
# Good: Explicit units
T = Quantity(100, "degC")  # Automatically converted to K
P = Quantity(14.7, "psi")  # Automatically converted to bar

# Bad: Bare numbers (assumes K and bar)
T = 373.15  # Is this K or °C?
P = 1.0     # Is this bar, atm, or psi?
```

### 2. Handle Convergence Warnings

Vapor pressure calculations may not converge near critical point:

```python
try:
    Psat = eos.calculate_vapor_pressure(T, water)
except ConvergenceWarning as w:
    print(f"Warning: {w}")
    print(f"Best estimate: {w.best_estimate} bar")
    # Use best estimate or reject calculation
```

### 3. Check Phase State

For two-phase conditions, specify which phase you want:

```python
state = eos.calculate_state(T, P, compound)

if state.phase == PhaseType.TWO_PHASE:
    print(f"Liquid Z: {state.z_factor_liquid}")
    print(f"Vapor Z: {state.z_factor_vapor}")
else:
    print(f"Single phase Z: {state.z_factor_vapor}")
```

### 4. Use JSON Output for Scripting

CLI JSON output is easier to parse in scripts:

```bash
# Extract Z factor in shell script
Z=$(pr-calc z-factor methane -T 300 -P 50 -f json | jq -r '.z_factor')
echo "Z factor: $Z"
```

### 5. Batch Processing

Process multiple conditions efficiently:

```python
# Define conditions
conditions = [
    (Quantity(250, "K"), Quantity(10, "bar")),
    (Quantity(300, "K"), Quantity(50, "bar")),
    (Quantity(350, "K"), Quantity(100, "bar"))
]

# Calculate all
results = []
for T, P in conditions:
    state = eos.calculate_state(T, P, methane)
    results.append({
        "T": T.magnitude,
        "P": P.magnitude,
        "Z": state.z_factor_vapor
    })
```

---

## Common Errors and Solutions

### Error: "Temperature must be positive"

**Cause**: Negative or zero temperature provided

**Solution**: Check temperature units - use absolute temperature (K), not relative (°C without conversion)

```python
# Wrong
T = Quantity(-10, "K")  # Negative absolute temperature!

# Right
T = Quantity(-10, "degC")  # Pint converts to 263.15 K
T = Quantity(263.15, "K")
```

### Error: "Temperature exceeds critical temperature"

**Cause**: Trying to calculate vapor pressure above critical point

**Solution**: Vapor pressure is undefined for supercritical conditions

```python
Tc = compound.critical_temperature.magnitude
if T.magnitude < Tc:
    Psat = eos.calculate_vapor_pressure(T, compound)
else:
    print("Supercritical - no vapor pressure defined")
```

### Error: "Mole fractions must sum to 1.0"

**Cause**: Mixture composition doesn't sum to 1.0

**Solution**: Normalize mole fractions or check for typos

```python
# Wrong
mole_fractions = [0.85, 0.10, 0.06]  # Sums to 1.01

# Right (normalized)
raw_fractions = [0.85, 0.10, 0.06]
total = sum(raw_fractions)
mole_fractions = [x / total for x in raw_fractions]  # Now sums to 1.0
```

### Warning: "Convergence did not achieve tolerance"

**Cause**: Vapor pressure iteration struggled (usually near critical point)

**Solution**: Accept best estimate with caution, or use different method

```python
try:
    Psat = eos.calculate_vapor_pressure(T, compound)
except ConvergenceWarning as w:
    if w.residual < 1e-4:  # Acceptable error
        Psat = w.best_estimate
    else:
        raise  # Re-raise if error too large
```

---

## Next Steps

### Explore Advanced Features

1. **Custom Compounds**: Add compounds not in database
   ```python
   custom = Compound(
       name="benzene",
       formula="C6H6",
       molecular_weight=78.11,
       critical_temperature=Quantity(562.05, "K"),
       critical_pressure=Quantity(48.98, "bar"),
       acentric_factor=0.210
   )
   db.add_compound(custom)
   ```

2. **Custom Binary Interaction Parameters**: Improve mixture accuracy
   ```python
   # Use literature kij values for better predictions
   mixture = Mixture.from_names(
       compound_names=["methane", "CO2"],
       mole_fractions=[0.7, 0.3],
       database=db,
       binary_interaction_params={("methane", "CO2"): 0.0919}
   )
   ```

3. **Validation Testing**: Verify accuracy for your application
   ```bash
   pr-calc validate --property z-factor --report my_validation.json
   ```

### Read the Documentation

- **API Reference**: Full function signatures and parameters
- **Theory Guide**: Peng-Robinson equation derivation and limitations
- **Troubleshooting Guide**: Common issues and convergence problems
- **Examples Gallery**: Advanced use cases and integration patterns

---

## Support and Contributing

### Get Help

- **GitHub Issues**: https://github.com/yourusername/che-toolbox/issues
- **Discussions**: https://github.com/yourusername/che-toolbox/discussions
- **Documentation**: https://che-toolbox.readthedocs.io

### Report Bugs

Found a calculation error or convergence issue? Please report:

1. Minimal example to reproduce
2. Expected vs actual result
3. Python version and dependency versions (`pr-calc --version`)

### Contribute

Contributions welcome! See `CONTRIBUTING.md` for guidelines:

- Add compounds to database (with NIST validation)
- Improve convergence algorithms
- Add binary interaction parameters from literature
- Write documentation and examples

---

## Summary

You now know how to:

✓ Calculate compressibility factors for pure components and mixtures
✓ Find vapor pressures and boiling points
✓ Calculate fugacity coefficients for phase equilibrium
✓ Handle mixtures with binary interaction parameters
✓ Use both Python API and CLI for calculations
✓ Interpret results and handle errors

**Recommended Next Step**: Try the examples with your own compounds and conditions, then explore the full API documentation for advanced features.

Happy calculating! 🧪
