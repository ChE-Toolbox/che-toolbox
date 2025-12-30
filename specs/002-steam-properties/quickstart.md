# Quickstart: IAPWS-IF97 Steam Properties

**Feature**: 002-steam-properties | **Date**: 2025-12-30

Get started with steam property calculations in Python, CLI, and web interfaces.

---

## Installation

```bash
pip install iapws-if97
```

Dependencies:
- NumPy 1.24+
- SciPy 1.10+
- Pint 0.23+
- Pydantic 2.x

---

## Python API

### Basic Usage: Pressure-Temperature Properties

```python
from iapws_if97 import SteamTable
from pint import UnitRegistry

ureg = UnitRegistry()
steam = SteamTable()

# Calculate enthalpy at 10 MPa, 500°C (Region 1)
h = steam.h_pt(10 * ureg.MPa, 500 * ureg.celsius)
print(f"Enthalpy: {h}")  # 3373.7 kJ/kg ± 0.03%

# Calculate entropy at 0.1 MPa, 200°C (Region 2)
s = steam.s_pt(0.1 * ureg.MPa, 200 * ureg.celsius)
print(f"Entropy: {s}")  # 7.5064 kJ/(kg·K) ± 0.06%

# Region 3 (supercritical): 25 MPa, 640°C
u = steam.u_pt(25 * ureg.MPa, 640 * ureg.celsius)
print(f"Internal energy: {u}")  # ~2631 kJ/kg ± 0.2%

# Density lookup
rho = steam.rho_pt(1 * ureg.MPa, 300 * ureg.kelvin)
print(f"Density: {rho}")  # kg/m³
```

### Unit Handling

All inputs accept Pint-compatible units. Outputs are always SI with Quantity wrapper:

```python
# Input units are flexible
h1 = steam.h_pt(10 * ureg.MPa, 500 * ureg.K)  # Kelvin
h2 = steam.h_pt(10 * ureg.MPa, 500 * ureg.celsius)  # Celsius (Pint handles offset)
h3 = steam.h_pt(100 * ureg.bar, 500 * ureg.K)  # Different pressure unit

print(f"All equivalent: {h1 ≈ h2 ≈ h3}")

# Output always SI; extract/convert as needed
print(h1.magnitude)  # Raw float: 3373.7
print(h1.to('kJ/kg'))  # Explicit SI unit
print(h1.to('Btu/lbm'))  # Convert to imperial (if Pint has definition)
```

### Saturation Properties

Find liquid/vapor properties at saturation:

```python
# Given pressure, find saturation temperature and properties
sat_at_1mpa = steam.T_sat(1 * ureg.MPa)
print(f"At 1 MPa:")
print(f"  T_sat = {sat_at_1mpa.saturation_temperature}")  # 453.04 K
print(f"  h_liquid = {sat_at_1mpa.enthalpy_liquid}")  # 417.36 kJ/kg
print(f"  h_vapor = {sat_at_1mpa.enthalpy_vapor}")  # 2675.5 kJ/kg
print(f"  ρ_liquid = {sat_at_1mpa.density_liquid}")  # ~887.2 kg/m³
print(f"  ρ_vapor = {sat_at_1mpa.density_vapor}")  # ~5.15 kg/m³

# Given temperature, find saturation pressure
sat_at_100c = steam.P_sat(100 * ureg.celsius)
print(f"At 100°C:")
print(f"  P_sat = {sat_at_100c.saturation_pressure}")  # 0.101325 MPa (1 atm)
print(f"  h_fg = {sat_at_100c.heat_of_vaporization}")  # Latent heat
```

### Error Handling

```python
from iapws_if97 import InputRangeError, NumericalInstabilityError

steam = SteamTable()

# Out-of-range pressure
try:
    h = steam.h_pt(0.1 * ureg.Pa, 500 * ureg.K)  # Way too low
except InputRangeError as e:
    print(f"Caught: {e}")
    # "Pressure: 0.1 Pa below valid range. Valid: 0.611657-863.91 MPa. Got: 0.1 Pa"

# Too close to critical point singularity
try:
    h = steam.h_pt(22.1 * ureg.MPa, 374 * ureg.K)  # Near critical point
except NumericalInstabilityError as e:
    print(f"Caught: {e}")
    # "Region 3 singularity near critical point (22.064 MPa, 373.946 K). Distance: 0.3%. Suggestion: P ≥ 22.6 MPa or T ≥ 382 K"

# Attempting two-phase calculation
try:
    h = steam.h_pt(1 * ureg.MPa, 453 * ureg.K)  # On saturation line
except InvalidStateError as e:
    print(f"Caught: {e}")
    # "Pressure 1 MPa, Temperature 453 K: On saturation line. Use T_sat(P) or P_sat(T) to get saturation properties."
```

### Complete Workflow Example

Typical engineering calculation: Find properties at multiple conditions, compare results:

```python
import pandas as pd
from iapws_if97 import SteamTable
from pint import UnitRegistry

ureg = UnitRegistry()
steam = SteamTable()

# Design a simple power cycle: pressures and temperatures
conditions = [
    {"name": "Boiler exit", "P": 10 * ureg.MPa, "T": 500 * ureg.celsius},
    {"name": "Turbine exit", "P": 0.05 * ureg.MPa, "T": 200 * ureg.celsius},
    {"name": "Condenser", "P": 0.01 * ureg.MPa},  # Saturation at this pressure
]

results = []
for cond in conditions:
    if "T" in cond:
        # Single-phase: use h_pt
        h = steam.h_pt(cond["P"], cond["T"]).to("kJ/kg").magnitude
        s = steam.s_pt(cond["P"], cond["T"]).to("kJ/(kg*K)").magnitude
        region = "1, 2, or 3"
    else:
        # Saturation: use T_sat
        sat = steam.T_sat(cond["P"])
        h = sat.enthalpy_vapor.to("kJ/kg").magnitude  # Assume saturated vapor
        s = sat.entropy_vapor.to("kJ/(kg*K)").magnitude
        region = "Saturation"

    results.append({
        "State": cond["name"],
        "P (MPa)": cond["P"].to("MPa").magnitude,
        "h (kJ/kg)": h,
        "s (kJ/(kg·K))": s,
        "Region": region,
    })

df = pd.DataFrame(results)
print(df)
```

---

## Command-Line Interface

### Basic Property Lookup

```bash
# Single property at P-T point
steam-table --property h --pressure 10 MPa --temperature 500 C
# Output: Enthalpy: 3373.7 kJ/kg

# All properties
steam-table --property all --pressure 10 MPa --temperature 500 C
# Output:
# Pressure: 10.000 MPa
# Temperature: 500.000°C (773.150 K)
# Enthalpy: 3373.7 kJ/kg
# Entropy: 6.5807 kJ/(kg·K)
# Density: 55.783 kg/m³
# Internal energy: 3106.5 kJ/kg

# JSON output for scripting
steam-table --json --property all --pressure 10 MPa --temperature 500 C
# Output:
# {
#   "pressure_Pa": 10000000,
#   "temperature_K": 773.15,
#   "enthalpy_kJ_per_kg": 3373.7,
#   "entropy_kJ_per_kg_K": 6.5807,
#   "density_kg_per_m3": 55.783
# }
```

### Saturation Properties

```bash
# Saturation temperature at given pressure
steam-table --saturated-temperature --pressure 1 MPa
# Output: Saturation temperature at 1.000 MPa: 453.04 K (179.89°C)

# Saturation pressure at given temperature
steam-table --saturated-pressure --temperature 100 C
# Output: Saturation pressure at 373.15 K (100.0°C): 0.1013 MPa (1.013 bar)

# Both phases at saturation
steam-table --json --saturation --pressure 1 MPa
# Output:
# {
#   "saturation_pressure_Pa": 1000000,
#   "saturation_temperature_K": 453.04,
#   "enthalpy_liquid_kJ_per_kg": 417.36,
#   "enthalpy_vapor_kJ_per_kg": 2675.5,
#   "entropy_liquid": 1.3026,
#   "entropy_vapor": 7.1270,
#   "density_liquid_kg_per_m3": 887.2,
#   "density_vapor_kg_per_m3": 5.15
# }
```

### Scripting Examples

```bash
# Batch process multiple conditions
cat conditions.txt
# 10 MPa, 500 C
# 1 MPa, 300 C
# 0.1 MPa, 200 C

cat conditions.txt | while read line; do
  P=$(echo $line | cut -d, -f1)
  T=$(echo $line | cut -d, -f2)
  steam-table --json --property h --pressure "$P" --temperature "$T"
done > results.jsonl
```

---

## Web Interface

Interactive calculator (static web component):

```
https://example.com/steam-calculator
```

Features:
- Input pressure (Pa, MPa, bar, atm, psi)
- Input temperature (K, °C, °F)
- Select property to display (h, s, u, ρ, or all)
- View results with units
- Toggle between scientific and engineering notation
- Copy results to clipboard

---

## Accuracy & Limitations

### Accuracy by Region

| Region | Valid Range | Accuracy |
|--------|-------------|----------|
| **Region 1** | P: 6.8-863.91 MPa, T: 273.15-863.15 K | ±0.03% |
| **Region 2** | P: 0-100 MPa, T: 273.15-863.15 K | ±0.06% |
| **Region 3** | P: 16.6-100 MPa, T: 623.15-863.15 K | ±0.2% |
| **Saturation** | P: 0.611657-22.064 MPa, T: 273.16-647.096 K | ±0.1% |

### What's NOT Included

- **Quality-based inputs** (P-h, T-s): MVP supports P-T only; future enhancement
- **Transport properties** (viscosity, thermal conductivity)
- **Derivatives** (heat capacity cp, cv, compressibility)
- **Two-phase calculations** with explicit quality (x = dryness fraction)

---

## Troubleshooting

**Q: "Conditions too close to critical point" error**
A: You're within 5% of the critical point (22.064 MPa, 373.946 K). Equations are singular here. Try conditions farther from the critical point.

**Q: Why is Temperature in Kelvin input "weird" with Celsius conversion?**
A: Pint handles temperature offset correctly. 100°C = 373.15 K. Input either unit; both work.

**Q: Can I get derivatives (cp, cv)?**
A: Not in MVP. Workaround: compute h at two nearby temperatures, approximate cp ≈ Δh/ΔT.

**Q: Performance is slow?**
A: First call may include JIT compilation (if using Numba). Subsequent calls are fast. Consider caching for loops:
  ```python
  from functools import lru_cache

  # User-side caching
  @lru_cache(maxsize=1000)
  def cached_h_pt(p_mpa, t_c):
      return float(steam.h_pt(p_mpa * ureg.MPa, t_c * ureg.celsius).magnitude)
  ```

---

## API Stability

This is the MVP (Minimum Viable Product) API. Future enhancements may add:
- Quality-based input methods (P-h, T-s, P-s)
- Derivatives and transport properties
- Batch property calculation (array inputs)

Core methods (h_pt, s_pt, u_pt, rho_pt, T_sat, P_sat) are stable and will be supported long-term.
