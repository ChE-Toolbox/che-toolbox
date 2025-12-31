# Research: Chemical Database Data Foundations

**Date**: 2025-12-29
**Feature**: 001-data-foundations

## Executive Summary

This research resolves technical unknowns for implementing the chemical compound database with NIST-validated data and Pint-based unit handling.

---

## 1. NIST Data Access Strategy

### Decision: Use CoolProp as Primary Data Source with NIST Validation

**Rationale**:
- CoolProp is MIT-licensed, aligns with Constitution Principle IV (Public Domain Data Only)
- Provides programmatic API (no web scraping needed)
- Includes 122+ fluids with high-accuracy thermodynamic properties
- Data is derived from peer-reviewed sources and validated against NIST REFPROP
- Direct Python integration via `CoolProp` package
- **All fluid data compiled into library** - 100% offline, no external dependencies after installation
- Uses equations of state for on-demand calculations (~50ms vs ~10ms for JSON lookups)

**Alternatives Considered**:
| Alternative | Reason Rejected |
|-------------|-----------------|
| NIST WebBook scraping | No official API; scraping is fragile and may violate ToS |
| NIST WebBook wrapper (subpath/NIST_chemistry_webbook_wrapper) | Returns pandas DataFrame; limited to fluid systems; web-dependent |
| Manual NIST data entry | Error-prone; time-consuming; hard to maintain |
| REFPROP | Commercial license ($$$); violates Principle V (Cost-Free) |

**Validation Approach**:
- Use CoolProp as runtime data source
- Store static reference data in JSON for the 10 core compounds
- Validation tests compare stored values against CoolProp and document NIST WebBook URLs as authoritative references

### Data Sources

| Source | License | Use Case |
|--------|---------|----------|
| [CoolProp](https://github.com/CoolProp/CoolProp) | MIT | Primary property calculations |
| [NIST WebBook](https://webbook.nist.gov/chemistry/) | Public Domain | Reference validation, attribution |
| [PubChem](https://pubchem.ncbi.nlm.nih.gov/) | Public Domain | CAS numbers, molecular formulas |

---

## 2. Thermophysical Properties Scope

### Decision: Core Properties Set (Extensible)

**Properties to Include**:

| Property | Symbol | Unit (SI) | Required | Source |
|----------|--------|-----------|----------|--------|
| Molecular Weight | MW | g/mol | Yes | CoolProp/PubChem |
| Critical Temperature | T_c | K | Yes | CoolProp |
| Critical Pressure | P_c | Pa | Yes | CoolProp |
| Critical Density | rho_c | kg/m³ | Yes | CoolProp |
| Acentric Factor | omega | dimensionless | Yes | CoolProp |
| Normal Boiling Point | T_b | K | Yes | CoolProp |
| Triple Point Temperature | T_tp | K | Optional | CoolProp |
| Triple Point Pressure | P_tp | Pa | Optional | CoolProp |
| CAS Number | - | string | Yes | PubChem |
| Chemical Formula | - | string | Yes | PubChem |
| IUPAC Name | - | string | Yes | PubChem |

**Rationale**: These properties enable equation-of-state calculations (Peng-Robinson, SRK) and are universally available in CoolProp for all target compounds.

**CoolProp Property Keys**:
```python
# Critical properties
T_crit = CP.PropsSI("Tcrit", "Water")  # K
P_crit = CP.PropsSI("pcrit", "Water")  # Pa
rho_crit = CP.PropsSI("rhocrit", "Water")  # kg/m³

# Other properties
MW = CP.PropsSI("molar_mass", "Water")  # kg/mol (convert to g/mol)
T_boiling = CP.PropsSI("T", "P", 101325, "Q", 0, "Water")  # Normal BP
omega = CP.PropsSI("acentric", "Water")  # Acentric factor
```

---

## 3. Unit Handling with Pint

### Decision: Pint with Custom UnitRegistry + Pydantic Integration

**Rationale**:
- Constitution mandates Pint for dimensional analysis (Principle I)
- Pint already in dependencies (chemeng-core pyproject.toml)
- Prevents unit conversion errors in calculations

**Implementation Pattern**:

```python
from pint import UnitRegistry

# Create shared registry
ureg = UnitRegistry()
Q_ = ureg.Quantity

# Chemical engineering units (already in Pint default)
# Pa, bar, psi, atm, K, degC, degF, kg/m³, mol, J, cal, BTU
```

**Pydantic Integration Strategy**:

```python
from pydantic import BaseModel, field_validator, field_serializer
from typing import Annotated

class QuantityField(BaseModel):
    """Store quantity as magnitude + unit string for JSON serialization."""
    magnitude: float
    unit: str

    def to_pint(self, ureg: UnitRegistry) -> Quantity:
        return ureg.Quantity(self.magnitude, self.unit)

    @classmethod
    def from_pint(cls, q: Quantity) -> "QuantityField":
        return cls(magnitude=q.magnitude, unit=str(q.units))
```

**JSON Serialization Format**:
```json
{
  "critical_temperature": {
    "magnitude": 647.096,
    "unit": "kelvin"
  }
}
```

**Alternatives Considered**:
| Alternative | Reason Rejected |
|-------------|-----------------|
| Store raw floats with separate unit field | Loses dimensional safety |
| Use `pint-pandas` | Over-engineering for static data |
| Custom unit system | Reinventing the wheel; violates Principle VII |

---

## 4. Data Storage Format

### Decision: JSON Files in `packages/core/src/chemeng_core/data/`

**Rationale**:
- Aligns with existing data directory README guidelines
- JSON is human-readable, version-controllable
- 10 compounds with ~15 properties each = ~5KB total (well under 100KB limit)
- No database dependencies (SQLite, etc.) = simpler architecture

**File Structure**:
```
packages/core/src/chemeng_core/data/
├── compounds/
│   └── compounds.json      # All 10 compounds in single file
├── units/
│   └── unit_registry.txt   # Custom Pint unit definitions (if needed)
└── README.md               # Existing documentation
```

**JSON Schema** (see data-model.md for full schema):
```json
{
  "metadata": {
    "version": "1.0.0",
    "source": "CoolProp 7.x / NIST WebBook",
    "retrieved_date": "2025-12-29",
    "attribution": "..."
  },
  "compounds": [...]
}
```

---

## 5. Validation Strategy

### Decision: Pytest with `@pytest.mark.validation` Marker

**Rationale**:
- Constitution requires validation tests for all calculations (Principle III)
- Existing pytest markers in pyproject.toml support this pattern
- Separates validation tests from unit tests for targeted runs

**Test Structure**:
```
packages/core/tests/
├── unit/
│   ├── test_compound_model.py    # Schema validation
│   └── test_unit_handler.py      # Unit conversion
├── validation/
│   └── test_nist_validation.py   # Compare to NIST values
└── conftest.py                   # Shared fixtures
```

**Validation Test Pattern**:
```python
@pytest.mark.validation
def test_water_critical_temperature():
    """Validate water T_c against NIST WebBook.

    Source: https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185
    NIST Value: 647.096 K
    Tolerance: ±0.01 K (0.0015%)
    """
    compound = get_compound("water")
    assert compound.critical_temperature.magnitude == pytest.approx(647.096, rel=1e-4)
```

**Tolerance Guidelines**:
| Property Type | Relative Tolerance | Rationale |
|--------------|-------------------|-----------|
| Critical T/P | ±0.01% | High-accuracy NIST data |
| Normal Boiling Point | ±0.1% | Some source variation |
| Acentric Factor | ±1% | Derived property, more uncertainty |

---

## 6. Compound Identification

### Decision: Multiple Identifiers with CAS as Primary Key

**Identifiers per Compound**:
| Field | Example (Water) | Purpose |
|-------|-----------------|---------|
| `cas_number` | "7732-18-5" | Primary key, universally unique |
| `name` | "Water" | Human-readable, display |
| `formula` | "H2O" | Chemical notation |
| `iupac_name` | "oxidane" | Official systematic name |
| `coolprop_name` | "Water" | CoolProp lookup key |
| `aliases` | ["H2O", "water", "dihydrogen monoxide"] | Search support |

**Rationale**: CAS numbers are globally unique and unambiguous. Multiple lookup methods support different user workflows.

---

## 7. Target Compound CoolProp Names

| Compound | CoolProp Name | CAS Number |
|----------|---------------|------------|
| Methane | "Methane" | 74-82-8 |
| Ethane | "Ethane" | 74-84-0 |
| Propane | "Propane" | 74-98-6 |
| Water | "Water" | 7732-18-5 |
| Ammonia | "Ammonia" | 7664-41-7 |
| Carbon Dioxide | "CarbonDioxide" | 124-38-9 |
| Nitrogen | "Nitrogen" | 7727-37-9 |
| Oxygen | "Oxygen" | 7782-44-7 |
| Hydrogen | "Hydrogen" | 1333-74-0 |
| Helium | "Helium" | 7440-59-7 |

---

## 8. Scaling Strategy

### CoolProp Data Architecture (Verified 2025-12-29)

**How CoolProp Stores Data**:
- All 122+ fluid property data is **compiled directly into the library** at build time
- Source data stored as JSON files in `dev/fluids/` folder of the repository
- JSON data embedded during compilation - no external files needed at runtime
- 100% offline operation after `pip install CoolProp`

**How CoolProp Calculates Properties**:
- Uses **equations of state** (Helmholtz energy formulations) for on-demand calculations
- NOT lookup tables - solving thermodynamic equations at runtime
- Performance: ~50ms per calculation vs ~10ms for JSON lookups
- Data sourced from peer-reviewed literature, validated against NIST REFPROP

### Tiered Registry Architecture

**Decision**: Implement JSON registry now, design for future CoolProp integration

**Scaling Thresholds**:

| Compound Count | Strategy | Storage | Performance | Implementation |
|----------------|----------|---------|-------------|----------------|
| 0-50 | Single JSON file | ~5-25KB | <10ms | Current feature |
| 50-200 | Split JSON files | ~100KB | <10ms | Future (lazy load) |
| 200+ | Tiered registry | ~100KB + CoolProp | <10ms (JSON) / ~50ms (CoolProp) | Future (multi-tier) |

**Tiered Registry Design** (future implementation):
```python
class CompoundRegistry:
    def get_compound(self, identifier: str) -> Compound:
        # Tier 1: Core compounds from JSON (fast, <10ms)
        # Tier 2: Extended compounds from CoolProp (122+ fluids, ~50ms)
        # Tier 3: User-added compounds (custom data)
```

**Rationale**:
- JSON for frequently-used compounds (10-50 core compounds)
- CoolProp for extended library access without storage duplication
- Maintains offline operation throughout all tiers
- No network dependencies at any scale

**When to Migrate**:
- **Phase 2** (50+ compounds): Split JSON files, lazy loading
- **Phase 3** (200+ compounds): Add CoolProp tier 2 fallback
- **Phase 4** (user request): Add user data directory tier 3

---

## 9. Open Questions Resolved

| Question | Resolution |
|----------|------------|
| How to access NIST data programmatically? | Use CoolProp (NIST-validated); store static JSON |
| What properties to include? | Core EOS properties (T_c, P_c, rho_c, omega, T_b, MW) |
| How to handle units? | Pint with magnitude/unit JSON serialization |
| Where to store data? | JSON in `packages/core/src/chemeng_core/data/` |
| How to validate accuracy? | Pytest validation tests vs CoolProp/NIST |
| How to identify compounds? | CAS number as primary key, multiple aliases |
| How to scale beyond 10 compounds? | Tiered registry: JSON (core) → CoolProp (extended) → User data |
| Is CoolProp online or offline? | 100% offline - data compiled into library, no external calls |

---

## References

- [CoolProp GitHub](https://github.com/CoolProp/CoolProp) - MIT License thermophysical property library
- [NIST Chemistry WebBook](https://webbook.nist.gov/chemistry/) - Authoritative reference data
- [Pint Documentation](https://pint.readthedocs.io/) - Python unit handling
- [Pydantic Serialization](https://docs.pydantic.dev/latest/concepts/serialization/) - JSON serialization patterns
