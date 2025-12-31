# Python API Contract

**Feature**: 001-peng-robinson
**Interface**: Python Library API
**Date**: 2025-12-29

## Overview

This document defines the public Python API for the Peng-Robinson EOS thermodynamic engine. All functions and classes follow library-first architecture principles with full type annotations and Pint unit support.

---

## Module Structure

```python
from che_toolbox.eos import PengRobinsonEOS
from che_toolbox.eos.models import (
    Compound,
    Mixture,
    ThermodynamicState,
    PhaseType
)
from che_toolbox.compounds import CompoundDatabase
```

---

## Core API

### 1. PengRobinsonEOS Calculator

**Purpose**: Main calculation engine for Peng-Robinson equation of state

#### Constructor

```python
class PengRobinsonEOS:
    """Peng-Robinson equation of state calculator."""

    def __init__(
        self,
        solver_method: Literal["numpy", "analytical", "hybrid"] = "hybrid",
        max_iterations: int = 100,
        tolerance: float = 1e-6
    ) -> None:
        """
        Initialize PR-EOS calculator.

        Parameters
        ----------
        solver_method : {"numpy", "analytical", "hybrid"}
            Method for solving cubic equation:
            - "numpy": NumPy polynomial roots (fast, general)
            - "analytical": Cardano analytical formula (robust near critical point)
            - "hybrid": NumPy with analytical fallback (default, recommended)
        max_iterations : int, default=100
            Maximum iterations for vapor pressure calculations
        tolerance : float, default=1e-6
            Convergence tolerance for iterative methods

        Examples
        --------
        >>> eos = PengRobinsonEOS()  # Use default hybrid solver
        >>> eos = PengRobinsonEOS(solver_method="numpy", max_iterations=50)
        """
```

#### Calculate Z Factor

```python
    def calculate_z_factor(
        self,
        temperature: Quantity,
        pressure: Quantity,
        composition: Compound | Mixture
    ) -> tuple[float, ...]:
        """
        Calculate compressibility factor(s) using Peng-Robinson EOS.

        Parameters
        ----------
        temperature : Quantity
            Absolute temperature (must be > 0 K)
        pressure : Quantity
            Absolute pressure (must be > 0 bar)
        composition : Compound or Mixture
            Pure component or mixture composition

        Returns
        -------
        z_factors : tuple[float, ...]
            Compressibility factor(s):
            - Single value for supercritical or single-phase conditions
            - Two values (Z_liquid, Z_vapor) for two-phase region
            Sorted ascending: smallest root = liquid, largest = vapor

        Raises
        ------
        ValueError
            If temperature or pressure is non-positive
        ValueError
            If no positive real roots found (invalid EOS parameters)

        Examples
        --------
        >>> from pint import Quantity
        >>> methane = compound_db.get("methane")
        >>> T = Quantity(300, "K")
        >>> P = Quantity(50, "bar")
        >>> z = eos.calculate_z_factor(T, P, methane)
        >>> z
        (0.941,)  # Single supercritical root

        >>> # Two-phase region
        >>> T = Quantity(150, "K")
        >>> P = Quantity(10, "bar")
        >>> z = eos.calculate_z_factor(T, P, methane)
        >>> z
        (0.054, 0.923)  # (liquid root, vapor root)
        """
```

#### Calculate Fugacity Coefficient

```python
    def calculate_fugacity_coefficient(
        self,
        temperature: Quantity,
        pressure: Quantity,
        composition: Compound | Mixture,
        phase: PhaseType | None = None
    ) -> float | tuple[float, float]:
        """
        Calculate fugacity coefficient using Peng-Robinson EOS.

        Parameters
        ----------
        temperature : Quantity
            Absolute temperature
        pressure : Quantity
            Absolute pressure
        composition : Compound or Mixture
            Pure component or mixture
        phase : PhaseType or None, optional
            Specify phase (VAPOR or LIQUID) for two-phase region.
            If None, returns both phases if two-phase region detected.

        Returns
        -------
        fugacity_coefficient : float or tuple[float, float]
            Fugacity coefficient φ (dimensionless):
            - Single float if phase specified or single-phase region
            - Tuple (φ_liquid, φ_vapor) if two-phase and phase not specified

        Raises
        ------
        ValueError
            If invalid temperature, pressure, or composition
        ValueError
            If phase specified but not available (e.g., LIQUID for supercritical)

        Notes
        -----
        Fugacity f = φ * P (fugacity coefficient × pressure)
        For ideal gas: φ = 1.0
        For real fluids: φ ≠ 1.0 (deviation from ideality)

        Examples
        --------
        >>> phi = eos.calculate_fugacity_coefficient(T, P, methane)
        >>> phi
        0.892

        >>> # Specify phase in two-phase region
        >>> phi_vap = eos.calculate_fugacity_coefficient(
        ...     T, P, methane, phase=PhaseType.VAPOR
        ... )
        >>> phi_vap
        0.923
        """
```

#### Calculate Vapor Pressure

```python
    def calculate_vapor_pressure(
        self,
        temperature: Quantity,
        compound: Compound
    ) -> Quantity:
        """
        Calculate saturation pressure at given temperature.

        Uses iterative solution (Brent's method) to find pressure where
        vapor and liquid fugacities are equal.

        Parameters
        ----------
        temperature : Quantity
            Absolute temperature (must be < critical temperature)
        compound : Compound
            Pure component (mixtures not supported for vapor pressure)

        Returns
        -------
        vapor_pressure : Quantity
            Saturation pressure in bar

        Raises
        ------
        ValueError
            If temperature ≥ critical temperature (no vapor pressure exists)
        ValueError
            If composition is a Mixture (vapor pressure only for pure components)
        ConvergenceWarning
            If iteration does not converge within max_iterations.
            Warning includes best estimate and final residual.

        Examples
        --------
        >>> water = compound_db.get("water")
        >>> T = Quantity(373.15, "K")  # 100°C
        >>> Psat = eos.calculate_vapor_pressure(T, water)
        >>> Psat.to("bar")
        <Quantity(1.01325, 'bar')>  # Atmospheric pressure

        >>> # Supercritical temperature
        >>> T = Quantity(650, "K")  # Above Tc
        >>> eos.calculate_vapor_pressure(T, water)
        ValueError: Temperature 650.0 K exceeds critical temperature 647.1 K
        """
```

#### Calculate Thermodynamic State

```python
    def calculate_state(
        self,
        temperature: Quantity,
        pressure: Quantity,
        composition: Compound | Mixture
    ) -> ThermodynamicState:
        """
        Calculate complete thermodynamic state (convenience method).

        Computes Z factor, fugacity coefficient, identifies phase, and
        calculates vapor pressure (if applicable).

        Parameters
        ----------
        temperature : Quantity
            Absolute temperature
        pressure : Quantity
            Absolute pressure
        composition : Compound or Mixture
            Component or mixture

        Returns
        -------
        state : ThermodynamicState
            Complete state with all calculated properties populated

        Examples
        --------
        >>> state = eos.calculate_state(
        ...     Quantity(300, "K"),
        ...     Quantity(50, "bar"),
        ...     methane
        ... )
        >>> state.phase
        PhaseType.SUPERCRITICAL
        >>> state.z_factor_vapor
        0.941
        >>> state.fugacity_coef_vapor
        0.892
        """
```

---

### 2. Compound Database

**Purpose**: Access compound critical properties and thermophysical data

```python
class CompoundDatabase:
    """Database of compound critical properties and thermophysical data."""

    def __init__(self, data_path: str | Path = "data/compounds.json") -> None:
        """
        Initialize compound database.

        Parameters
        ----------
        data_path : str or Path, default="data/compounds.json"
            Path to JSON file containing compound data

        Examples
        --------
        >>> db = CompoundDatabase()  # Use default path
        >>> db = CompoundDatabase("custom/path/compounds.json")
        """

    def get(self, name: str) -> Compound:
        """
        Retrieve compound by name.

        Parameters
        ----------
        name : str
            Compound name (case-insensitive, e.g., "methane", "Methane")

        Returns
        -------
        compound : Compound
            Compound object with critical properties

        Raises
        ------
        KeyError
            If compound not found in database

        Examples
        --------
        >>> methane = db.get("methane")
        >>> methane.critical_temperature
        <Quantity(190.564, 'kelvin')>
        """

    def get_by_cas(self, cas_number: str) -> Compound:
        """
        Retrieve compound by CAS Registry Number.

        Parameters
        ----------
        cas_number : str
            CAS number (format: "####-##-#")

        Returns
        -------
        compound : Compound

        Raises
        ------
        KeyError
            If CAS number not found

        Examples
        --------
        >>> methane = db.get_by_cas("74-82-8")
        """

    def list_compounds(self) -> list[str]:
        """
        List all available compound names.

        Returns
        -------
        names : list[str]
            Sorted list of compound names

        Examples
        --------
        >>> db.list_compounds()
        ['ethane', 'methane', 'n-butane', 'propane', 'water']
        """

    def add_compound(self, compound: Compound) -> None:
        """
        Add custom compound to database (in-memory only).

        Parameters
        ----------
        compound : Compound
            Compound object to add

        Examples
        --------
        >>> custom = Compound(
        ...     name="benzene",
        ...     formula="C6H6",
        ...     molecular_weight=78.11,
        ...     critical_temperature=Quantity(562.05, "K"),
        ...     critical_pressure=Quantity(48.98, "bar"),
        ...     acentric_factor=0.210
        ... )
        >>> db.add_compound(custom)
        """
```

---

### 3. Mixture Construction

**Purpose**: Build multi-component mixtures with composition

```python
class Mixture:
    """Multi-component mixture with composition and interaction parameters."""

    @classmethod
    def from_names(
        cls,
        compound_names: list[str],
        mole_fractions: list[float],
        database: CompoundDatabase,
        binary_interaction_params: dict[tuple[str, str], float] | None = None
    ) -> "Mixture":
        """
        Construct mixture from compound names.

        Parameters
        ----------
        compound_names : list[str]
            List of compound names
        mole_fractions : list[float]
            Corresponding mole fractions (must sum to 1.0)
        database : CompoundDatabase
            Database to retrieve compounds from
        binary_interaction_params : dict, optional
            Binary interaction parameters {(name1, name2): kij}
            Default: all kij = 0 (ideal mixing)

        Returns
        -------
        mixture : Mixture

        Examples
        --------
        >>> natural_gas = Mixture.from_names(
        ...     compound_names=["methane", "ethane", "propane"],
        ...     mole_fractions=[0.85, 0.10, 0.05],
        ...     database=db,
        ...     binary_interaction_params={
        ...         ("methane", "ethane"): 0.003,
        ...         ("methane", "propane"): 0.012
        ...     }
        ... )
        """
```

---

## Unit Handling

All API functions accept and return Pint `Quantity` objects for dimensional safety:

```python
from pint import Quantity

# Accepted temperature units: K, degC, degF, degR
T = Quantity(300, "K")
T = Quantity(26.85, "degC")  # Automatically converted to K

# Accepted pressure units: bar, Pa, kPa, MPa, psi, atm
P = Quantity(50, "bar")
P = Quantity(5e6, "Pa")  # Automatically converted to bar

# Results returned in base units (K, bar) unless converted
Psat = eos.calculate_vapor_pressure(T, water)
Psat.to("psi")  # Convert to desired unit
```

---

## Error Handling

### Exceptions

| Exception | When Raised | Example |
|-----------|-------------|---------|
| `ValueError` | Invalid input (T ≤ 0, P ≤ 0, invalid composition) | `ValueError: Temperature must be positive, got T=-10.0 K` |
| `ValueError` | No positive real roots found | `ValueError: Cubic equation has no positive real roots` |
| `ValueError` | Vapor pressure for supercritical T | `ValueError: Temperature exceeds critical temperature` |
| `KeyError` | Compound not in database | `KeyError: Compound 'benzene' not found` |
| `ConvergenceWarning` | Vapor pressure iteration fails | `ConvergenceWarning: Did not converge in 100 iterations` |

### Example Error Handling

```python
from che_toolbox.eos import PengRobinsonEOS, ConvergenceWarning

eos = PengRobinsonEOS()

try:
    Psat = eos.calculate_vapor_pressure(Quantity(650, "K"), water)
except ValueError as e:
    print(f"Invalid input: {e}")

try:
    Psat = eos.calculate_vapor_pressure(Quantity(640, "K"), water)
except ConvergenceWarning as w:
    print(f"Convergence issue: {w}")
    print(f"Best estimate: {w.best_estimate}")
```

---

## Usage Examples

### Example 1: Pure Component Z Factor

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
T = Quantity(300, "K")
P = Quantity(50, "bar")
z = eos.calculate_z_factor(T, P, methane)

print(f"Z factor: {z[0]:.3f}")
# Output: Z factor: 0.941
```

### Example 2: Vapor Pressure Calculation

```python
water = db.get("water")
T = Quantity(373.15, "K")  # 100°C

Psat = eos.calculate_vapor_pressure(T, water)
print(f"Saturation pressure: {Psat.to('bar'):.5f} bar")
# Output: Saturation pressure: 1.01325 bar
```

### Example 3: Mixture Fugacity

```python
# Build mixture
mixture = Mixture.from_names(
    compound_names=["methane", "ethane"],
    mole_fractions=[0.7, 0.3],
    database=db,
    binary_interaction_params={("methane", "ethane"): 0.003}
)

# Calculate fugacity coefficients
T = Quantity(250, "K")
P = Quantity(40, "bar")
phi = eos.calculate_fugacity_coefficient(T, P, mixture)

print(f"Fugacity coefficient: {phi:.3f}")
```

### Example 4: Complete State Calculation

```python
state = eos.calculate_state(
    temperature=Quantity(200, "K"),
    pressure=Quantity(50, "bar"),
    composition=methane
)

print(f"Phase: {state.phase}")
print(f"Z factor: {state.z_factor_vapor:.3f}")
print(f"Fugacity coefficient: {state.fugacity_coef_vapor:.3f}")
print(f"Reduced temperature: {state.reduced_temperature:.3f}")

# Output:
# Phase: PhaseType.SUPERCRITICAL
# Z factor: 0.941
# Fugacity coefficient: 0.892
# Reduced temperature: 1.049
```

---

## Type Annotations

All functions include full type annotations for mypy --strict compliance:

```python
def calculate_z_factor(
    self,
    temperature: Quantity,
    pressure: Quantity,
    composition: Compound | Mixture
) -> tuple[float, ...]:
    ...
```

Enable static type checking:
```bash
mypy --strict src/
```

---

## Testing Support

### Test Fixtures

```python
import pytest
from che_toolbox.compounds import CompoundDatabase

@pytest.fixture
def compound_db() -> CompoundDatabase:
    """Provide compound database for tests."""
    return CompoundDatabase()

@pytest.fixture
def methane(compound_db: CompoundDatabase) -> Compound:
    """Provide methane compound for tests."""
    return compound_db.get("methane")
```

### Validation Utilities

```python
from che_toolbox.validation import NISTValidation

validator = NISTValidation(data_path="data/nist_reference/")
results = validator.validate_all(eos)
print(f"Pass rate: {results.pass_rate:.1%}")
```

---

## Performance Characteristics

| Operation | Typical Time | Notes |
|-----------|--------------|-------|
| Single Z factor calculation | <1 ms | NumPy optimized |
| Fugacity coefficient | <2 ms | Includes Z factor + integration |
| Vapor pressure | 10-50 ms | Iterative, depends on convergence |
| Mixture (5 components) | <5 ms | Mixing rules are O(n²) |
| Complete state | <3 ms | Excludes vapor pressure |

---

## Thread Safety

- `PengRobinsonEOS`: Thread-safe (no mutable state)
- `CompoundDatabase`: Read-only after initialization (thread-safe)
- `Mixture`: Immutable after construction (thread-safe)

Safe for parallel processing with `multiprocessing` or `concurrent.futures`.

---

## Versioning

API follows semantic versioning (SemVer):
- **MAJOR**: Breaking changes to function signatures or return types
- **MINOR**: New features, backward-compatible additions
- **PATCH**: Bug fixes, documentation, internal refactoring

Current version: `0.1.0` (initial implementation)
