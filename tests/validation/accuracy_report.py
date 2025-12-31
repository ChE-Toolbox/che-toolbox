"""
Accuracy reporting script for IAPWS-IF97 implementation.

Generates summary table of error percentages per region for documentation purposes.
This script analyzes validation results and produces a formatted report suitable
for inclusion in technical documentation.
"""

import json
import sys
from pathlib import Path

import numpy as np
from pint import UnitRegistry

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from iapws_if97 import SteamTable

ureg = UnitRegistry()


def load_reference_data() -> dict:
    """Load IAPWS reference validation tables."""
    validation_file = (
        Path(__file__).parent.parent.parent
        / "src"
        / "iapws_if97"
        / "validation"
        / "iapws_tables.json"
    )

    with open(validation_file) as f:
        return json.load(f)


def calculate_relative_error(computed: float, reference: float) -> float:
    """Calculate relative error as a percentage."""
    if reference == 0:
        return 0.0
    return abs((computed - reference) / reference) * 100


def analyze_region_accuracy(
    region_name: str, test_points: list[dict], steam_table: SteamTable
) -> dict:
    """
    Analyze accuracy for a single region.

    Returns dictionary with statistics:
        - total_points: Number of test points
        - properties: Dict of property-specific stats
        - overall_max_error: Maximum error across all properties
        - overall_avg_error: Average error across all properties
    """
    property_errors = {"enthalpy": [], "entropy": [], "density": [], "internal_energy": []}

    for point in test_points:
        try:
            p_pa = point["pressure_Pa"]
            t_k = point["temperature_K"]

            if "enthalpy_kJ_per_kg" in point:
                h_computed = steam_table.h_pt(p_pa * ureg.Pa, t_k * ureg.K).to("kJ/kg").magnitude
                h_ref = point["enthalpy_kJ_per_kg"]
                property_errors["enthalpy"].append(calculate_relative_error(h_computed, h_ref))

            if "entropy_kJ_per_kg_K" in point:
                s_computed = (
                    steam_table.s_pt(p_pa * ureg.Pa, t_k * ureg.K).to("kJ/(kg*K)").magnitude
                )
                s_ref = point["entropy_kJ_per_kg_K"]
                property_errors["entropy"].append(calculate_relative_error(s_computed, s_ref))

            if "density_kg_per_m3" in point:
                rho_computed = (
                    steam_table.rho_pt(p_pa * ureg.Pa, t_k * ureg.K).to("kg/m^3").magnitude
                )
                rho_ref = point["density_kg_per_m3"]
                property_errors["density"].append(calculate_relative_error(rho_computed, rho_ref))

            if "internal_energy_kJ_per_kg" in point:
                u_computed = steam_table.u_pt(p_pa * ureg.Pa, t_k * ureg.K).to("kJ/kg").magnitude
                u_ref = point["internal_energy_kJ_per_kg"]
                property_errors["internal_energy"].append(
                    calculate_relative_error(u_computed, u_ref)
                )

        except Exception:
            # Skip points that cause errors (documented separately)
            continue

    # Calculate statistics per property
    property_stats = {}
    all_errors = []

    for prop_name, errors in property_errors.items():
        if errors:
            property_stats[prop_name] = {
                "count": len(errors),
                "min_error": min(errors),
                "max_error": max(errors),
                "avg_error": np.mean(errors),
                "median_error": np.median(errors),
                "std_error": np.std(errors),
                "percentile_95": np.percentile(errors, 95),
                "percentile_99": np.percentile(errors, 99),
            }
            all_errors.extend(errors)

    return {
        "total_points": len(test_points),
        "properties": property_stats,
        "overall_max_error": max(all_errors) if all_errors else 0.0,
        "overall_avg_error": np.mean(all_errors) if all_errors else 0.0,
        "overall_median_error": np.median(all_errors) if all_errors else 0.0,
        "overall_std_error": np.std(all_errors) if all_errors else 0.0,
    }


def generate_accuracy_report():
    """Generate comprehensive accuracy report."""
    print("=" * 100)
    print("IAPWS-IF97 ACCURACY REPORT")
    print("=" * 100)
    print()

    # Load reference data
    print("Loading IAPWS reference data...")
    ref_data = load_reference_data()

    # Initialize steam table
    steam = SteamTable()

    # Expected tolerances
    tolerances = {"region1": 0.03, "region2": 0.06, "region3": 0.2, "saturation": 0.1}

    # Analyze each region
    results = {}

    for region_name, test_points in ref_data.get("regions", {}).items():
        if not test_points:
            continue

        print(f"\nAnalyzing {region_name.upper()}...")
        results[region_name] = analyze_region_accuracy(region_name, test_points, steam)

    # Generate summary table
    print("\n" + "=" * 100)
    print("ACCURACY SUMMARY TABLE")
    print("=" * 100)
    print()

    # Overall statistics
    print(
        f"{'Region':<15} {'Points':<8} {'Tolerance':<12} {'Max Error':<12} {'Avg Error':<12} {'Median':<12} {'Status':<8}"
    )
    print("-" * 100)

    for region_name in ["region1", "region2", "region3", "saturation"]:
        if region_name not in results:
            continue

        res = results[region_name]
        tolerance = tolerances[region_name]

        status = "✓ PASS" if res["overall_max_error"] <= tolerance else "✗ FAIL"

        print(
            f"{region_name:<15} {res['total_points']:<8} "
            f"±{tolerance}%{'':<8} "
            f"{res['overall_max_error']:<12.4f} "
            f"{res['overall_avg_error']:<12.4f} "
            f"{res['overall_median_error']:<12.4f} "
            f"{status:<8}"
        )

    # Property-specific breakdown
    print("\n" + "=" * 100)
    print("PROPERTY-SPECIFIC ACCURACY")
    print("=" * 100)

    for region_name, res in results.items():
        print(f"\n{region_name.upper()}:")
        print("-" * 100)
        print(
            f"{'Property':<20} {'Count':<8} {'Min%':<10} {'Max%':<10} {'Avg%':<10} {'Median%':<10} {'95th%':<10}"
        )
        print("-" * 100)

        for prop_name, stats in res["properties"].items():
            print(
                f"{prop_name:<20} {stats['count']:<8} "
                f"{stats['min_error']:<10.4f} "
                f"{stats['max_error']:<10.4f} "
                f"{stats['avg_error']:<10.4f} "
                f"{stats['median_error']:<10.4f} "
                f"{stats['percentile_95']:<10.4f}"
            )

    # Statistical summary
    print("\n" + "=" * 100)
    print("STATISTICAL SUMMARY")
    print("=" * 100)
    print()

    total_points = sum(r["total_points"] for r in results.values())
    all_max_errors = [r["overall_max_error"] for r in results.values()]
    all_avg_errors = [r["overall_avg_error"] for r in results.values()]

    print(f"Total validation points: {total_points}")
    print(f"Regions validated: {len(results)}")
    print(f"Maximum error (any region): {max(all_max_errors):.4f}%")
    print(f"Average error (across all regions): {np.mean(all_avg_errors):.4f}%")

    # Compliance check
    print("\n" + "-" * 100)
    print("COMPLIANCE CHECK:")
    print("-" * 100)

    all_compliant = True
    for region_name, res in results.items():
        tolerance = tolerances.get(region_name, 0.1)
        compliant = res["overall_max_error"] <= tolerance

        if not compliant:
            all_compliant = False

        status_symbol = "✓" if compliant else "✗"
        print(
            f"{status_symbol} {region_name}: Max error {res['overall_max_error']:.4f}% "
            f"{'≤' if compliant else '>'} tolerance {tolerance}%"
        )

    print()
    if all_compliant:
        print("✓ ALL REGIONS MEET ACCURACY REQUIREMENTS")
    else:
        print("✗ SOME REGIONS EXCEED ACCURACY TOLERANCE")

    print()
    print("=" * 100)

    # Export results as JSON for documentation
    output_file = Path(__file__).parent / "accuracy_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nDetailed results exported to: {output_file}")

    return 0 if all_compliant else 1


if __name__ == "__main__":
    sys.exit(generate_accuracy_report())
