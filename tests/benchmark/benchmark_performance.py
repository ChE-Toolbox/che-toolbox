"""Performance benchmarking for IAPWS-IF97 calculations.

Measures calculation time for each region and saturation properties.
Target: <10ms per calculation.
"""

import timeit
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from iapws_if97 import SteamTable, ureg


def benchmark_region(name, func, iterations=1000):
    """Benchmark a function and print results."""
    start = timeit.default_timer()
    for _ in range(iterations):
        func()
    elapsed = timeit.default_timer() - start
    avg_ms = (elapsed / iterations) * 1000
    return {"name": name, "iterations": iterations, "avg_ms": avg_ms}


def main():
    """Run full performance benchmark suite."""
    print("=" * 70)
    print("IAPWS-IF97 Performance Benchmark")
    print("=" * 70)
    print()

    steam = SteamTable()

    # Define test cases
    benchmarks = [
        ("Region 1 (liquid) @ 10 MPa, 500 K",
         lambda: steam.h_pt(10 * ureg.MPa, 500 * ureg.K)),
        
        ("Region 2 (steam) @ 0.1 MPa, 400 K",
         lambda: steam.h_pt(0.1 * ureg.MPa, 400 * ureg.K)),
        
        ("Region 3 (supercritical) @ 30 MPa, 700 K",
         lambda: steam.h_pt(30 * ureg.MPa, 700 * ureg.K)),
        
        ("Saturation T_sat @ 1 MPa",
         lambda: steam.T_sat(1 * ureg.MPa)),
        
        ("Saturation P_sat @ 373 K",
         lambda: steam.P_sat(373 * ureg.K)),
    ]

    results = []
    for name, func in benchmarks:
        result = benchmark_region(name, func, iterations=100)
        results.append(result)
        print(f"{result['name']:<50} {result['avg_ms']:>8.2f} ms")

    print()
    print("=" * 70)
    print("Performance Summary")
    print("=" * 70)

    # Check against targets
    targets = {
        "Region 1": 2.0,
        "Region 2": 3.0,
        "Region 3": 10.0,
        "Saturation": 5.0,
    }

    all_pass = True
    for result in results:
        for target_name, target_ms in targets.items():
            if target_name in result["name"]:
                status = "✓ PASS" if result["avg_ms"] <= target_ms else "✗ FAIL"
                if "FAIL" in status:
                    all_pass = False
                print(
                    f"{result['name']:<50} "
                    f"{result['avg_ms']:>8.2f} ms (target: {target_ms} ms) {status}"
                )
                break

    print()
    if all_pass:
        print("✓ All performance targets met!")
        return 0
    else:
        print("✗ Some performance targets not met. See above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
