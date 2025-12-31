"""
Comprehensive validation runner for all IAPWS-IF97 regions.

Loads IAPWS reference tables and reports accuracy statistics per region.
This script validates that the implementation meets the accuracy requirements:
- Region 1: ±0.03%
- Region 2: ±0.06%
- Region 3: ±0.2%
- Saturation: ±0.1%
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


def validate_region(
    region_name: str, test_points: list[dict], steam_table: SteamTable, tolerance_percent: float
) -> tuple[int, int, float, float, list[dict]]:
    """
    Validate a single region against reference data.

    Returns:
        (total_tests, passed_tests, max_error, avg_error, failures)
    """
    total = 0
    passed = 0
    errors = []
    failures = []

    for point in test_points:
        try:
            p_pa = point["pressure_Pa"]
            t_k = point["temperature_K"]

            # Properties to validate
            props_to_test = []

            if "enthalpy_kJ_per_kg" in point:
                h_computed = steam_table.h_pt(p_pa * ureg.Pa, t_k * ureg.K).to("kJ/kg").magnitude
                h_ref = point["enthalpy_kJ_per_kg"]
                h_error = calculate_relative_error(h_computed, h_ref)
                props_to_test.append(("enthalpy", h_error, h_computed, h_ref))

            if "entropy_kJ_per_kg_K" in point:
                s_computed = (
                    steam_table.s_pt(p_pa * ureg.Pa, t_k * ureg.K).to("kJ/(kg*K)").magnitude
                )
                s_ref = point["entropy_kJ_per_kg_K"]
                s_error = calculate_relative_error(s_computed, s_ref)
                props_to_test.append(("entropy", s_error, s_computed, s_ref))

            if "density_kg_per_m3" in point:
                rho_computed = (
                    steam_table.rho_pt(p_pa * ureg.Pa, t_k * ureg.K).to("kg/m^3").magnitude
                )
                rho_ref = point["density_kg_per_m3"]
                rho_error = calculate_relative_error(rho_computed, rho_ref)
                props_to_test.append(("density", rho_error, rho_computed, rho_ref))

            if "internal_energy_kJ_per_kg" in point:
                u_computed = steam_table.u_pt(p_pa * ureg.Pa, t_k * ureg.K).to("kJ/kg").magnitude
                u_ref = point["internal_energy_kJ_per_kg"]
                u_error = calculate_relative_error(u_computed, u_ref)
                props_to_test.append(("internal_energy", u_error, u_computed, u_ref))

            # Check each property
            for prop_name, error, computed, ref in props_to_test:
                total += 1
                errors.append(error)

                if error <= tolerance_percent:
                    passed += 1
                else:
                    failures.append(
                        {
                            "point_id": point.get(
                                "point_id", f"P={p_pa / 1e6:.2f}MPa,T={t_k:.2f}K"
                            ),
                            "property": prop_name,
                            "error_percent": error,
                            "computed": computed,
                            "reference": ref,
                            "pressure_Pa": p_pa,
                            "temperature_K": t_k,
                        }
                    )

        except Exception as e:
            total += 1
            failures.append(
                {
                    "point_id": point.get("point_id", f"P={p_pa / 1e6:.2f}MPa,T={t_k:.2f}K"),
                    "error": str(e),
                    "pressure_Pa": p_pa,
                    "temperature_K": t_k,
                }
            )

    max_error = max(errors) if errors else 0.0
    avg_error = np.mean(errors) if errors else 0.0

    return total, passed, max_error, avg_error, failures


def main():
    """Run comprehensive validation across all regions."""
    print("=" * 80)
    print("IAPWS-IF97 Comprehensive Validation Suite")
    print("=" * 80)
    print()

    # Load reference data
    print("Loading IAPWS reference data...")
    ref_data = load_reference_data()

    # Initialize steam table
    steam = SteamTable()

    # Validation tolerances per region
    tolerances = {
        "region1": 0.03,  # ±0.03%
        "region2": 0.06,  # ±0.06%
        "region3": 0.2,  # ±0.2%
        "saturation": 0.1,  # ±0.1%
    }

    # Validate each region
    results = {}
    all_passed = True

    for region_name, test_points in ref_data.get("regions", {}).items():
        if not test_points:
            continue

        tolerance = tolerances.get(region_name, 0.1)

        print(f"\nValidating {region_name.upper()}...")
        print(f"  Tolerance: ±{tolerance}%")
        print(f"  Test points: {len(test_points)}")

        total, passed, max_err, avg_err, failures = validate_region(
            region_name, test_points, steam, tolerance
        )

        results[region_name] = {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "max_error": max_err,
            "avg_error": avg_err,
            "failures": failures,
            "tolerance": tolerance,
        }

        pass_rate = (passed / total * 100) if total > 0 else 0
        status = "✓ PASS" if passed == total else "✗ FAIL"

        print(f"  Results: {passed}/{total} passed ({pass_rate:.1f}%)")
        print(f"  Max error: {max_err:.4f}%")
        print(f"  Avg error: {avg_err:.4f}%")
        print(f"  Status: {status}")

        if passed != total:
            all_passed = False
            print("\n  Top 5 failures:")
            sorted_failures = sorted(
                failures, key=lambda x: x.get("error_percent", float("inf")), reverse=True
            )
            for i, failure in enumerate(sorted_failures[:5], 1):
                if "error" in failure:
                    print(f"    {i}. {failure['point_id']}: {failure['error']}")
                else:
                    print(
                        f"    {i}. {failure['point_id']} - {failure['property']}: "
                        f"{failure['error_percent']:.4f}% error"
                    )

    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    total_all = sum(r["total"] for r in results.values())
    passed_all = sum(r["passed"] for r in results.values())
    overall_rate = (passed_all / total_all * 100) if total_all > 0 else 0

    print(f"\nOverall: {passed_all}/{total_all} tests passed ({overall_rate:.1f}%)")
    print(
        f"\nStatus: {'✓ ALL REGIONS VALIDATED' if all_passed else '✗ VALIDATION FAILURES DETECTED'}"
    )

    # Detailed results table
    print("\n" + "-" * 80)
    print(
        f"{'Region':<15} {'Total':<8} {'Passed':<8} {'Failed':<8} {'Pass%':<8} {'MaxErr%':<10} {'AvgErr%':<10}"
    )
    print("-" * 80)

    for region, res in results.items():
        pass_pct = (res["passed"] / res["total"] * 100) if res["total"] > 0 else 0
        print(
            f"{region:<15} {res['total']:<8} {res['passed']:<8} {res['failed']:<8} "
            f"{pass_pct:<8.1f} {res['max_error']:<10.4f} {res['avg_error']:<10.4f}"
        )

    print("-" * 80)

    # Return exit code
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
