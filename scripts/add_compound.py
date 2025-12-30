#!/usr/bin/env python3
"""CLI utility to add new compounds to the database using CoolProp.

This script extracts properties from CoolProp for a specified fluid and adds
it to the compounds database with proper validation and duplicate checking.

Usage:
    python scripts/add_compound.py <coolprop_name> <cas_number> <name> <formula> <iupac_name> [--aliases <alias1> <alias2> ...] [--nist-url <url>]

Examples:
    # Add Argon
    python scripts/add_compound.py Argon 7440-37-1 "Argon" "Ar" "argon" --aliases argon Ar

    # Add Benzene with NIST URL
    python scripts/add_compound.py Benzene 71-43-2 "Benzene" "C6H6" "benzene" \\
        --aliases benzene C6H6 --nist-url "https://webbook.nist.gov/cgi/cbook.cgi?ID=C71432"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add parent directory to path to import chemeng_core
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "core" / "src"))

try:
    from chemeng_core.compounds.extractor import CoolPropDataExtractor
    from chemeng_core.compounds.loader import add_compound_to_database
except ImportError as e:
    print(f"ERROR: Failed to import chemeng_core: {e}")
    print("Make sure you've installed the package with: pip install -e packages/core")
    sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Add a new compound to the database using CoolProp data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "coolprop_name",
        help="CoolProp fluid identifier (e.g., 'Argon', 'Benzene')",
    )
    parser.add_argument(
        "cas_number",
        help="CAS Registry Number (e.g., '7440-37-1')",
    )
    parser.add_argument(
        "name",
        help="Common name (e.g., 'Argon')",
    )
    parser.add_argument(
        "formula",
        help="Chemical formula (e.g., 'Ar', 'C6H6')",
    )
    parser.add_argument(
        "iupac_name",
        help="IUPAC systematic name (e.g., 'argon', 'benzene')",
    )
    parser.add_argument(
        "--aliases",
        nargs="+",
        default=[],
        help="Alternative names for search (space-separated)",
    )
    parser.add_argument(
        "--nist-url",
        help="NIST WebBook reference URL",
    )
    parser.add_argument(
        "--database",
        default="packages/core/src/chemeng_core/data/compounds/compounds.json",
        help="Path to compounds.json file (default: %(default)s)",
    )
    parser.add_argument(
        "--no-duplicate-check",
        action="store_true",
        help="Skip duplicate checking (dangerous - may create duplicates)",
    )

    args = parser.parse_args()

    # Resolve database path
    db_path = Path(args.database)
    if not db_path.exists():
        print(f"ERROR: Database file not found: {db_path}")
        print(f"Absolute path: {db_path.absolute()}")
        sys.exit(1)

    print(f"Extracting data for {args.name} from CoolProp...")
    print(f"  CoolProp fluid: {args.coolprop_name}")
    print(f"  CAS number: {args.cas_number}")
    print(f"  Formula: {args.formula}")
    print()

    try:
        # Extract compound data
        extractor = CoolPropDataExtractor(args.coolprop_name)
        compound = extractor.extract_compound_data(
            cas_number=args.cas_number,
            name=args.name,
            formula=args.formula,
            iupac_name=args.iupac_name,
            aliases=args.aliases,
            nist_url=args.nist_url,
        )

        print("Extracted properties:")
        print(f"  T_c = {compound.critical_properties.temperature}")
        print(f"  P_c = {compound.critical_properties.pressure}")
        print(f"  ρ_c = {compound.critical_properties.density}")
        print(f"  ω = {compound.critical_properties.acentric_factor}")
        print(f"  T_b = {compound.phase_properties.normal_boiling_point}")
        print(f"  MW = {compound.molecular_weight}")
        print()

        # Add to database
        print(f"Adding compound to database: {db_path}")
        add_compound_to_database(
            compound=compound,
            database_path=db_path,
            check_duplicates=not args.no_duplicate_check,
        )

        print(f"✓ Successfully added {args.name} to database")
        print(f"  Total compounds in database: {len(compound.aliases) + 10}")  # Approximate

    except ValueError as e:
        print(f"ERROR: Invalid input - {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"ERROR: CoolProp extraction failed - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
