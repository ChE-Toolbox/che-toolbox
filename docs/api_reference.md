# API Reference: IAPWS-IF97 Steam Properties

**Project**: 002-steam-properties | **Version**: 1.0.0 | **Date**: 2025-12-30

Complete reference for Python API and exception types.

---

## Module: `iapws_if97`

### Main Class: `SteamTable`

Main API for thermodynamic property calculations.

```python
from iapws_if97 import SteamTable, ureg

steam = SteamTable()
```

#### Method: `h_pt(pressure, temperature) -> Quantity`

Calculate enthalpy at given pressure and temperature.

**Parameters**:
- `pressure` (Quantity): Pressure in any Pint-compatible unit
- `temperature` (Quantity): Temperature in any Pint-compatible unit

**Returns**:
- `Quantity`: Enthalpy in kJ/kg (SI units)

**Raises**:
- `InputRangeError`: If P or T outside valid range
- `NumericalInstabilityError`: If Region 3 and too close to critical point

**Example**:
```python
h = steam.h_pt(10 * ureg.MPa, 500 * ureg.K)  # 3373.7 kJ/kg ± 0.03%
```

---

#### Method: `s_pt(pressure, temperature) -> Quantity`

Calculate entropy at given pressure and temperature.

**Example**:
```python
s = steam.s_pt(10 * ureg.MPa, 500 * ureg.K)  # 6.5807 kJ/(kg·K)
```

---

#### Method: `u_pt(pressure, temperature) -> Quantity`

Calculate internal energy at given pressure and temperature.

**Example**:
```python
u = steam.u_pt(10 * ureg.MPa, 500 * ureg.K)  # 3106.5 kJ/kg
```

---

#### Method: `rho_pt(pressure, temperature) -> Quantity`

Calculate density at given pressure and temperature.

**Example**:
```python
rho = steam.rho_pt(10 * ureg.MPa, 500 * ureg.K)  # 55.783 kg/m³
```

---

#### Method: `T_sat(pressure) -> SaturationProperties`

Calculate saturation temperature and properties for given pressure.

**Example**:
```python
sat = steam.T_sat(1 * ureg.MPa)
print(sat.saturation_temperature)  # 453.04 K
print(sat.enthalpy_vapor)          # 2675.5 kJ/kg
```

---

#### Method: `P_sat(temperature) -> SaturationProperties`

Calculate saturation pressure and properties for given temperature.

**Example**:
```python
sat = steam.P_sat(373.15 * ureg.K)  # 100°C
print(sat.saturation_pressure)     # 0.101325 MPa
```

---

## Data Classes

### `SaturationProperties`

Properties at saturation line with liquid and vapor phase properties.

**Attributes**:
- `saturation_temperature`: T_sat in K
- `saturation_pressure`: P_sat in Pa
- `enthalpy_liquid`: h_f in kJ/kg
- `enthalpy_vapor`: h_g in kJ/kg
- `entropy_liquid`: s_f in kJ/(kg·K)
- `entropy_vapor`: s_g in kJ/(kg·K)
- `density_liquid`: ρ_f in kg/m³
- `density_vapor`: ρ_g in kg/m³
- `heat_of_vaporization`: h_g - h_f (latent heat)

---

## Exceptions

### `InputRangeError`

Raised when input pressure or temperature is outside valid range.

**Valid Ranges**:
- Pressure: 0.611657 Pa to 863.91 MPa
- Temperature: 273.15 K to 863.15 K

---

### `NumericalInstabilityError`

Raised when calculation is too close to singularity or convergence fails.

**Common Causes**:
- Region 3 conditions within 5% of critical point (22.064 MPa, 373.946 K)
- Root-finding iteration failed

---

### `InvalidStateError`

Raised when attempting single-phase calculation on saturation line.

**Solution**: Use `T_sat()` or `P_sat()` methods to query saturation properties.

---

## Unit Registry

```python
from iapws_if97 import ureg

p = 10 * ureg.MPa
t = 500 * ureg.K
p_pa = p.to('Pa')  # Convert to pascal
```

**Supported Units**:
- Pressure: Pa, kPa, MPa, bar, atm, psi
- Temperature: K, °C, °F
- Energy: J, kJ, MJ, Btu

---

## Version Stability

**MVP (v1.0.0)**: Core methods are stable and will not change.

Core methods: `h_pt`, `s_pt`, `u_pt`, `rho_pt`, `T_sat`, `P_sat`
