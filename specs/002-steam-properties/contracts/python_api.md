# Python API Contract: IAPWS-IF97 Steam Properties

**Feature**: 002-steam-properties | **Date**: 2025-12-30 | **Version**: 1.0.0

Complete API specification for Python library users.

---

## Module Structure

```python
# Public API (from iapws_if97 import ...)
from iapws_if97 import (
    SteamTable,                    # Main class for property lookups
    SteamProperties,               # Return type for single-phase properties
    SaturationProperties,          # Return type for saturation properties
    Region,                        # Enum for thermodynamic region
    InputRangeError,               # Exception: input out of bounds
    NumericalInstabilityError,     # Exception: singularity or convergence failure
    InvalidStateError,             # Exception: on saturation line for single-phase API
)

# Unit handling
from iapws_if97 import ureg       # Exported UnitRegistry instance
# or use your own: from pint import UnitRegistry
```

---

## Core Class: SteamTable

Main interface for all property calculations.

### Constructor

```python
class SteamTable:
    def __init__(self):
        """Initialize SteamTable with IAPWS-IF97 coefficients.

        No arguments needed. Internal initialization:
        - Load polynomial coefficients for all regions
        - Initialize saturation line correlation
        - Set up numerical precision parameters
        """
```

### Properties at Pressure-Temperature (P-T)

All methods accept Pint Quantity inputs with flexible units. Output is Pint Quantity in SI.

#### h_pt(pressure: Quantity, temperature: Quantity) → Quantity

```python
def h_pt(self, pressure: Quantity, temperature: Quantity) -> Quantity:
    """Calculate specific enthalpy at given pressure and temperature.

    Args:
        pressure: Pressure with units (e.g., 10*ureg.MPa, 1e7*ureg.Pa)
        temperature: Temperature with units (e.g., 500*ureg.K, 500*ureg.celsius)

    Returns:
        Enthalpy as Pint Quantity with units kJ/kg

    Raises:
        InputRangeError: If P or T outside valid range
        NumericalInstabilityError: If too close to singularities
        InvalidStateError: If on saturation line

    Accuracy:
        ±0.03% Region 1, ±0.06% Region 2, ±0.2% Region 3

    Example:
        >>> steam = SteamTable()
        >>> h = steam.h_pt(10*ureg.MPa, 500*ureg.K)
        >>> h.magnitude  # 3373.7
        >>> h.units  # kJ/kg
    """
```

#### s_pt(pressure: Quantity, temperature: Quantity) → Quantity

```python
def s_pt(self, pressure: Quantity, temperature: Quantity) -> Quantity:
    """Calculate specific entropy at given pressure and temperature.

    Args:
        pressure: Pressure with units
        temperature: Temperature with units

    Returns:
        Entropy as Pint Quantity with units kJ/(kg·K)

    Raises:
        InputRangeError, NumericalInstabilityError, InvalidStateError

    Accuracy:
        ±0.03% Region 1, ±0.06% Region 2, ±0.2% Region 3

    Example:
        >>> s = steam.s_pt(0.1*ureg.MPa, 200*ureg.celsius)
        >>> s  # <Quantity(7.5064, 'kilogram⁻¹ * kilojoule / kelvin')>
    """
```

#### u_pt(pressure: Quantity, temperature: Quantity) → Quantity

```python
def u_pt(self, pressure: Quantity, temperature: Quantity) -> Quantity:
    """Calculate specific internal energy at given pressure and temperature.

    Args:
        pressure: Pressure with units
        temperature: Temperature with units

    Returns:
        Internal energy as Pint Quantity with units kJ/kg

    Raises:
        InputRangeError, NumericalInstabilityError, InvalidStateError

    Accuracy:
        ±0.03% Region 1, ±0.06% Region 2, ±0.2% Region 3

    Note:
        Related to enthalpy by: h = u + P*v (handled internally)

    Example:
        >>> u = steam.u_pt(25*ureg.MPa, 640*ureg.celsius)
        >>> u.to('kJ/kg')
    """
```

#### rho_pt(pressure: Quantity, temperature: Quantity) → Quantity

```python
def rho_pt(self, pressure: Quantity, temperature: Quantity) -> Quantity:
    """Calculate density at given pressure and temperature.

    Args:
        pressure: Pressure with units
        temperature: Temperature with units

    Returns:
        Density as Pint Quantity with units kg/m³

    Raises:
        InputRangeError, NumericalInstabilityError, InvalidStateError

    Accuracy:
        ±0.03% Region 1, ±0.06% Region 2, ±0.2% Region 3

    Example:
        >>> rho = steam.rho_pt(1*ureg.MPa, 300*ureg.K)
        >>> rho.magnitude  # 1004.78 (approximate)
    """
```

### Saturation Line Properties

#### T_sat(pressure: Quantity) → SaturationProperties

```python
def T_sat(self, pressure: Quantity) -> SaturationProperties:
    """Find saturation temperature and properties at given pressure.

    Args:
        pressure: Saturation pressure (0.611657 Pa ≤ P ≤ 22.064 MPa)

    Returns:
        SaturationProperties object containing:
        - saturation_temperature: T_sat (K)
        - saturation_pressure: P_sat (Pa, echoed)
        - enthalpy_liquid, entropy_liquid, density_liquid (subscript 'f')
        - enthalpy_vapor, entropy_vapor, density_vapor (subscript 'g')
        - heat_of_vaporization: h_fg = h_g - h_f

    Raises:
        InputRangeError: If P outside saturation range

    Accuracy:
        ±0.1% for saturation properties

    Example:
        >>> sat = steam.T_sat(1*ureg.MPa)
        >>> sat.saturation_temperature  # <Quantity(453.04, 'kelvin')>
        >>> sat.enthalpy_vapor  # <Quantity(2675.5, 'kilogram⁻¹ * kilojoule')>
    """
```

#### P_sat(temperature: Quantity) → SaturationProperties

```python
def P_sat(self, temperature: Quantity) -> SaturationProperties:
    """Find saturation pressure and properties at given temperature.

    Args:
        temperature: Saturation temperature (273.16 K ≤ T ≤ 647.096 K)

    Returns:
        SaturationProperties object (same as T_sat)

    Raises:
        InputRangeError: If T outside saturation range

    Accuracy:
        ±0.1% for saturation properties

    Example:
        >>> sat = steam.P_sat(100*ureg.celsius)
        >>> sat.saturation_pressure  # <Quantity(0.101325, 'megapascal')>
    """
```

---

## Data Classes

### SteamProperties

Return type for single-phase property lookups (h_pt, s_pt, u_pt, rho_pt).

```python
@dataclass(frozen=True)
class SteamProperties:
    """Thermodynamic properties at specified P-T conditions."""

    pressure: Quantity           # Input pressure (echoed for clarity)
    temperature: Quantity        # Input temperature (echoed)
    enthalpy: Quantity          # h in kJ/kg
    entropy: Quantity           # s in kJ/(kg·K)
    internal_energy: Quantity   # u in kJ/kg
    density: Quantity           # ρ in kg/m³

    # Optional derived properties (computed if requested, else None)
    specific_heat_p: Quantity | None = None   # cp in kJ/(kg·K)
    specific_heat_v: Quantity | None = None   # cv in kJ/(kg·K)
    speed_of_sound: Quantity | None = None    # w in m/s
```

**Usage**:
```python
props = steam.h_pt(10*ureg.MPa, 500*ureg.K)
print(props.enthalpy)      # Access specific property
print(props.pressure)      # Check input conditions
print(props)               # Pretty-print all properties
```

### SaturationProperties

Return type for saturation calculations (T_sat, P_sat).

```python
@dataclass(frozen=True)
class SaturationProperties:
    """Properties at saturation line (liquid-vapor equilibrium)."""

    saturation_temperature: Quantity     # T_sat in K
    saturation_pressure: Quantity        # P_sat in Pa

    enthalpy_liquid: Quantity            # h_f in kJ/kg
    entropy_liquid: Quantity             # s_f in kJ/(kg·K)
    density_liquid: Quantity             # ρ_f in kg/m³

    enthalpy_vapor: Quantity             # h_g in kJ/kg
    entropy_vapor: Quantity              # s_g in kJ/(kg·K)
    density_vapor: Quantity              # ρ_g in kg/m³

    @property
    def heat_of_vaporization(self) -> Quantity:
        """Latent heat: h_fg = h_g - h_f."""
        return self.enthalpy_vapor - self.enthalpy_liquid
```

**Usage**:
```python
sat = steam.T_sat(1*ureg.MPa)
print(sat.enthalpy_liquid)        # Saturated liquid enthalpy
print(sat.enthalpy_vapor)         # Saturated vapor enthalpy
print(sat.heat_of_vaporization)   # Latent heat (derived)
```

---

## Enumerations

### Region

```python
class Region(Enum):
    """IAPWS-IF97 thermodynamic region."""

    REGION1 = 1        # Compressed liquid (6.8-863.91 MPa, 273.15-863.15 K)
    REGION2 = 2        # Superheated steam (0-100 MPa, 273.15-863.15 K)
    REGION3 = 3        # Supercritical (16.6-100 MPa, 623.15-863.15 K)
    SATURATION = 99    # Two-phase region (on saturation line)
```

**Usage** (internal):
```python
region = steam._assign_region(p, t)  # Private method; users don't call directly
if region == Region.REGION1:
    ...
```

---

## Exception Classes

### InputRangeError

```python
class InputRangeError(ValueError):
    """Raised when pressure or temperature input is outside valid range.

    Attributes:
        parameter: Name of invalid parameter ('pressure' or 'temperature')
        value: Value that was invalid
        min_value: Minimum valid value
        max_value: Maximum valid value
        message: Human-readable error message

    Example message:
        "Pressure: 0.1 Pa below valid range. Valid: 0.611657-863.91 MPa. Got: 0.1 Pa"
    """
```

**Usage**:
```python
try:
    h = steam.h_pt(-1*ureg.MPa, 500*ureg.K)  # Negative pressure
except InputRangeError as e:
    print(f"Error: {e}")
    print(f"Parameter: {e.parameter}")
    print(f"Valid range: {e.min_value} to {e.max_value}")
```

### NumericalInstabilityError

```python
class NumericalInstabilityError(RuntimeError):
    """Raised when calculation cannot proceed due to singularity or convergence failure.

    Attributes:
        reason: Why calculation cannot proceed (e.g., "singularity", "no convergence")
        location: Where the problem occurs (e.g., "critical point", "region boundary")
        suggestion: User guidance (e.g., move away from critical point)
        message: Human-readable error message

    Example message:
        "Region 3 singularity near critical point (22.064 MPa, 373.946 K). Distance: 2.1%. Suggestion: P ≥ 22.6 MPa or T ≥ 382 K"
    """
```

**Usage**:
```python
try:
    h = steam.h_pt(22.1*ureg.MPa, 374*ureg.K)  # Near critical point
except NumericalInstabilityError as e:
    print(f"Error: {e}")
    print(f"Suggestion: {e.suggestion}")
```

### InvalidStateError

```python
class InvalidStateError(ValueError):
    """Raised when user attempts to use single-phase API on saturation line.

    Attributes:
        pressure: Input pressure
        temperature: Input temperature
        message: Guidance on correct API to use

    Example message:
        "Pressure 1 MPa, Temperature 453.04 K: On saturation line. Use T_sat(P) or P_sat(T)."
    """
```

**Usage**:
```python
try:
    h = steam.h_pt(1*ureg.MPa, 453*ureg.K)  # On saturation line
except InvalidStateError as e:
    print(f"Error: {e}")
    # Use saturation API instead
    sat = steam.T_sat(1*ureg.MPa)
    h_vapor = sat.enthalpy_vapor
```

---

## Unit Registry

```python
# Singleton UnitRegistry exported from library
from iapws_if97 import ureg

# Standard SI units (always available)
pressure_pa = 1e6 * ureg.Pa
pressure_mpa = 1 * ureg.MPa
temperature_k = 500 * ureg.K
temperature_c = 100 * ureg.celsius
enthalpy = 3373.7 * ureg.kJ / ureg.kg
entropy = 6.5807 * ureg.kJ / ureg.kg / ureg.K
density = 55.783 * ureg.kg / ureg.m3
```

---

## Validation Rules

### Input Validation

1. **Type check**: Arguments must be Pint Quantity objects
2. **Range check**:
   - Pressure: 611.657 Pa ≤ P ≤ 863.91 MPa
   - Temperature: 273.15 K ≤ T ≤ 863.15 K
3. **Region assignment**: (P, T) mapped to Region 1, 2, 3, or SATURATION
4. **Singularity check**: If Region 3 and within 5% of critical point → RuntimeError
5. **State check**: If SATURATION → InvalidStateError

### Output Validation

1. **Finiteness**: All returned quantities are finite (not NaN/inf)
2. **Type safety**: All quantities have correct units
3. **Physical consistency**: Properties increase/decrease as expected (e.g., h increases with T)

---

## Performance Characteristics

- **Single property calculation**: < 10 ms (P-T lookup)
- **Saturation calculation**: < 5 ms (iteration-based)
- **Memory per SteamTable instance**: ~10 MB (coefficients in memory)
- **No caching**: Each call triggers fresh computation (user responsible for caching if needed)

---

## Type Safety & Hints

Full type coverage for static analysis:

```python
from iapws_if97 import SteamTable
from pint import Quantity
from typing import Union

steam: SteamTable = SteamTable()

# Type hints for inputs
P: Quantity = 10 * ureg.MPa
T: Quantity = 500 * ureg.K

# Type hints for outputs
h: Quantity = steam.h_pt(P, T)
sat: SaturationProperties = steam.T_sat(P)

# mypy --strict passes all checks
```

---

## Backward Compatibility

**API Version**: 1.0.0

The core methods (h_pt, s_pt, u_pt, rho_pt, T_sat, P_sat) are stable. Future versions will maintain backward compatibility with these signatures. Future additions (new methods, optional parameters) will not break existing code.

**Deprecation policy**: Any breaking changes will include a 2-release deprecation window with warnings.
