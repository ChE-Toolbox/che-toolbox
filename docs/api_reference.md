# API Reference: Peng-Robinson EOS Thermodynamic Engine

## Overview

The Peng-Robinson EOS implementation provides a complete thermodynamic calculation engine for determining compressibility factors, fugacity coefficients, and vapor pressures for pure components and mixtures.

## Core Classes

### PengRobinsonEOS

Main class for all Peng-Robinson EOS calculations.

```python
from src.eos.peng_robinson import PengRobinsonEOS
from src.compounds.database import CompoundDatabase

db = CompoundDatabase()
methane = db.get("methane")
eos = PengRobinsonEOS()
```

#### Methods

##### `calculate_a(tc, pc, omega, temperature) -> float`

Calculate the 'a' parameter in Peng-Robinson EOS.

**Parameters:**
- `tc` (float): Critical temperature in K
- `pc` (float): Critical pressure in Pa
- `omega` (float): Acentric factor
- `temperature` (float): Temperature in K

**Returns:** Parameter 'a' in Pa·m⁶·mol⁻²

**Raises:** `ValueError` if temperature, tc, or pc is non-positive

**Example:**
```python
a = eos.calculate_a(190.564, 4599200.0, 0.011, 300.0)
```

##### `calculate_b(tc, pc) -> float`

Calculate the 'b' parameter in Peng-Robinson EOS.

**Parameters:**
- `tc` (float): Critical temperature in K
- `pc` (float): Critical pressure in Pa

**Returns:** Parameter 'b' in m³·mol⁻¹

**Example:**
```python
b = eos.calculate_b(190.564, 4599200.0)
```

##### `calculate_z_factor(temperature, pressure, compound) -> tuple[float, ...]`

Calculate compressibility factor(s) for a pure component or mixture.

**Parameters:**
- `temperature` (float): Temperature in K
- `pressure` (float): Pressure in Pa
- `compound` (Compound): Compound object with critical properties

**Returns:** Sorted Z factors (smallest=liquid, largest=vapor)

**Raises:** `ValueError` if temperature or pressure is invalid

**Example:**
```python
z_factors = eos.calculate_z_factor(300.0, 5000000.0, methane)
```

##### `calculate_fugacity_coefficient(temperature, pressure, compound, phase=None) -> float`

Calculate fugacity coefficient for a pure component or mixture.

**Parameters:**
- `temperature` (float): Temperature in K
- `pressure` (float): Pressure in Pa
- `compound` (Compound or Mixture): Compound or mixture object
- `phase` (PhaseType, optional): Phase to use (VAPOR or LIQUID)

**Returns:** Fugacity coefficient (dimensionless)

**Example:**
```python
phi = eos.calculate_fugacity_coefficient(300.0, 5000000.0, methane, PhaseType.VAPOR)
```

##### `calculate_vapor_pressure(temperature, compound) -> float`

Calculate saturation pressure for a pure component.

**Parameters:**
- `temperature` (float): Temperature in K
- `compound` (Compound): Pure compound object

**Returns:** Vapor pressure in Pa

**Raises:** `ValueError` if temperature >= critical temperature

**Example:**
```python
psat = eos.calculate_vapor_pressure(373.15, water)
```

##### `calculate_state(temperature, pressure, compound) -> ThermodynamicState`

Calculate complete thermodynamic state.

**Parameters:**
- `temperature` (float): Temperature in K
- `pressure` (float): Pressure in Pa
- `compound` (Compound or Mixture): Compound or mixture object

**Returns:** ThermodynamicState object with Z, fugacity, and phase

**Example:**
```python
state = eos.calculate_state(300.0, 5000000.0, methane)
print(f"Z = {state.z_factor}, Phase = {state.phase}")
```

## Data Models

### Compound

Represents a pure chemical compound with critical properties.

```python
from src.compounds.models import Compound

methane = Compound(
    name="methane",
    cas_number="74-82-8",
    molecular_weight=16.043,
    tc=190.564,
    pc=4599200.0,
    acentric_factor=0.011
)
```

**Fields:**
- `name` (str): Compound name
- `cas_number` (str): CAS registry number
- `molecular_weight` (float): Molecular weight in g/mol
- `tc` (float): Critical temperature in K
- `pc` (float): Critical pressure in Pa
- `acentric_factor` (float): Acentric factor (-1 < ω < 2)

### Mixture

Represents a multi-component mixture.

```python
from src.eos.models import Mixture

mixture = Mixture(
    compounds=[methane, ethane],
    mole_fractions=[0.85, 0.15]
)
```

**Fields:**
- `compounds` (list[Compound]): List of pure compound objects
- `mole_fractions` (list[float]): Mole fractions (must sum to 1.0)
- `binary_interaction_params` (list[list[float]], optional): kij matrix

### ThermodynamicState

Result of a complete state calculation.

```python
state = eos.calculate_state(temperature, pressure, compound)
print(f"Z = {state.z_factor}")
print(f"Phase = {state.phase}")
```

**Fields:**
- `temperature` (float): Temperature in K
- `pressure` (float): Pressure in Pa
- `z_factor` (float): Compressibility factor
- `fugacity_coefficient` (float): Fugacity coefficient
- `phase` (PhaseType): Identified phase (VAPOR, LIQUID, SUPERCRITICAL, TWO_PHASE)

### PhaseType

Enumeration of thermodynamic phases.

```python
from src.eos.models import PhaseType

phase = PhaseType.VAPOR
phase = PhaseType.LIQUID
phase = PhaseType.SUPERCRITICAL
phase = PhaseType.TWO_PHASE
```

## Database

### CompoundDatabase

Access and manage compound data.

```python
from src.compounds.database import CompoundDatabase

db = CompoundDatabase()  # Loads from data/compounds.json
```

**Methods:**

- `get(name: str) -> Compound`: Get compound by name (case-insensitive)
- `get_by_cas(cas_number: str) -> Compound`: Get compound by CAS number
- `list_compounds() -> list[str]`: List all available compound names
- `add_compound(compound: Compound)`: Add compound to database
- `save()`: Save database to JSON file

**Example:**
```python
db = CompoundDatabase()
methane = db.get("methane")
compounds = db.list_compounds()  # ['ethane', 'methane', 'propane', ...]
```

## Mixing Rules

### calculate_a_mix

Calculate 'a' parameter for mixture using van der Waals mixing rules.

```python
from src.eos.mixing_rules import calculate_a_mix

a_mix = calculate_a_mix(a_values, mole_fractions, kij_matrix)
```

**Parameters:**
- `a_values` (list[float]): Pure component 'a' values
- `mole_fractions` (list[float]): Mole fractions
- `kij_matrix` (list[list[float]]): Binary interaction parameters

**Returns:** Mixed 'a' parameter

### calculate_b_mix

Calculate 'b' parameter for mixture.

```python
from src.eos.mixing_rules import calculate_b_mix

b_mix = calculate_b_mix(b_values, mole_fractions)
```

**Parameters:**
- `b_values` (list[float]): Pure component 'b' values
- `mole_fractions` (list[float]): Mole fractions

**Returns:** Mixed 'b' parameter

## Exceptions

### ConvergenceWarning

Warning raised when vapor pressure calculation doesn't converge.

```python
from src.eos.exceptions import ConvergenceWarning
```

**Attributes:**
- `best_estimate` (float): Best estimate of vapor pressure
- `residual` (float): Final residual value
- `message` (str): Warning message

## Command-Line Interface

See [CLI Interface](../specs/001-peng-robinson/contracts/cli_interface.md) for detailed CLI documentation.

Quick reference:

```bash
# Calculate Z factor
pr-calc z-factor methane -T 300 -P 50

# Calculate fugacity
pr-calc fugacity ethane -T 350 -P 30

# Calculate vapor pressure
pr-calc vapor-pressure water -T 373.15

# Get complete state
pr-calc state methane -T 200 -P 50

# List available compounds
pr-calc list-compounds

# Run validation
pr-calc validate methane
```

## Constants

The gas constant R = 8.314462618 J/(mol·K) = 8.314462618 Pa·m³/(mol·K)

## Numerical Methods

- **Cubic equation solving:** NumPy polynomial roots with analytical fallback (Cardano's method)
- **Vapor pressure iteration:** SciPy Brent's method (brentq) with max 100 iterations
- **Root selection:** Physically meaningful roots only (Z > 0)
- **Phase identification:** Based on reduced conditions and number of real roots

## Units Convention

All internal calculations use SI units:
- Temperature: Kelvin (K)
- Pressure: Pascal (Pa)
- Volume: cubic meter per mole (m³/mol)
- Fugacity: Pascal (Pa)

The CLI accepts inputs in bar and converts automatically.
