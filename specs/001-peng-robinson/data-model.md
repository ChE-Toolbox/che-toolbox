# Data Model: Peng-Robinson EOS

**Feature**: 001-peng-robinson
**Date**: 2025-12-29
**Status**: Phase 1 Design

## Overview

This document defines the data models for the Peng-Robinson equation of state thermodynamic engine. All models use Pydantic for validation and type safety, with Pint for dimensional analysis.

---

## Core Entities

### 1. Compound

Represents a pure chemical species with critical properties required for Peng-Robinson calculations.

**Purpose**: Encapsulate all thermophysical properties needed for EOS calculations

**Attributes**:

| Field | Type | Units | Validation | Description |
|-------|------|-------|------------|-------------|
| `name` | `str` | - | Non-empty, unique identifier | Compound common name (e.g., "methane") |
| `formula` | `str` | - | Valid chemical formula | Molecular formula (e.g., "CH4") |
| `cas_number` | `str` | - | Optional, format: `####-##-#` | CAS Registry Number for unique identification |
| `molecular_weight` | `float` | g/mol | > 0 | Molecular weight |
| `critical_temperature` | `Quantity` | K | > 0 | Critical temperature (Tc) |
| `critical_pressure` | `Quantity` | bar | > 0 | Critical pressure (Pc) |
| `acentric_factor` | `float` | - | -1.0 < ω < 2.0 | Pitzer acentric factor (ω) |
| `ideal_gas_heat_capacity` | `Optional[Callable]` | J/(mol·K) | Optional | Function Cp(T) for advanced calculations |

**Relationships**:
- Used by: `ThermodynamicState`, `Mixture`
- References: `CompoundDatabase`

**Example**:
```python
methane = Compound(
    name="methane",
    formula="CH4",
    cas_number="74-82-8",
    molecular_weight=16.043,
    critical_temperature=Quantity(190.564, "K"),
    critical_pressure=Quantity(45.99, "bar"),
    acentric_factor=0.011
)
```

**Pydantic Validators**:
- `critical_temperature`: Must be positive (> 0 K)
- `critical_pressure`: Must be positive (> 0 bar)
- `acentric_factor`: Physical range check (-1.0 < ω < 2.0)
- `molecular_weight`: Must be positive

---

### 2. Mixture

Represents a multi-component system with composition and binary interaction parameters.

**Purpose**: Define composition and non-ideal mixing behavior for multi-component calculations

**Attributes**:

| Field | Type | Units | Validation | Description |
|-------|------|-------|------------|-------------|
| `components` | `list[Compound]` | - | Length ≥ 1 | List of compounds in mixture |
| `mole_fractions` | `list[float]` | - | Length matches components, all ≥ 0, sum = 1.0 ± 1e-6 | Mole fraction for each component |
| `binary_interaction_params` | `dict[tuple[str, str], float]` | - | -0.5 < kij < 0.5 | Binary interaction parameters (kij) indexed by (compound_i, compound_j) |

**Relationships**:
- Composed of: `Compound` (1 to many)
- Used by: `ThermodynamicState`

**Derived Properties**:
- `is_pure`: bool - True if only one component
- `component_count`: int - Number of components

**Example**:
```python
natural_gas = Mixture(
    components=[methane, ethane, propane],
    mole_fractions=[0.85, 0.10, 0.05],
    binary_interaction_params={
        ("methane", "ethane"): 0.003,
        ("methane", "propane"): 0.012,
        ("ethane", "propane"): 0.006
    }
)
```

**Pydantic Validators**:
- `mole_fractions`:
  - Length must match `components`
  - All values ≥ 0
  - Sum must equal 1.0 ± 1e-6 (floating-point tolerance)
- `binary_interaction_params`:
  - Keys must reference compounds in `components`
  - Symmetric: kij = kji (auto-populate if only one direction provided)
  - Physical range: typically -0.5 < kij < 0.5

**Invariants**:
- `len(mole_fractions) == len(components)`
- `sum(mole_fractions) ≈ 1.0` (within tolerance)
- All kij entries reference valid component pairs

---

### 3. ThermodynamicState

Represents specific conditions (T, P, composition) and calculated properties.

**Purpose**: Encapsulate input conditions and computed EOS properties for a single state point

**Attributes**:

| Field | Type | Units | Validation | Description |
|-------|------|-------|------------|-------------|
| `temperature` | `Quantity` | K | > 0 | Absolute temperature |
| `pressure` | `Quantity` | bar | > 0 | Absolute pressure |
| `composition` | `Compound \| Mixture` | - | Valid compound or mixture | Pure component or mixture |
| `phase` | `PhaseType` | - | Enum: VAPOR, LIQUID, SUPERCRITICAL, TWO_PHASE | Identified phase state |
| `z_factor_vapor` | `Optional[float]` | - | ≥ 0 if present | Compressibility factor (vapor phase) |
| `z_factor_liquid` | `Optional[float]` | - | ≥ 0 if present | Compressibility factor (liquid phase) |
| `fugacity_coef_vapor` | `Optional[float]` | - | > 0 if present | Fugacity coefficient (vapor phase) |
| `fugacity_coef_liquid` | `Optional[float]` | - | > 0 if present | Fugacity coefficient (liquid phase) |
| `vapor_pressure` | `Optional[Quantity]` | bar | > 0 if present, only for pure components | Saturation pressure at given T |

**Relationships**:
- References: `Compound` or `Mixture`
- Computed by: `PengRobinsonEOS` calculator

**Derived Properties**:
- `reduced_temperature`: float - T / Tc
- `reduced_pressure`: float - P / Pc
- `is_subcritical`: bool - T < Tc
- `is_supercritical`: bool - T > Tc or P > Pc

**Example**:
```python
state = ThermodynamicState(
    temperature=Quantity(300, "K"),
    pressure=Quantity(50, "bar"),
    composition=methane,
    phase=PhaseType.SUPERCRITICAL,
    z_factor_vapor=0.941,
    fugacity_coef_vapor=0.892
)
```

**Pydantic Validators**:
- `temperature`: Must be positive (> 0 K)
- `pressure`: Must be positive (> 0 bar)
- `vapor_pressure`: Only valid for pure components (`isinstance(composition, Compound)`)
- Phase consistency: If `phase == TWO_PHASE`, both `z_factor_vapor` and `z_factor_liquid` must be present

**State Transitions**:
- Initial state: T, P, composition provided by user
- After calculation: phase identified, Z factors and fugacity coefficients computed

---

### 4. ValidationTestCase

Represents reference calculation with known inputs and expected outputs from NIST.

**Purpose**: Enable systematic validation of EOS calculations against authoritative data

**Attributes**:

| Field | Type | Units | Validation | Description |
|-------|------|-------|------------|-------------|
| `test_id` | `str` | - | Non-empty, unique | Unique identifier (e.g., "methane_T200_P50") |
| `compound` | `Compound` | - | Valid compound | Compound being tested |
| `temperature` | `Quantity` | K | > 0 | Test temperature |
| `pressure` | `Quantity` | bar | > 0 | Test pressure |
| `nist_z_factor` | `float` | - | > 0 | NIST reference Z factor |
| `nist_fugacity_coef` | `Optional[float]` | - | > 0 if present | NIST reference fugacity coefficient |
| `nist_vapor_pressure` | `Optional[Quantity]` | bar | > 0 if present | NIST reference saturation pressure (if T < Tc) |
| `tolerance_z` | `float` | - | 0 < tol < 1 | Acceptable relative deviation for Z (default: 0.05) |
| `tolerance_fugacity` | `float` | - | 0 < tol < 1 | Acceptable relative deviation for fugacity (default: 0.10) |
| `data_source` | `str` | - | Non-empty | NIST WebBook URL or literature citation |

**Relationships**:
- References: `Compound`
- Used by: Validation test suite

**Derived Properties**:
- `is_vapor_pressure_test`: bool - True if `nist_vapor_pressure` is present
- `is_two_phase`: bool - True if P < nist_vapor_pressure

**Example**:
```python
test_case = ValidationTestCase(
    test_id="methane_T200_P50",
    compound=methane,
    temperature=Quantity(200, "K"),
    pressure=Quantity(50, "bar"),
    nist_z_factor=0.941,
    nist_fugacity_coef=0.892,
    tolerance_z=0.05,
    tolerance_fugacity=0.10,
    data_source="https://webbook.nist.gov/cgi/fluid.cgi?ID=C74828"
)
```

**Validation Methods**:
```python
def validate_z_factor(calculated: float) -> bool:
    """Check if calculated Z is within tolerance of NIST value."""
    relative_error = abs(calculated - nist_z_factor) / nist_z_factor
    return relative_error <= tolerance_z

def validate_fugacity(calculated: float) -> bool:
    """Check if calculated fugacity coefficient is within tolerance."""
    relative_error = abs(calculated - nist_fugacity_coef) / nist_fugacity_coef
    return relative_error <= tolerance_fugacity
```

---

### 5. BinaryInteractionParameter

Represents deviation from ideal mixing for a compound pair.

**Purpose**: Store empirical corrections for mixture calculations

**Attributes**:

| Field | Type | Units | Validation | Description |
|-------|------|-------|------------|-------------|
| `compound_1` | `str` | - | Non-empty | Name of first compound |
| `compound_2` | `str` | - | Non-empty | Name of second compound |
| `k_ij` | `float` | - | -0.5 < kij < 0.5 | Binary interaction parameter |
| `data_source` | `str` | - | Non-empty | Literature citation or experimental source |
| `temperature_range` | `Optional[tuple[Quantity, Quantity]]` | K | T_min < T_max | Valid temperature range (if kij is temperature-dependent) |

**Relationships**:
- References: `Compound` (pair)
- Used by: `Mixture`

**Symmetry Constraint**:
- kij (i,j) = kij (j,i) - order of compounds doesn't matter

**Example**:
```python
kij_methane_ethane = BinaryInteractionParameter(
    compound_1="methane",
    compound_2="ethane",
    k_ij=0.003,
    data_source="Knapp et al. (1982), Vapor-Liquid Equilibria for Mixtures",
    temperature_range=(Quantity(200, "K"), Quantity(400, "K"))
)
```

**Default Behavior**:
- If kij not available for a pair: default to 0.0 (ideal mixing assumption)

---

## Supporting Enums

### PhaseType

```python
from enum import Enum

class PhaseType(str, Enum):
    """Enumeration of possible phase states."""

    VAPOR = "vapor"              # Single vapor phase (low density)
    LIQUID = "liquid"            # Single liquid phase (high density)
    SUPERCRITICAL = "supercritical"  # Single supercritical fluid phase
    TWO_PHASE = "two_phase"      # Vapor-liquid equilibrium
    UNKNOWN = "unknown"          # Phase not yet determined
```

**Assignment Logic**:
1. If T > Tc → `SUPERCRITICAL`
2. If T < Tc and P > Pc → `SUPERCRITICAL`
3. If T < Tc and P < Psat → `VAPOR`
4. If T < Tc and P > Psat → `LIQUID`
5. If T < Tc and P ≈ Psat → `TWO_PHASE` (within tolerance)

---

## Data Storage Formats

### Compound Database (JSON)

**File**: `data/compounds.json`

**Schema**:
```json
{
  "version": "1.0.0",
  "compounds": [
    {
      "name": "methane",
      "formula": "CH4",
      "cas_number": "74-82-8",
      "molecular_weight": 16.043,
      "critical_temperature": 190.564,
      "critical_pressure": 45.99,
      "acentric_factor": 0.011,
      "data_source": "NIST Chemistry WebBook"
    }
  ]
}
```

**Note**: All numeric values in base SI units (K for temperature, bar for pressure)

---

### NIST Reference Data (JSON)

**File**: `data/nist_reference/{compound_name}.json`

**Schema**:
```json
{
  "compound": "methane",
  "data_source": "https://webbook.nist.gov/cgi/fluid.cgi?ID=C74828",
  "critical_properties": {
    "Tc": 190.564,
    "Pc": 45.99,
    "omega": 0.011
  },
  "test_cases": [
    {
      "temperature": 200.0,
      "pressure": 50.0,
      "nist_density": 160.5,
      "nist_z_factor": 0.941,
      "nist_fugacity_coef": 0.892,
      "phase": "supercritical"
    }
  ]
}
```

---

### Binary Interaction Parameters (JSON)

**File**: `data/binary_interaction_params.json`

**Schema**:
```json
{
  "version": "1.0.0",
  "parameters": [
    {
      "compound_1": "methane",
      "compound_2": "ethane",
      "k_ij": 0.003,
      "data_source": "Knapp et al. (1982)",
      "temperature_range": [200, 400]
    }
  ]
}
```

---

## Validation Rules Summary

### Input Validation (Pre-Calculation)

1. **Temperature**: Must be positive (> 0 K)
2. **Pressure**: Must be positive (> 0 bar)
3. **Mole Fractions**: All ≥ 0, sum = 1.0 ± 1e-6
4. **Critical Properties**: Tc > 0, Pc > 0, -1 < ω < 2
5. **Binary Interaction Parameters**: -0.5 < kij < 0.5

### Output Validation (Post-Calculation)

1. **Z Factor**: Must be positive (Z > 0)
2. **Fugacity Coefficient**: Must be positive (φ > 0)
3. **Vapor Pressure**: Must be < Pc for subcritical temperatures
4. **Phase Consistency**: Two-phase region must have both vapor and liquid roots

### Error Handling

- **ValueError**: Raised for invalid inputs (negative values, compositions not summing to 1.0)
- **ConvergenceWarning**: Raised for non-convergent iterations (with best estimate)
- **KeyError**: Raised for missing compound data in database

---

## Type Annotations

All models use full type annotations for mypy --strict compliance:

```python
from pydantic import BaseModel, Field, field_validator
from pint import Quantity
from typing import Optional, Callable

class Compound(BaseModel):
    name: str = Field(..., min_length=1)
    formula: str
    cas_number: Optional[str] = None
    molecular_weight: float = Field(..., gt=0)
    critical_temperature: Quantity
    critical_pressure: Quantity
    acentric_factor: float = Field(..., gt=-1.0, lt=2.0)
    ideal_gas_heat_capacity: Optional[Callable[[float], float]] = None

    @field_validator('critical_temperature', 'critical_pressure')
    @classmethod
    def validate_positive_quantity(cls, v: Quantity) -> Quantity:
        if v.magnitude <= 0:
            raise ValueError(f"Value must be positive, got {v}")
        return v
```

---

## Relationships Diagram

```
Compound ──┬─> ThermodynamicState
           │
           └─> Mixture ──> ThermodynamicState
           │
           └─> ValidationTestCase
           │
           └─> BinaryInteractionParameter

CompoundDatabase ──> Compound (loads from JSON)

PengRobinsonEOS (calculator) ──> ThermodynamicState (computes properties)
```

---

## Future Extensions (Deferred)

1. **FlashResult**: For multi-phase equilibrium calculations (vapor-liquid-liquid)
2. **TemperatureDependentKij**: Support for kij(T) functions
3. **ResidualProperty**: For enthalpy, entropy, heat capacity calculations
4. **ActivityCoefficient**: For liquid-phase non-ideality (advanced mixing rules)

These extensions are out of scope for Phase 1 implementation but may be added in future versions.
