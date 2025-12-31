# Troubleshooting Guide: Peng-Robinson EOS Implementation

## Common Issues and Solutions

### 1. Vapor Pressure Calculation Issues

#### Problem: ConvergenceWarning - Vapor pressure didn't converge

**Symptoms:**
```
ConvergenceWarning: Vapor pressure calculation did not converge within 100 iterations
best_estimate: 45234.5 Pa
residual: 1.2e-5
```

**Causes:**
- Temperature too close to critical temperature (T > 0.95 × T_c)
- Compound properties inaccurate
- Numerical instability near phase boundary

**Solutions:**
1. **Check input temperature:** Ensure T < T_c
   ```python
   if temperature >= compound.tc:
       raise ValueError("Vapor pressure undefined for T >= Tc")
   ```

2. **Use best estimate:** The warning includes a best estimate
   ```python
   try:
       psat = eos.calculate_vapor_pressure(temperature, compound)
   except ConvergenceWarning as w:
       psat = w.best_estimate  # Use best estimate
       print(f"Using best estimate: {psat} Pa (residual: {w.residual})")
   ```

3. **Reduce tolerance:** Accept larger residuals for edge cases
   ```python
   # Modify maximum iterations or tolerance in source code if needed
   ```

#### Problem: Vapor pressure returns negative or zero value

**Symptoms:**
```
psat = eos.calculate_vapor_pressure(100.0, compound)
# Returns very small or negative value
```

**Cause:** Temperature near critical point; phase equilibrium conditions not met

**Solution:** Verify temperature is well below critical temperature:
```python
assert temperature < compound.tc * 0.95, "Temperature too close to critical point"
```

---

### 2. Z Factor Calculation Issues

#### Problem: Z factor doesn't make physical sense

**Symptoms:**
```
z = eos.calculate_z_factor(temperature, pressure, compound)
# Returns negative or extremely large value (>1.5)
```

**Causes:**
- Pressure much higher than critical pressure
- Numerical issues in cubic solver
- Invalid compound properties

**Solutions:**
1. **Check pressure bounds:**
   ```python
   assert pressure > 0, "Pressure must be positive"
   assert temperature > 0, "Temperature must be positive"
   ```

2. **Verify critical properties in database:**
   ```python
   db = CompoundDatabase()
   compound = db.get("methane")
   print(f"Tc={compound.tc}, Pc={compound.pc}, omega={compound.acentric_factor}")
   # Tc should be ~190K for methane, not 190,000K
   ```

3. **Check pressure units:** Ensure pressure is in Pa, not bar
   ```python
   # Correct: 50 bar = 5,000,000 Pa
   pressure_pa = 50 * 100000.0
   z = eos.calculate_z_factor(300.0, pressure_pa, compound)
   ```

#### Problem: Multiple Z factors returned - which one to use?

**Symptoms:**
```python
z_factors = eos.calculate_z_factor(150.0, 1000000.0, methane)
# Returns (0.23, 0.78)  # Two roots
```

**Explanation:** In two-phase region, smallest root = liquid, largest = vapor

**Solution:** Use phase identification to select correct root
```python
state = eos.calculate_state(temperature, pressure, compound)
if state.phase == PhaseType.TWO_PHASE:
    # Both liquid and vapor coexist
    print(f"Liquid Z: {state.z_factor} (smallest root)")
    print(f"Vapor Z: {state.z_factor} (largest root)")
elif state.phase == PhaseType.VAPOR:
    print(f"Vapor Z: {state.z_factor}")
elif state.phase == PhaseType.LIQUID:
    print(f"Liquid Z: {state.z_factor}")
```

---

### 3. Fugacity Coefficient Issues

#### Problem: Fugacity coefficient > 1.0 for vapor phase

**Symptoms:**
```python
phi = eos.calculate_fugacity_coefficient(300.0, pressure, compound)
# Returns 1.2 for vapor (should be < 1.0 typically)
```

**Explanation:** Not necessarily wrong! Fugacity coefficient can exceed 1.0 in certain regions (high pressure, low temperature)

**Verify:** Calculate fugacity itself:
```python
phi = eos.calculate_fugacity_coefficient(temperature, pressure, compound, PhaseType.VAPOR)
fugacity = phi * pressure
print(f"φ = {phi}, f = {fugacity} Pa")
# Fugacity should be physical (0 < f < P)
```

#### Problem: Fugacity coefficients of mixture don't match sum rule

**Symptoms:**
```python
# For mixture: Σ(xi * ln(φi)) should relate to bulk properties
# If they don't match, something is wrong
```

**Check:** Verify mixture composition sums to 1.0
```python
mixture = Mixture(
    compounds=[comp1, comp2],
    mole_fractions=[0.7, 0.3]
)
assert sum(mixture.mole_fractions) == 1.0
```

---

### 4. Mixture Calculation Issues

#### Problem: ValueError during mixture creation

**Symptoms:**
```
ValueError: mole_fractions must sum to 1.0 (got 0.95)
```

**Solution:** Ensure mole fractions sum to exactly 1.0
```python
xH = 0.85
xE = 1.0 - xH  # Exact 1.0, not 0.15000000001
mixture = Mixture(
    compounds=[methane, ethane],
    mole_fractions=[xH, xE]
)
```

#### Problem: Binary interaction parameters not set

**Symptoms:**
```
Default kij = 0 assumed
# May not match literature values
```

**Solution:** Provide binary interaction parameters explicitly
```python
kij_matrix = [
    [0.000, 0.003],  # methane-ethane
    [0.003, 0.000],  # ethane-methane
]
mixture = Mixture(
    compounds=[methane, ethane],
    mole_fractions=[0.7, 0.3],
    binary_interaction_params=kij_matrix
)
```

**Common values:**
- Methane-ethane: 0.003
- Methane-propane: 0.012
- Ethane-propane: 0.006

---

### 5. Database Issues

#### Problem: Compound not found

**Symptoms:**
```
CompoundError: Compound 'metane' not found
```

**Solution:**
```python
db = CompoundDatabase()
compounds = db.list_compounds()  # See available names
print(compounds)  # ['ethane', 'methane', 'propane', ...]

# Use correct spelling
methane = db.get("methane")  # Not "metane"
```

#### Problem: Invalid compound properties

**Symptoms:**
```
ValueError: acentric_factor=-1.5 must be between -1 and 2
```

**Solution:** Check compound data in `data/compounds.json`
```python
import json
with open("data/compounds.json") as f:
    compounds_data = json.load(f)
    for c in compounds_data:
        if c["name"] == "methane":
            print(json.dumps(c, indent=2))
            # Verify tc > 0, pc > 0, -1 < omega < 2
```

---

### 6. Performance Issues

#### Problem: Calculation is slow

**Symptoms:**
```python
import time
start = time.time()
psat = eos.calculate_vapor_pressure(300.0, methane)
print(time.time() - start)  # Returns 2-5 seconds
```

**Causes:**
- Vapor pressure convergence taking many iterations
- Poor initial bracket bounds
- Numerical instability

**Optimization tips:**
1. **Cache results:** Thermodynamic properties don't change
   ```python
   _z_factor_cache = {}
   def get_z_factor(T, P, compound):
       key = (T, P, compound.name)
       if key not in _z_factor_cache:
           _z_factor_cache[key] = eos.calculate_z_factor(T, P, compound)
       return _z_factor_cache[key]
   ```

2. **Batch calculations:** Process multiple states together
   ```python
   for T in temperatures:
       for P in pressures:
           z = eos.calculate_z_factor(T, P, compound)
   ```

3. **Use approximate methods:** For rough estimates
   ```python
   # Virial EOS for low pressures: Z ≈ 1 + B*P/RT
   ```

---

### 7. CLI Issues

#### Problem: Command not found: pr-calc

**Symptoms:**
```bash
$ pr-calc --version
pr-calc: command not found
```

**Solution:**
```bash
# Install in development mode
pip install -e .

# Or use Python module directly
python -m src.cli.pr_calc --version
```

#### Problem: JSON parsing error in mixture command

**Symptoms:**
```
json.JSONDecodeError: Expecting value at line 1
```

**Solution:** Verify mixture JSON file format
```bash
# Correct format
cat mixture.json
{
  "name": "natural_gas",
  "components": [
    {"name": "methane", "mole_fraction": 0.85},
    {"name": "ethane", "mole_fraction": 0.15}
  ],
  "binary_interaction_params": {
    "methane-ethane": 0.003
  }
}
```

#### Problem: Temperature or pressure unit confusion

**Symptoms:**
```bash
$ pr-calc z-factor methane -T 300 -P 50
# Works fine

$ pr-calc z-factor methane -T 300 --units-pressure psi -P 365  # 50 bar ≈ 725 psi, using 365?
```

**Note:** Default units are K and bar
```bash
pr-calc z-factor methane -T 300 -P 50        # 300 K, 50 bar
pr-calc z-factor methane -T 27 --units-temp degC -P 50  # 300 K (27°C), 50 bar
```

---

## Debugging Tips

### 1. Enable verbose logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("src.eos")

# Now all debug messages will be printed
z_factors = eos.calculate_z_factor(300.0, 5000000.0, methane)
```

### 2. Inspect intermediate values

```python
eos = PengRobinsonEOS()
a = eos.calculate_a(compound.tc, compound.pc, compound.acentric_factor, 300.0)
b = eos.calculate_b(compound.tc, compound.pc)
print(f"a = {a:.6e} Pa*m^6/mol^2")
print(f"b = {b:.6e} m^3/mol")

# Verify reasonable ranges
assert a > 0, "Parameter a should be positive"
assert b > 0, "Parameter b should be positive"
```

### 3. Compare with literature

```python
# Use NIST WebBook to verify results
# https://webbook.nist.gov/chemistry/

# For methane at 300 K, 50 bar:
# Expected Z ≈ 0.9
z = eos.calculate_z_factor(300.0, 5000000.0, methane)
print(f"Calculated Z: {z:.4f}")
print(f"Expected Z: ~0.90")
```

### 4. Unit conversion checklist

- Temperature: Always in Kelvin (K)
- Pressure: Internal calculations use Pa; CLI accepts bar
- Volumes: Always in m³/mol
- Fugacity: Returns Pa (not bar)

```python
# Unit conversions
T_celsius = 27  # °C
T_kelvin = T_celsius + 273.15  # K

P_bar = 50  # bar
P_pa = P_bar * 100000.0  # Pa

P_psi = 725  # psi
P_pa = P_psi * 6894.76  # Pa (1 psi = 6894.76 Pa)
```

---

## Validation Against Expected Values

### Methane at 300 K, 50 bar

**Expected properties (from NIST WebBook):**
- Z ≈ 0.901
- Fugacity coefficient ≈ 0.892

**Test:**
```python
methane = db.get("methane")
z = eos.calculate_z_factor(300.0, 5000000.0, methane)
phi = eos.calculate_fugacity_coefficient(300.0, 5000000.0, methane)

assert 0.85 < z < 0.95, f"Z = {z:.4f} outside expected range"
assert 0.85 < phi < 0.95, f"φ = {phi:.4f} outside expected range"
```

### Water vapor pressure at 373.15 K (100°C)

**Expected:** P_sat ≈ 101,325 Pa (≈ 1 atm)

**Test:**
```python
water = db.get("water")
psat = eos.calculate_vapor_pressure(373.15, water)
psat_bar = psat / 100000.0

assert 0.95 < psat_bar < 1.10, f"P_sat = {psat_bar:.3f} bar outside expected range"
```

---

## Getting Help

1. **Check calculation logs:** Enable debug logging to see intermediate steps
2. **Validate inputs:** Verify all parameters are in correct units and ranges
3. **Compare with NIST:** https://webbook.nist.gov/chemistry/
4. **Review theory:** See [theory.md](theory.md) for underlying equations
5. **Check test cases:** Look at [tests/](../tests/) for working examples
6. **Examine validation data:** See [data/nist_reference/](../data/nist_reference/) for expected values
