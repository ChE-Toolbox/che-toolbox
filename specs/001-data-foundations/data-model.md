# Data Model: Chemical Database Data Foundations

**Date**: 2025-12-29
**Feature**: 001-data-foundations

## Overview

This document defines the data entities, their attributes, relationships, and validation rules for the chemical compound database.

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    CompoundDatabase                         │
├─────────────────────────────────────────────────────────────┤
│ + metadata: DatabaseMetadata                                │
│ + compounds: list[Compound]                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ 1:N
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       Compound                              │
├─────────────────────────────────────────────────────────────┤
│ + cas_number: str (PK)                                      │
│ + name: str                                                 │
│ + formula: str                                              │
│ + iupac_name: str                                           │
│ + coolprop_name: str                                        │
│ + aliases: list[str]                                        │
│ + molecular_weight: Quantity                                │
│ + critical_properties: CriticalProperties                   │
│ + phase_properties: PhaseProperties                         │
│ + source: SourceAttribution                                 │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│CriticalProperties│  │ PhaseProperties │  │SourceAttribution│
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│+ temperature: Q │  │+ boiling_point:Q│  │+ name: str      │
│+ pressure: Q    │  │+ triple_point_T:Q│  │+ url: str       │
│+ density: Q     │  │+ triple_point_P:Q│  │+ retrieved: date│
│+ acentric: float│  │                 │  │+ version: str   │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## Entities

### 1. DatabaseMetadata

Container for database-level metadata.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| version | str | Yes | Semantic version of data format (e.g., "1.0.0") |
| source | str | Yes | Primary data source name |
| retrieved_date | date | Yes | Date data was retrieved/generated |
| attribution | str | Yes | Full attribution statement |
| compound_count | int | Yes | Number of compounds in database |

**Validation Rules**:
- `version` must match pattern `^\d+\.\d+\.\d+$`
- `retrieved_date` must not be in the future

---

### 2. Compound

Core entity representing a chemical compound with its properties.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| cas_number | str | Yes | CAS Registry Number (primary key) |
| name | str | Yes | Common name (e.g., "Water") |
| formula | str | Yes | Chemical formula (e.g., "H2O") |
| iupac_name | str | Yes | IUPAC systematic name |
| coolprop_name | str | Yes | CoolProp lookup identifier |
| aliases | list[str] | No | Alternative names for search |
| molecular_weight | Quantity | Yes | Molecular weight with unit |
| critical_properties | CriticalProperties | Yes | Critical point properties |
| phase_properties | PhaseProperties | Yes | Phase transition properties |
| source | SourceAttribution | Yes | Data source information |

**Validation Rules**:
- `cas_number` must match pattern `^\d{1,7}-\d{2}-\d$` (CAS format)
- `name` must be non-empty, max 100 characters
- `formula` must be non-empty, contain only valid element symbols and numbers
- `molecular_weight` must be positive, unit must be mass/amount dimension

**Identity Rule**: `cas_number` is globally unique and immutable.

---

### 3. Quantity

Represents a physical quantity with magnitude and unit (Pint-compatible).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| magnitude | float | Yes | Numerical value |
| unit | str | Yes | Pint-compatible unit string |

**Validation Rules**:
- `magnitude` must be a finite number (not NaN or Inf)
- `unit` must be parseable by Pint UnitRegistry

**Serialization**:
```json
{
  "magnitude": 647.096,
  "unit": "kelvin"
}
```

---

### 4. CriticalProperties

Critical point thermodynamic properties.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| temperature | Quantity | Yes | Critical temperature (T_c) |
| pressure | Quantity | Yes | Critical pressure (P_c) |
| density | Quantity | Yes | Critical density (ρ_c) |
| acentric_factor | float | Yes | Acentric factor (ω) |

**Validation Rules**:
- `temperature` unit must have temperature dimension, value > 0 K
- `pressure` unit must have pressure dimension, value > 0 Pa
- `density` unit must have mass/volume dimension, value > 0
- `acentric_factor` typically in range [-0.5, 1.5], dimensionless

**Physical Constraints**:
- All values represent the critical point (liquid-vapor equilibrium endpoint)

---

### 5. PhaseProperties

Phase transition properties at standard conditions.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| normal_boiling_point | Quantity | Yes | Boiling point at 1 atm (T_b) |
| triple_point_temperature | Quantity | No | Triple point temperature |
| triple_point_pressure | Quantity | No | Triple point pressure |

**Validation Rules**:
- `normal_boiling_point` unit must have temperature dimension
- Triple point properties are optional (some compounds don't have accessible triple points)
- If triple point temperature provided, pressure must also be provided

---

### 6. SourceAttribution

Metadata for data provenance and attribution.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | str | Yes | Source name (e.g., "CoolProp / NIST WebBook") |
| url | str | Yes | Reference URL |
| retrieved_date | date | Yes | Date data was retrieved |
| version | str | No | Source version if applicable |
| notes | str | No | Additional attribution notes |

**Validation Rules**:
- `name` must be non-empty
- `url` must be valid URL format
- `retrieved_date` must not be in the future

---

## JSON Schema

### Complete Database Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ChemEng Compound Database",
  "type": "object",
  "required": ["metadata", "compounds"],
  "properties": {
    "metadata": {
      "type": "object",
      "required": ["version", "source", "retrieved_date", "attribution", "compound_count"],
      "properties": {
        "version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
        "source": { "type": "string" },
        "retrieved_date": { "type": "string", "format": "date" },
        "attribution": { "type": "string" },
        "compound_count": { "type": "integer", "minimum": 1 }
      }
    },
    "compounds": {
      "type": "array",
      "items": { "$ref": "#/definitions/Compound" }
    }
  },
  "definitions": {
    "Quantity": {
      "type": "object",
      "required": ["magnitude", "unit"],
      "properties": {
        "magnitude": { "type": "number" },
        "unit": { "type": "string" }
      }
    },
    "Compound": {
      "type": "object",
      "required": ["cas_number", "name", "formula", "iupac_name", "coolprop_name",
                   "molecular_weight", "critical_properties", "phase_properties", "source"],
      "properties": {
        "cas_number": { "type": "string", "pattern": "^\\d{1,7}-\\d{2}-\\d$" },
        "name": { "type": "string", "maxLength": 100 },
        "formula": { "type": "string" },
        "iupac_name": { "type": "string" },
        "coolprop_name": { "type": "string" },
        "aliases": { "type": "array", "items": { "type": "string" } },
        "molecular_weight": { "$ref": "#/definitions/Quantity" },
        "critical_properties": { "$ref": "#/definitions/CriticalProperties" },
        "phase_properties": { "$ref": "#/definitions/PhaseProperties" },
        "source": { "$ref": "#/definitions/SourceAttribution" }
      }
    },
    "CriticalProperties": {
      "type": "object",
      "required": ["temperature", "pressure", "density", "acentric_factor"],
      "properties": {
        "temperature": { "$ref": "#/definitions/Quantity" },
        "pressure": { "$ref": "#/definitions/Quantity" },
        "density": { "$ref": "#/definitions/Quantity" },
        "acentric_factor": { "type": "number" }
      }
    },
    "PhaseProperties": {
      "type": "object",
      "required": ["normal_boiling_point"],
      "properties": {
        "normal_boiling_point": { "$ref": "#/definitions/Quantity" },
        "triple_point_temperature": { "$ref": "#/definitions/Quantity" },
        "triple_point_pressure": { "$ref": "#/definitions/Quantity" }
      }
    },
    "SourceAttribution": {
      "type": "object",
      "required": ["name", "url", "retrieved_date"],
      "properties": {
        "name": { "type": "string" },
        "url": { "type": "string", "format": "uri" },
        "retrieved_date": { "type": "string", "format": "date" },
        "version": { "type": "string" },
        "notes": { "type": "string" }
      }
    }
  }
}
```

---

## Example Data

### Water (H2O)

```json
{
  "cas_number": "7732-18-5",
  "name": "Water",
  "formula": "H2O",
  "iupac_name": "oxidane",
  "coolprop_name": "Water",
  "aliases": ["water", "H2O", "dihydrogen monoxide"],
  "molecular_weight": {
    "magnitude": 18.01528,
    "unit": "gram / mole"
  },
  "critical_properties": {
    "temperature": { "magnitude": 647.096, "unit": "kelvin" },
    "pressure": { "magnitude": 22064000, "unit": "pascal" },
    "density": { "magnitude": 322.0, "unit": "kilogram / meter ** 3" },
    "acentric_factor": 0.3443
  },
  "phase_properties": {
    "normal_boiling_point": { "magnitude": 373.124, "unit": "kelvin" },
    "triple_point_temperature": { "magnitude": 273.16, "unit": "kelvin" },
    "triple_point_pressure": { "magnitude": 611.657, "unit": "pascal" }
  },
  "source": {
    "name": "CoolProp / NIST WebBook",
    "url": "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185",
    "retrieved_date": "2025-12-29",
    "version": "CoolProp 7.x",
    "notes": "Critical properties from IAPWS-IF97"
  }
}
```

---

## State Transitions

Compounds in this database are static reference data with no state transitions. The database itself has implicit states:

| State | Description | Transitions |
|-------|-------------|-------------|
| Unloaded | Database not yet loaded into memory | → Loaded (via `load_database()`) |
| Loaded | Database available for queries | → Unloaded (garbage collection) |

---

## Indexing Strategy

For efficient compound lookup:

| Index | Field(s) | Purpose |
|-------|----------|---------|
| Primary | `cas_number` | Unique compound identification |
| Secondary | `name` (lowercase) | Human-friendly lookup |
| Secondary | `coolprop_name` | CoolProp integration |
| Search | `aliases` (flattened) | Flexible user queries |

Implementation: In-memory dictionary with multiple key mappings pointing to same Compound instance.

---

## Validation Test Values

Reference values for NIST validation tests (from CoolProp/NIST WebBook):

| Compound | T_c (K) | P_c (Pa) | ω | Tolerance |
|----------|---------|----------|---|-----------|
| Water | 647.096 | 22064000 | 0.3443 | ±0.01% |
| Methane | 190.564 | 4599200 | 0.01142 | ±0.01% |
| Carbon Dioxide | 304.128 | 7377300 | 0.22394 | ±0.01% |
| Nitrogen | 126.192 | 3395800 | 0.0372 | ±0.01% |
| Ammonia | 405.40 | 11333000 | 0.25601 | ±0.01% |
