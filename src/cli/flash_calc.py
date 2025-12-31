"""
Command-line interface for PT Flash calculations.

Provides commands for performing vapor-liquid equilibrium calculations
using the Rachford-Rice flash algorithm with Peng-Robinson EOS.
"""

import argparse
import json
import logging
import sys
from typing import Any, cast

import numpy as np

from src.compounds.database import CompoundDatabase
from src.eos import FlashConvergence, FlashPT

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


class CLIFormatter:
    """Formats output for CLI commands."""

    @staticmethod
    def format_quantity(value: float, unit: str) -> dict[str, Any]:
        """Format a quantity with its unit."""
        return {"value": round(value, 6), "unit": unit}

    @staticmethod
    def format_text_flash(
        comp1_name: str,
        comp2_name: str,
        temperature: float,
        pressure: float,
        z1: float,
        z2: float,
        L: float,
        V: float,
        x: np.ndarray,
        y: np.ndarray,
        convergence: FlashConvergence,
        iterations: int,
    ) -> str:
        """Format flash calculation output as text."""
        lines = [
            "PT Flash Calculation Results",
            "=" * 50,
            "",
            "Conditions:",
            f"  Temperature: {temperature:.2f} K",
            f"  Pressure: {pressure:.2f} bar",
            "",
            "Feed Composition:",
            f"  {comp1_name}: {z1:.4f}",
            f"  {comp2_name}: {z2:.4f}",
            "",
            "Results:",
            f"  Convergence: {convergence.value}",
            f"  Iterations: {iterations}",
            "",
            f"  Liquid Fraction (L): {L:.6f}",
            f"  Vapor Fraction (V): {V:.6f}",
            "",
            "Liquid Composition (x):",
            f"  {comp1_name}: {x[0]:.6f}",
            f"  {comp2_name}: {x[1]:.6f}",
            "",
            "Vapor Composition (y):",
            f"  {comp1_name}: {y[0]:.6f}",
            f"  {comp2_name}: {y[1]:.6f}",
        ]
        return "\n".join(lines)


def add_global_options(subparser: argparse.ArgumentParser) -> None:
    """Add global options to a subparser."""
    subparser.add_argument(
        "--output-format",
        "-f",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    subparser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for flash-calc command."""
    parser = argparse.ArgumentParser(
        prog="flash-calc",
        description="PT Flash vapor-liquid equilibrium calculations",
    )

    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # calculate command
    calc_parser = subparsers.add_parser("calculate", help="Calculate vapor-liquid equilibrium")
    calc_parser.add_argument("compound1", help="First compound name")
    calc_parser.add_argument("compound2", help="Second compound name")
    calc_parser.add_argument(
        "--temperature", "-T", type=float, required=True, help="Temperature in K"
    )
    calc_parser.add_argument("--pressure", "-P", type=float, required=True, help="Pressure in bar")
    calc_parser.add_argument(
        "--z1", type=float, required=True, help="Mole fraction of first compound (0-1)"
    )
    calc_parser.add_argument(
        "--z2", type=float, required=True, help="Mole fraction of second compound (0-1)"
    )
    calc_parser.add_argument(
        "--max-iter", type=int, default=50, help="Maximum iterations (default: 50)"
    )
    calc_parser.add_argument(
        "--tolerance", type=float, default=1e-6, help="Convergence tolerance (default: 1e-6)"
    )
    add_global_options(calc_parser)

    # validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate flash calculations against reference data"
    )
    validate_parser.add_argument(
        "--test-case",
        choices=["ethane-propane", "methane-propane", "all"],
        default="all",
        help="Test case to validate (default: all)",
    )
    add_global_options(validate_parser)

    return parser


def handle_calculate(args: argparse.Namespace) -> int:
    """Handle calculate command."""
    try:
        # Validate mole fractions
        if not (0 <= args.z1 <= 1 and 0 <= args.z2 <= 1):
            raise ValueError("Mole fractions must be between 0 and 1")

        total_z = args.z1 + args.z2
        if not np.isclose(total_z, 1.0, atol=1e-6):
            raise ValueError(f"Mole fractions must sum to 1.0 (got {total_z:.6f})")

        # Get compounds from database
        db = CompoundDatabase()
        comp1 = db.get(args.compound1)
        comp2 = db.get(args.compound2)

        if comp1 is None:
            raise ValueError(f"Compound not found: {args.compound1}")
        if comp2 is None:
            raise ValueError(f"Compound not found: {args.compound2}")

        # Prepare inputs
        z = np.array([args.z1, args.z2])
        tc = np.array([comp1.tc, comp2.tc])
        pc = np.array([comp1.pc, comp2.pc])

        # Convert pressure from bar to Pa
        pressure_pa = args.pressure * 100000.0

        # Run flash calculation
        flash = FlashPT()
        result = flash.calculate(
            feed_composition=z,
            temperature=args.temperature,
            pressure=pressure_pa,
            critical_temperatures=tc,
            critical_pressures=pc,
            tolerance=args.tolerance,
            max_iterations=args.max_iter,
        )

        if args.output_format == "json":
            output = {
                "conditions": {
                    "temperature": CLIFormatter.format_quantity(args.temperature, "K"),
                    "pressure": CLIFormatter.format_quantity(args.pressure, "bar"),
                },
                "feed": {
                    args.compound1: args.z1,
                    args.compound2: args.z2,
                },
                "results": {
                    "convergence": result.convergence.value,
                    "iterations": result.iterations,
                    "liquid_fraction": round(result.L, 6),
                    "vapor_fraction": round(result.V, 6),
                    "liquid_composition": {
                        args.compound1: round(result.x[0], 6),
                        args.compound2: round(result.x[1], 6),
                    },
                    "vapor_composition": {
                        args.compound1: round(result.y[0], 6),
                        args.compound2: round(result.y[1], 6),
                    },
                },
            }
            print(json.dumps(output, indent=2))
        else:
            text = CLIFormatter.format_text_flash(
                args.compound1,
                args.compound2,
                args.temperature,
                args.pressure,
                args.z1,
                args.z2,
                result.L,
                result.V,
                result.x,
                result.y,
                result.convergence,
                result.iterations,
            )
            print(text)

        # Return non-zero if flash didn't converge
        if result.convergence != FlashConvergence.SUCCESS:
            return 3

        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


def handle_validate(args: argparse.Namespace) -> int:
    """Handle validate command."""
    try:
        # Reference test cases from NIST data
        test_cases = {
            "ethane-propane": {
                "comp1": "ethane",
                "comp2": "propane",
                "T": 300.0,
                "P": 2e6,  # Pa
                "z": np.array([0.60, 0.40]),
                "expected_L": 0.424,
                "expected_V": 0.576,
            },
            "methane-propane": {
                "comp1": "methane",
                "comp2": "propane",
                "T": 280.0,
                "P": 3e6,  # Pa
                "z": np.array([0.55, 0.45]),
                "expected_L": 0.302,
                "expected_V": 0.698,
            },
        }

        # Select test cases
        if args.test_case == "all":
            cases_to_run = list(test_cases.keys())
        else:
            cases_to_run = [args.test_case]

        db = CompoundDatabase()
        flash = FlashPT()

        all_passed = True
        results = {}

        for case_name in cases_to_run:
            case = test_cases[case_name]

            # Get compounds
            comp1 = db.get(str(case["comp1"]))
            comp2 = db.get(str(case["comp2"]))

            if comp1 is None or comp2 is None:
                print(f"Warning: Skipping {case_name} - compounds not found", file=sys.stderr)
                continue

            # Prepare inputs
            tc = np.array([comp1.tc, comp2.tc])
            pc = np.array([comp1.pc, comp2.pc])

            # Run flash
            result = flash.calculate(
                feed_composition=case["z"],  # type: ignore[arg-type]
                temperature=cast("float", case["T"]),
                pressure=cast("float", case["P"]),
                critical_temperatures=tc,
                critical_pressures=pc,
            )

            # Check results
            L_error = abs(result.L - cast("float", case["expected_L"]))
            V_error = abs(result.V - cast("float", case["expected_V"]))
            material_balance_error = float(
                np.max(np.abs((result.L * result.x + result.V * result.y) - np.array(case["z"])))
            )

            passed = (
                result.convergence == FlashConvergence.SUCCESS
                and L_error < 0.05  # ±5% tolerance
                and V_error < 0.05
                and material_balance_error < 1e-6
            )

            all_passed = all_passed and passed

            results[case_name] = {
                "passed": passed,
                "convergence": result.convergence.value,
                "L_calc": result.L,
                "L_ref": case["expected_L"],
                "L_error": L_error,
                "V_calc": result.V,
                "V_ref": case["expected_V"],
                "V_error": V_error,
                "material_balance_error": material_balance_error,
            }

        if args.output_format == "json":
            output = {
                "test_cases": results,
                "overall_passed": all_passed,
            }
            print(json.dumps(output, indent=2))
        else:
            print("Flash Validation Results")
            print("=" * 70)

            for case_name, res in results.items():
                status = "PASS" if res["passed"] else "FAIL"
                print(f"\nTest Case: {case_name} [{status}]")
                print(f"  Convergence: {res['convergence']}")
                print(
                    f"  L: {res['L_calc']:.4f} (ref: {res['L_ref']:.4f}, error: {res['L_error']:.4f})"
                )
                print(
                    f"  V: {res['V_calc']:.4f} (ref: {res['V_ref']:.4f}, error: {res['V_error']:.4f})"
                )
                print(f"  Material Balance Error: {res['material_balance_error']:.2e}")

            print(f"\nOverall: {'ALL PASSED' if all_passed else 'SOME FAILED'}")

        return 0 if all_passed else 4

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()

    if argv is None:
        argv = sys.argv[1:]

    # If no arguments provided, show help
    if not argv:
        parser.print_help()
        return 0

    args = parser.parse_args(argv)

    # Set logging level
    if hasattr(args, "verbose") and args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Dispatch to command handler
    if args.command == "calculate":
        return handle_calculate(args)
    elif args.command == "validate":
        return handle_validate(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
