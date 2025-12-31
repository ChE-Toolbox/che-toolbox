#!/usr/bin/env python3
"""Generate compound data from CoolProp for the initial 10 compounds.

This script extracts thermophysical properties from CoolProp and generates
a compounds.json file with complete NIST-validated data.

Usage:
    python scripts/generate_compound_data.py

Output:
    packages/core/src/chemeng_core/data/compounds/compounds.json
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

try:
    import CoolProp.CoolProp as CP
except ImportError:
    print("ERROR: CoolProp not installed. Run: pip install CoolProp")
    exit(1)

# Target compounds with their CoolProp names and metadata
COMPOUNDS = [
    {
        "coolprop_name": "Water",
        "name": "Water",
        "formula": "H2O",
        "iupac_name": "oxidane",
        "cas_number": "7732-18-5",
        "aliases": ["water", "H2O", "dihydrogen monoxide"],
        "nist_url": "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185",
    },
    {
        "coolprop_name": "Methane",
        "name": "Methane",
        "formula": "CH4",
        "iupac_name": "methane",
        "cas_number": "74-82-8",
        "aliases": ["methane", "CH4"],
        "nist_url": "https://webbook.nist.gov/cgi/cbook.cgi?ID=C74828",
    },
    {
        "coolprop_name": "Ethane",
        "name": "Ethane",
        "formula": "C2H6",
        "iupac_name": "ethane",
        "cas_number": "74-84-0",
        "aliases": ["ethane", "C2H6"],
        "nist_url": "https://webbook.nist.gov/cgi/cbook.cgi?ID=C74840",
    },
    {
        "coolprop_name": "Propane",
        "name": "Propane",
        "formula": "C3H8",
        "iupac_name": "propane",
        "cas_number": "74-98-6",
        "aliases": ["propane", "C3H8"],
        "nist_url": "https://webbook.nist.gov/cgi/cbook.cgi?ID=C74986",
    },
    {
        "coolprop_name": "Ammonia",
        "name": "Ammonia",
        "formula": "NH3",
        "iupac_name": "azane",
        "cas_number": "7664-41-7",
        "aliases": ["ammonia", "NH3"],
        "nist_url": "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7664417",
    },
    {
        "coolprop_name": "CarbonDioxide",
        "name": "Carbon Dioxide",
        "formula": "CO2",
        "iupac_name": "carbon dioxide",
        "cas_number": "124-38-9",
        "aliases": ["carbon dioxide", "CO2"],
        "nist_url": "https://webbook.nist.gov/cgi/cbook.cgi?ID=C124389",
    },
    {
        "coolprop_name": "Nitrogen",
        "name": "Nitrogen",
        "formula": "N2",
        "iupac_name": "molecular nitrogen",
        "cas_number": "7727-37-9",
        "aliases": ["nitrogen", "N2"],
        "nist_url": "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7727379",
    },
    {
        "coolprop_name": "Oxygen",
        "name": "Oxygen",
        "formula": "O2",
        "iupac_name": "molecular oxygen",
        "cas_number": "7782-44-7",
        "aliases": ["oxygen", "O2"],
        "nist_url": "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7782447",
    },
    {
        "coolprop_name": "Hydrogen",
        "name": "Hydrogen",
        "formula": "H2",
        "iupac_name": "molecular hydrogen",
        "cas_number": "1333-74-0",
        "aliases": ["hydrogen", "H2"],
        "nist_url": "https://webbook.nist.gov/cgi/cbook.cgi?ID=C1333740",
    },
    {
        "coolprop_name": "Helium",
        "name": "Helium",
        "formula": "He",
        "iupac_name": "helium",
        "cas_number": "7440-59-7",
        "aliases": ["helium", "He"],
        "nist_url": "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440597",
    },
]


def extract_compound_data(metadata: dict) -> dict:
    """Extract compound data from CoolProp.

    Args:
        metadata: Compound metadata dictionary with coolprop_name, name, etc.

    Returns:
        Complete compound data dictionary
    """
    fluid = metadata["coolprop_name"]

    # Extract critical properties
    T_crit = CP.PropsSI("Tcrit", fluid)  # K
    P_crit = CP.PropsSI("pcrit", fluid)  # Pa
    rho_crit = CP.PropsSI("rhocrit", fluid)  # kg/m³
    omega = CP.PropsSI("acentric", fluid)  # dimensionless

    # Molecular weight (CoolProp returns kg/mol, we want g/mol)
    MW = CP.PropsSI("molar_mass", fluid) * 1000  # kg/mol -> g/mol

    # Normal boiling point (saturation temperature at 1 atm = 101325 Pa)
    try:
        T_boil = CP.PropsSI("T", "P", 101325, "Q", 0, fluid)  # K
    except Exception:
        # Some fluids don't have a boiling point at 1 atm (e.g., CO2, He)
        # Use triple point temperature or critical temperature as fallback
        T_boil = CP.PropsSI("Ttriple", fluid) if CP.PropsSI("Ttriple", fluid) > 0 else T_crit

    # Triple point (optional)
    try:
        T_triple = CP.PropsSI("Ttriple", fluid)  # K
        P_triple = CP.PropsSI("ptriple", fluid)  # Pa
    except Exception:
        T_triple = None
        P_triple = None

    # Build compound data structure
    compound = {
        "cas_number": metadata["cas_number"],
        "name": metadata["name"],
        "formula": metadata["formula"],
        "iupac_name": metadata["iupac_name"],
        "coolprop_name": metadata["coolprop_name"],
        "aliases": metadata["aliases"],
        "molecular_weight": {"magnitude": round(MW, 5), "unit": "gram / mole"},
        "critical_properties": {
            "temperature": {"magnitude": round(T_crit, 5), "unit": "kelvin"},
            "pressure": {"magnitude": round(P_crit, 1), "unit": "pascal"},
            "density": {"magnitude": round(rho_crit, 2), "unit": "kilogram / meter ** 3"},
            "acentric_factor": round(omega, 5),
        },
        "phase_properties": {
            "normal_boiling_point": {"magnitude": round(T_boil, 5), "unit": "kelvin"},
        },
        "source": {
            "name": "CoolProp / NIST WebBook",
            "url": metadata["nist_url"],
            "retrieved_date": str(date.today()),
            "version": f"CoolProp {CP.get_global_param_string('version')}",
            "notes": f"Data extracted from CoolProp for {metadata['name']}",
        },
    }

    # Add triple point if available
    if T_triple is not None and P_triple is not None:
        compound["phase_properties"]["triple_point_temperature"] = {
            "magnitude": round(T_triple, 5),
            "unit": "kelvin",
        }
        compound["phase_properties"]["triple_point_pressure"] = {
            "magnitude": round(P_triple, 1),
            "unit": "pascal",
        }

    return compound


def main() -> None:
    """Generate compounds.json from CoolProp data."""
    print("Generating compound data from CoolProp...")
    print(f"CoolProp version: {CP.get_global_param_string('version')}")

    compounds_data = []

    for compound_meta in COMPOUNDS:
        try:
            print(f"  Extracting data for {compound_meta['name']}...")
            compound_data = extract_compound_data(compound_meta)
            compounds_data.append(compound_data)
        except Exception as e:
            print(f"    ERROR: Failed to extract {compound_meta['name']}: {e}")
            continue

    # Create database structure
    database = {
        "metadata": {
            "version": "1.0.0",
            "source": "CoolProp / NIST WebBook",
            "retrieved_date": str(date.today()),
            "attribution": (
                "Data sourced from CoolProp thermophysical property library (MIT License) "
                "which uses NIST-validated reference equations of state. "
                "See individual compound source URLs for NIST WebBook references."
            ),
            "compound_count": len(compounds_data),
        },
        "compounds": compounds_data,
    }

    # Write to JSON file
    output_path = (
        Path(__file__).parent.parent
        / "packages/core/src/chemeng_core/data/compounds/compounds.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
        f.write("\n")  # Add trailing newline

    print(f"\n✓ Generated {len(compounds_data)} compounds")
    print(f"✓ Output: {output_path}")
    print(f"✓ File size: {output_path.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
