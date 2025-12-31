# Data Model: IAPWS-IF97 Steam Properties

**Feature**: 002-steam-properties | **Date**: 2025-12-30

---

## Core Entities

### Region (Enum)

Identifies which IAPWS-IF97 region applies to given P-T conditions.

```python
from enum import Enum

class Region(Enum):
    REGION1 = 1      # Liquid water (6.8 MPa ≤ P ≤ 863.91 MPa, 273.15 K ≤ T ≤ 863.15 K)
    REGION2 = 2      # Steam/vapor (0 < P ≤ 100 MPa, 273.15 K ≤ T ≤ 863.15 K, below saturation)
    REGION3 = 3      # Supercritical fluid (16.6 MPa ≤ P ≤ 100 MPa, 623.15 K ≤ T ≤ 863.15 K)
    SATURATION = 99  # Two-phase region (on saturation line)
```

**Validation Rules**:
- Pressure: 611.657 Pa ≤ P ≤ 863.91 MPa
- Temperature: 273.15 K ≤ T ≤ 863.15 K
- Any (P, T) outside these bounds is invalid (raise InputRangeError)
- Any (P, T) in two-phase region is invalid for single-phase calculation (raise InputRangeError with saturation guidance)

**Assignment Logic**:
```
Given (P, T):
  If P < P_sat(T):
    Region = REGION2  # Subcooled steam (low pressure)
  Else if P > P_sat(T):
    If P > 16.6 MPa and T > 623.15 K:
      Region = REGION3  # Supercritical
    Else:
      Region = REGION1  # Compressed liquid
  Else:
    Region = SATURATION  # Exactly on saturation line
```

---

### SteamProperties (Dataclass)

Primary return type for single-phase region property calculations (P-T input).

```python
from dataclasses import dataclass
from pint import Quantity

@dataclass
class SteamProperties:
    """Thermodynamic properties of water/steam at specified conditions."""

    # Input conditions (always stored, echoed back for clarity)
    pressure: Quantity  # Input pressure (Pa, but user can provide MPa/bar/etc)
    temperature: Quantity  # Input temperature (K, but user can provide °C)

    # Fundamental properties (all as Pint Quantity with units)
    enthalpy: Quantity  # h in kJ/kg
    entropy: Quantity  # s in kJ/(kg·K)
    internal_energy: Quantity  # u in kJ/kg
    density: Quantity  # ρ in kg/m³

    # Optional derived properties (computed if requested)
    specific_heat_p: Quantity | None = None  # cp in kJ/(kg·K)
    specific_heat_v: Quantity | None = None  # cv in kJ/(kg·K)
    speed_of_sound: Quantity | None = None  # w in m/s
```

**Validation Rules**:
- All properties must be Pint Quantity objects with proper units
- All properties must be finite (no NaN/inf)
- Accuracy metadata: Implicit assumption is ±0.03-0.2% depending on region (documented, not stored)

**Example usage**:
```python
steam = SteamTable()
props = steam.h_pt(10 * ureg.MPa, 500 * ureg.K)
# props = SteamProperties(
#     pressure: <Quantity(10, 'megapascal')>,
#     temperature: <Quantity(500, 'kelvin')>,
#     enthalpy: <Quantity(3373.7, 'kilogram⁻¹ * kilojoule')>,
#     ...
# )
print(props.enthalpy.to('kJ/kg'))  # Extract and convert if needed
```

---

### SaturationProperties (Dataclass)

Return type for saturation calculations (T_sat(P) or P_sat(T)).

```python
@dataclass
class SaturationProperties:
    """Properties at the saturation line (liquid-vapor equilibrium)."""

    # Saturation conditions
    saturation_temperature: Quantity  # T_sat in K
    saturation_pressure: Quantity  # P_sat in Pa

    # Liquid phase properties (subscript 'f' for saturated liquid)
    enthalpy_liquid: Quantity  # h_f in kJ/kg
    entropy_liquid: Quantity  # s_f in kJ/(kg·K)
    density_liquid: Quantity  # ρ_f in kg/m³

    # Vapor phase properties (subscript 'g' for saturated vapor)
    enthalpy_vapor: Quantity  # h_g in kJ/kg
    entropy_vapor: Quantity  # s_g in kJ/(kg·K)
    density_vapor: Quantity  # ρ_g in kg/m³

    # Derived: heat of vaporization (latent heat)
    heat_of_vaporization: Quantity = None  # h_g - h_f

    @property
    def quality(self) -> dict:
        """Thermodynamic quality (undefined; for reference only)."""
        return {
            "note": "Quality is undefined at saturation line; use for two-phase calculations",
            "h_fg": self.heat_of_vaporization,
            "s_fg": self.entropy_vapor - self.entropy_liquid,
        }
```

**Validation Rules**:
- T_sat and P_sat must be consistent (call Wagner-Pruss to verify: P_sat(T_sat) ≈ input pressure within tolerance)
- All properties must be Pint Quantity objects
- Liquid properties must be less than vapor properties (h_f < h_g, ρ_f > ρ_g)

**Example usage**:
```python
steam = SteamTable()
sat_props = steam.T_sat(1 * ureg.MPa)
# Returns saturation properties at 1 MPa
# sat_props.saturation_temperature ≈ 453.04 K
# sat_props.enthalpy_liquid ≈ 417.36 kJ/kg
# sat_props.enthalpy_vapor ≈ 2675.5 kJ/kg
```

---

### InputError Exceptions

Custom exceptions for input validation and numerical stability.

```python
class InputRangeError(ValueError):
    """Raised when pressure or temperature input is outside valid range."""
    message_format = "[Parameter]: [violation]. Valid range: [min]-[max]. Got: [value]"
    # Example: "Temperature: 150 K below triple point. Valid: 273.15-863.15 K. Got: 123.15 K"

class NumericalInstabilityError(RuntimeError):
    """Raised when calculation cannot proceed due to singularity or convergence failure."""
    message_format = "[Error]: [reason]. Distance: [metric]%. Suggestion: [action]"
    # Example: "Region 3 singularity near critical point. Distance: 2.1%. Suggestion: P ≥ 22.6 MPa"

class InvalidStateError(ValueError):
    """Raised when user attempts two-phase calculation on single-phase API."""
    message_format = "[Condition]: On saturation line. Specify quality or use saturation API."
    # Example: "Pressure 1 MPa, Temperature 453.04 K: On saturation line. Use T_sat(P) or P_sat(T)."
```

---

## Derived Entities & Type Aliases

### Quantity (from Pint)

All physical quantities in the library are Pint Quantity objects:
```python
from pint import Quantity

# Types used throughout:
Pressure = Quantity  # Units: Pa, MPa, bar, atm (Pint handles conversion)
Temperature = Quantity  # Units: K, °C, °F (Pint handles conversion)
Energy = Quantity  # Units: J, kJ, MJ (always kg-specific: kJ/kg in library)
Entropy = Quantity  # Units: kJ/(kg·K) standard
Density = Quantity  # Units: kg/m³
```

### Configuration / Constants

Critical point and universal constants:
```python
CRITICAL_POINT = {
    "pressure_Pa": 22.064e6,  # 22.064 MPa
    "temperature_K": 373.946,  # 373.946 K (647.096 K = 373.946 K) [absolute]
}

TRIPLE_POINT = {
    "pressure_Pa": 611.657,  # 611.657 Pa
    "temperature_K": 273.16,  # 273.16 K
}

SINGULARITY_THRESHOLD = 0.05  # 5% normalized distance from critical point

CONVERGENCE_TOLERANCE = {
    "temperature_K": 1e-6,  # 1 µK absolute tolerance
    "pressure_Pa": 1e-3,  # 1 mPa absolute tolerance
}
```

---

## Region Boundaries (Detailed)

### Region 1 Boundary

Compressed liquid water:
- **Pressure**: 6.8 MPa ≤ P ≤ 863.91 MPa
- **Temperature**: 273.15 K ≤ T ≤ 863.15 K
- **Lower boundary**: Saturation line (transition to Region 2 or saturation)
- **Upper boundary**: Maximum pressure/temperature limits of IAPWS-IF97 applicability

### Region 2 Boundary

Superheated steam and subcooled vapor:
- **Pressure**: 0 < P ≤ 100 MPa
- **Temperature**: 273.15 K ≤ T ≤ 863.15 K
- **Lower boundary**: Saturation line (transition to Region 1 or saturation)
- **Sub-regions**:
  - **2a**: 0 < P ≤ 4 MPa, 273.15 K ≤ T ≤ 863.15 K
  - **2b**: 4 < P ≤ 100 MPa, 273.15 K ≤ T ≤ max(T_sat(P), T_boundary)
  - **2c**: 3.4 < P ≤ 100 MPa, T ≥ T_boundary (high-pressure steam near saturation)

### Region 3 Boundary

Supercritical fluid:
- **Pressure**: 16.6 MPa ≤ P ≤ 100 MPa
- **Temperature**: 623.15 K ≤ T ≤ 863.15 K
- **Special consideration**: Overlaps with Region 1 in some (P,T) space; exact boundary determined by saturation curve
- **Singularity zone**: Within 5% of critical point (22.064 MPa, 373.946 K) → raise RuntimeError

### Saturation Line

Two-phase boundary:
- **Applicable range**: 611.657 Pa ≤ P ≤ 22.064 MPa, 273.16 K ≤ T ≤ 647.096 K
- **Wagner-Pruss equation**: Relates P_sat and T_sat
- **Detection**: If P = P_sat(T) for input (P, T) → Region = SATURATION
- **User action**: Use T_sat(P) or P_sat(T) API; single-phase methods raise InvalidStateError

---

## Validation Strategy

### Input Validation (Before Calculation)

1. **Range check**: P and T within global bounds
2. **Type check**: Both inputs are Pint Quantity objects
3. **Unit extraction**: Convert to SI (Pa, K) internally
4. **Region assignment**: Determine which region applies
5. **Singularity check**: If Region 3 and too close to critical point → raise NumericalInstabilityError
6. **Two-phase check**: If region = SATURATION → raise InvalidStateError with guidance

### Output Validation (After Calculation)

1. **Finiteness**: All properties are finite (not NaN/inf)
2. **Physical reasonableness**: Entropy increases with temperature (basic check)
3. **Consistency**: Properties satisfy thermodynamic relations (e.g., h = u + Pv, optional deeper check)
4. **Type check**: All properties wrapped as Pint Quantity with correct units

### Test Coverage

- **Unit tests**: Each validation rule tested in isolation (invalid input → exception with correct message)
- **Integration tests**: Full workflows (valid input → valid output with correct region assignment)
- **Validation tests**: Compare against IAPWS reference tables (100+ points per region)

---

## State Diagram (Conceptual)

```
User Input (P, T)
    ↓
[Validate Range: 611.657 Pa ≤ P ≤ 863.91 MPa, 273.15 K ≤ T ≤ 863.15 K]
    ├─ Invalid? → InputRangeError ✗
    └─ Valid ↓
[Assign Region: Check P vs P_sat(T)]
    ├─ On saturation line? → InvalidStateError (use T_sat or P_sat API) ✗
    ├─ Region 1 (compressed liquid) ↓ [→ Region 1 equations]
    ├─ Region 2 (superheated steam) ↓ [→ Region 2 equations]
    └─ Region 3 (supercritical) ↓
        [Check singularity: distance from critical point ≥ 5%?]
        ├─ Too close? → NumericalInstabilityError ✗
        └─ Valid ↓ [→ Region 3 equations]
[Calculate Properties: h, s, u, ρ from region equations]
    ↓
[Wrap in Pint Quantity with units]
    ↓
[Return SteamProperties object] ✓
```

---

## Entity Relationships

```
SteamTable (main API class)
    ├── uses UnitRegistry (singleton)
    ├── calls Region.assign(P, T)
    ├── dispatches to region1.properties(), region2.properties(), region3.properties()
    ├── returns SteamProperties(...)
    ├── raises InputRangeError, NumericalInstabilityError, InvalidStateError
    └── saturation methods
        ├── T_sat(P) → uses scipy.optimize.brentq
        ├── P_sat(T) → uses Wagner-Pruss direct equation
        └── returns SaturationProperties(...)
```

---

## Implementation Notes

1. **Immutability**: SteamProperties and SaturationProperties are frozen dataclasses (immutable)
2. **Type hints**: Full type coverage (mypy --strict)
3. **Docstrings**: NumPy-style docstrings for all classes and methods
4. **Error messages**: All exceptions include actionable guidance (parameter name, valid range, suggestion)
5. **Unit safety**: Pint prevents silent unit errors (e.g., can't accidentally add kg to Pa)
