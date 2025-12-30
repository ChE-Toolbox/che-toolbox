# Quickstart: Chemical Database Data Foundations

**Feature**: 001-data-foundations
**Date**: 2025-12-29

## Prerequisites

```bash
# Install chemeng-core package (from repository root)
pip install -e packages/core

# Or install with dev dependencies
pip install -e "packages/core[dev]"
```

---

## Basic Usage

### Load a Compound

```python
from chemeng_core.compounds import get_compound

# Get water by name
water = get_compound("water")
print(water.name)  # "Water"
print(water.cas_number)  # "7732-18-5"
print(water.formula)  # "H2O"

# Get by CAS number
methane = get_compound("74-82-8")
print(methane.name)  # "Methane"

# Get by formula
co2 = get_compound("CO2")
print(co2.name)  # "Carbon Dioxide"
```

### Access Properties

```python
from chemeng_core.compounds import get_compound

water = get_compound("water")

# Critical properties
print(f"T_c: {water.critical_properties.temperature}")
# T_c: QuantityDTO(magnitude=647.096, unit='kelvin')

print(f"P_c: {water.critical_properties.pressure}")
# P_c: QuantityDTO(magnitude=22064000, unit='pascal')

print(f"Acentric factor: {water.critical_properties.acentric_factor}")
# Acentric factor: 0.3443

# Phase properties
print(f"Normal BP: {water.phase_properties.normal_boiling_point}")
# Normal BP: QuantityDTO(magnitude=373.124, unit='kelvin')

# Molecular weight
print(f"MW: {water.molecular_weight}")
# MW: QuantityDTO(magnitude=18.01528, unit='gram / mole')
```

### Convert Units

```python
from chemeng_core.units import create_unit_handler

handler = create_unit_handler()

# Temperature conversion
t_kelvin = handler.convert(100, "degC", "kelvin")
print(f"100 C = {t_kelvin} K")  # 100 C = 373.15 K

t_fahrenheit = handler.convert(100, "degC", "degF")
print(f"100 C = {t_fahrenheit} F")  # 100 C = 212.0 F

# Pressure conversion
p_bar = handler.convert(101325, "pascal", "bar")
print(f"1 atm = {p_bar} bar")  # 1 atm = 1.01325 bar

p_psi = handler.convert(101325, "pascal", "psi")
print(f"1 atm = {p_psi:.2f} psi")  # 1 atm = 14.70 psi

# Density conversion
rho_lb_ft3 = handler.convert(1000, "kg/m**3", "lb/ft**3")
print(f"1000 kg/m³ = {rho_lb_ft3:.2f} lb/ft³")  # 1000 kg/m³ = 62.43 lb/ft³
```

### Work with Quantities

```python
from chemeng_core.compounds import get_compound
from chemeng_core.units import create_unit_handler

handler = create_unit_handler()
water = get_compound("water")

# Convert a property to different units
t_c_celsius = handler.convert_quantity(
    water.critical_properties.temperature,
    "degC"
)
print(f"Water T_c = {t_c_celsius.magnitude:.2f} {t_c_celsius.unit}")
# Water T_c = 373.95 degC

# Check unit compatibility
print(handler.is_compatible("kelvin", "degC"))  # True
print(handler.is_compatible("kelvin", "pascal"))  # False
```

---

## Using the Registry

```python
from chemeng_core.compounds import create_registry

registry = create_registry()

# List all compounds
for compound in registry.list_all():
    print(f"{compound.name} ({compound.formula})")

# Search compounds
results = registry.search("methane")
print(f"Found {len(results)} matches")

# Get database metadata
meta = registry.metadata
print(f"Database v{meta.version}: {meta.compound_count} compounds")
print(f"Source: {meta.source}")
print(f"Retrieved: {meta.retrieved_date}")
```

---

## Available Compounds

| Name | Formula | CAS Number |
|------|---------|------------|
| Methane | CH₄ | 74-82-8 |
| Ethane | C₂H₆ | 74-84-0 |
| Propane | C₃H₈ | 74-98-6 |
| Water | H₂O | 7732-18-5 |
| Ammonia | NH₃ | 7664-41-7 |
| Carbon Dioxide | CO₂ | 124-38-9 |
| Nitrogen | N₂ | 7727-37-9 |
| Oxygen | O₂ | 7782-44-7 |
| Hydrogen | H₂ | 1333-74-0 |
| Helium | He | 7440-59-7 |

---

## Supported Units

### Temperature
- `kelvin`, `K`
- `degC`, `celsius`
- `degF`, `fahrenheit`
- `degR`, `rankine`

### Pressure
- `pascal`, `Pa`
- `bar`
- `atm`, `atmosphere`
- `psi`
- `mmHg`, `torr`
- `kPa`, `MPa`

### Density
- `kg/m**3`, `kilogram/meter**3`
- `g/cm**3`, `gram/centimeter**3`
- `lb/ft**3`
- `mol/m**3`, `mol/L`

### Energy
- `joule`, `J`
- `kilojoule`, `kJ`
- `calorie`, `cal`
- `BTU`
- `J/mol`, `kJ/mol`

### Molar Mass
- `g/mol`, `gram/mole`
- `kg/mol`, `kilogram/mole`
- `kg/kmol`

---

## Error Handling

```python
from chemeng_core.compounds import get_compound, CompoundNotFoundError
from chemeng_core.units import create_unit_handler, DimensionalityError

# Handle missing compound
try:
    compound = get_compound("unobtainium")
except CompoundNotFoundError as e:
    print(f"Error: {e}")
    # Error: Compound not found: identifier='unobtainium'

# Handle incompatible units
handler = create_unit_handler()
try:
    result = handler.convert(100, "kelvin", "pascal")
except DimensionalityError as e:
    print(f"Error: {e}")
    # Error: Cannot convert from 'kelvin' to 'pascal': incompatible dimensions
```

---

## Data Attribution

All compound data is sourced from:

- **CoolProp** (MIT License) - Primary thermophysical property source
- **NIST WebBook** (Public Domain) - Reference validation

When using this data in publications, please cite:
> CoolProp: Bell, I.H., Wronski, J., Quoilin, S., and Lemort, V. (2014).
> Pure and Pseudo-pure Fluid Thermophysical Property Evaluation and the
> Open-Source Thermophysical Property Library CoolProp. Industrial &
> Engineering Chemistry Research, 53(6), 2498-2508.

---

## Next Steps

- See [data-model.md](./data-model.md) for complete entity documentation
- See [contracts/compound_api.py](./contracts/compound_api.py) for API reference
- Run validation tests: `pytest -m validation packages/core/tests/`
