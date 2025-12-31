"""
Command-line interface for Peng-Robinson EOS thermodynamic engine.

Provides commands for calculating compressibility factors, fugacity coefficients,
vapor pressures, and validating against NIST reference data.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

from src.compounds.database import CompoundDatabase
from src.eos.models import Mixture
from src.eos.peng_robinson import PengRobinsonEOS
from src.validation.nist_data import NISTDataLoader
from src.validation.validator import NISTValidation

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
    def format_text_z_factor(
        compound_name: str,
        temperature: float,
        pressure: float,
        phase: str,
        z_factor: float,
    ) -> str:
        """Format Z factor output as text."""
        lines = [
            f"Compound: {compound_name}",
            f"Temperature: {temperature:.2f} K",
            f"Pressure: {pressure:.2f} bar",
            f"Phase: {phase}",
            f"Z factor: {z_factor:.6g}",
        ]
        return "\n".join(lines)

    @staticmethod
    def format_text_fugacity(
        compound_name: str,
        temperature: float,
        pressure: float,
        phase: str,
        fugacity_coef: float,
        fugacity: float,
    ) -> str:
        """Format fugacity output as text."""
        lines = [
            f"Compound: {compound_name}",
            f"Temperature: {temperature:.2f} K",
            f"Pressure: {pressure:.2f} bar",
            f"Phase: {phase}",
            f"Fugacity coefficient: {fugacity_coef:.6g}",
            f"Fugacity: {fugacity:.2f} bar",
        ]
        return "\n".join(lines)

    @staticmethod
    def format_text_vapor_pressure(
        compound_name: str,
        temperature: float,
        critical_temp: float,
        vapor_pressure: float,
    ) -> str:
        """Format vapor pressure output as text."""
        lines = [
            f"Compound: {compound_name}",
            f"Temperature: {temperature:.2f} K",
            f"Critical temperature: {critical_temp:.2f} K",
            f"Vapor pressure: {vapor_pressure:.4f} bar",
        ]
        return "\n".join(lines)

    @staticmethod
    def format_text_state(
        compound_name: str,
        temperature: float,
        pressure: float,
        reduced_temp: float,
        reduced_pres: float,
        phase: str,
        z_factor: float,
        fugacity_coef: float,
        fugacity: float,
    ) -> str:
        """Format complete state output as text."""
        lines = [
            f"Compound: {compound_name}",
            f"Temperature: {temperature:.2f} K",
            f"Pressure: {pressure:.2f} bar",
            f"Reduced T: {reduced_temp:.3f}",
            f"Reduced P: {reduced_pres:.3f}",
            f"Phase: {phase}",
            "",
            "Properties:",
            f"  Z factor: {z_factor:.6g}",
            f"  Fugacity coefficient: {fugacity_coef:.6g}",
            f"  Fugacity: {fugacity:.2f} bar",
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
    subparser.add_argument(
        "--units-temp",
        choices=["K", "degC", "degF"],
        default="K",
        help="Temperature unit for output (default: K)",
    )
    subparser.add_argument(
        "--units-pressure",
        choices=["bar", "Pa", "kPa", "MPa", "psi", "atm"],
        default="bar",
        help="Pressure unit for output (default: bar)",
    )
    subparser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for pr-calc command."""
    parser = argparse.ArgumentParser(
        prog="pr-calc",
        description="Peng-Robinson EOS thermodynamic calculations",
    )

    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # z-factor command
    z_factor_parser = subparsers.add_parser("z-factor", help="Calculate compressibility factor")
    z_factor_parser.add_argument("compound", help="Compound name or mixture JSON path")
    z_factor_parser.add_argument(
        "--temperature", "-T", type=float, required=True, help="Temperature value"
    )
    z_factor_parser.add_argument(
        "--pressure", "-P", type=float, required=True, help="Pressure value"
    )
    z_factor_parser.add_argument("--temp-unit", default="K", help="Temperature unit (default: K)")
    z_factor_parser.add_argument(
        "--pressure-unit", default="bar", help="Pressure unit (default: bar)"
    )
    z_factor_parser.add_argument(
        "--phase",
        choices=["vapor", "liquid", "all"],
        default="all",
        help="Phase to return (default: all)",
    )
    add_global_options(z_factor_parser)

    # fugacity command
    fugacity_parser = subparsers.add_parser("fugacity", help="Calculate fugacity coefficient")
    fugacity_parser.add_argument("compound", help="Compound name or mixture JSON path")
    fugacity_parser.add_argument(
        "--temperature", "-T", type=float, required=True, help="Temperature value"
    )
    fugacity_parser.add_argument(
        "--pressure", "-P", type=float, required=True, help="Pressure value"
    )
    fugacity_parser.add_argument("--temp-unit", default="K", help="Temperature unit (default: K)")
    fugacity_parser.add_argument(
        "--pressure-unit", default="bar", help="Pressure unit (default: bar)"
    )
    fugacity_parser.add_argument(
        "--phase",
        choices=["vapor", "liquid", "all"],
        default="all",
        help="Phase to return (default: all)",
    )

    add_global_options(fugacity_parser)
    # vapor-pressure command
    vp_parser = subparsers.add_parser("vapor-pressure", help="Calculate vapor pressure")
    vp_parser.add_argument("compound", help="Pure compound name")
    vp_parser.add_argument(
        "--temperature", "-T", type=float, required=True, help="Temperature value"
    )
    vp_parser.add_argument("--temp-unit", default="K", help="Temperature unit (default: K)")

    add_global_options(vp_parser)
    # state command
    state_parser = subparsers.add_parser("state", help="Calculate complete state")
    state_parser.add_argument("compound", help="Compound name")
    state_parser.add_argument(
        "--temperature", "-T", type=float, required=True, help="Temperature value"
    )
    state_parser.add_argument("--pressure", "-P", type=float, required=True, help="Pressure value")
    state_parser.add_argument("--temp-unit", default="K", help="Temperature unit (default: K)")
    state_parser.add_argument("--pressure-unit", default="bar", help="Pressure unit (default: bar)")

    add_global_options(state_parser)
    # mixture command
    mixture_parser = subparsers.add_parser("mixture", help="Calculate mixture properties")
    mixture_parser.add_argument("mixture_file", help="Path to mixture JSON file")
    mixture_parser.add_argument(
        "--temperature", "-T", type=float, required=True, help="Temperature value"
    )
    mixture_parser.add_argument(
        "--pressure", "-P", type=float, required=True, help="Pressure value"
    )
    mixture_parser.add_argument("--temp-unit", default="K", help="Temperature unit (default: K)")
    mixture_parser.add_argument(
        "--pressure-unit", default="bar", help="Pressure unit (default: bar)"
    )

    add_global_options(mixture_parser)
    # validate command
    validate_parser = subparsers.add_parser("validate", help="Run NIST validation tests")
    validate_parser.add_argument(
        "compound", nargs="?", default=None, help="Specific compound to validate"
    )
    validate_parser.add_argument(
        "--property",
        choices=["z-factor", "fugacity", "vapor-pressure", "all"],
        default="all",
        help="Property to validate (default: all)",
    )
    validate_parser.add_argument("--report", help="Path to save detailed validation report")

    add_global_options(validate_parser)
    # list-compounds command
    list_parser = subparsers.add_parser("list-compounds", help="List available compounds")
    add_global_options(list_parser)

    return parser


def handle_z_factor(args: argparse.Namespace) -> int:
    """Handle z-factor command."""
    try:
        db = CompoundDatabase()
        compound = db.get(args.compound)
        if compound is None:
            raise ValueError(f"Compound not found: {args.compound}")

        # Convert pressure from bar to Pa for calculations
        pressure_pa = args.pressure * 100000.0

        eos = PengRobinsonEOS()
        state = eos.calculate_state(args.temperature, pressure_pa, compound)

        if args.output_format == "json":
            output = {
                "compound": args.compound,
                "temperature": CLIFormatter.format_quantity(args.temperature, "K"),
                "pressure": CLIFormatter.format_quantity(args.pressure, "bar"),
                "phase": state.phase.value if state.phase else "unknown",
                "z_factor": round(state.z_factor, 6) if state.z_factor is not None else None,
            }
            print(json.dumps(output, indent=2))
        else:
            phase_value = state.phase.value if state.phase else "unknown"
            z_value = state.z_factor if state.z_factor is not None else 0.0
            text = CLIFormatter.format_text_z_factor(
                args.compound,
                args.temperature,
                args.pressure,
                phase_value,
                z_value,
            )
            print(text)

        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


def handle_fugacity(args: argparse.Namespace) -> int:
    """Handle fugacity command."""
    try:
        db = CompoundDatabase()
        compound = db.get(args.compound)
        if compound is None:
            raise ValueError(f"Compound not found: {args.compound}")

        # Convert pressure from bar to Pa for calculations
        pressure_pa = args.pressure * 100000.0

        eos = PengRobinsonEOS()
        state = eos.calculate_state(args.temperature, pressure_pa, compound)

        fugacity_coef = eos.calculate_fugacity_coefficient(
            args.temperature, pressure_pa, compound, state.phase
        )
        # Fugacity in Pa
        fugacity_pa = fugacity_coef * pressure_pa
        # Convert to bar
        fugacity = fugacity_pa / 100000.0

        if args.output_format == "json":
            output = {
                "compound": args.compound,
                "temperature": CLIFormatter.format_quantity(args.temperature, "K"),
                "pressure": CLIFormatter.format_quantity(args.pressure, "bar"),
                "phase": state.phase.value if state.phase else "unknown",
                "fugacity_coefficient": round(fugacity_coef, 6),
                "fugacity": CLIFormatter.format_quantity(fugacity, "bar"),
            }
            print(json.dumps(output, indent=2))
        else:
            phase_value = state.phase.value if state.phase else "unknown"
            text = CLIFormatter.format_text_fugacity(
                args.compound,
                args.temperature,
                args.pressure,
                phase_value,
                fugacity_coef,
                fugacity,
            )
            print(text)

        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


def handle_vapor_pressure(args: argparse.Namespace) -> int:
    """Handle vapor-pressure command."""
    try:
        db = CompoundDatabase()
        compound = db.get(args.compound)
        if compound is None:
            raise ValueError(f"Compound not found: {args.compound}")

        eos = PengRobinsonEOS()
        vapor_pressure = eos.calculate_vapor_pressure(args.temperature, compound)

        # Convert pressure from Pa to bar
        vapor_pressure_bar = vapor_pressure / 100000.0

        if args.output_format == "json":
            output = {
                "compound": args.compound,
                "temperature": CLIFormatter.format_quantity(args.temperature, "K"),
                "critical_temperature": CLIFormatter.format_quantity(compound.tc, "K"),
                "vapor_pressure": CLIFormatter.format_quantity(vapor_pressure_bar, "bar"),
            }
            print(json.dumps(output, indent=2))
        else:
            text = CLIFormatter.format_text_vapor_pressure(
                args.compound, args.temperature, compound.tc, vapor_pressure_bar
            )
            print(text)

        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 3


def handle_state(args: argparse.Namespace) -> int:
    """Handle state command."""
    try:
        db = CompoundDatabase()
        compound = db.get(args.compound)
        if compound is None:
            raise ValueError(f"Compound not found: {args.compound}")

        # Convert pressure from bar to Pa for calculations
        pressure_pa = args.pressure * 100000.0

        eos = PengRobinsonEOS()
        state = eos.calculate_state(args.temperature, pressure_pa, compound)

        fugacity_coef = eos.calculate_fugacity_coefficient(
            args.temperature, pressure_pa, compound, state.phase
        )
        # Fugacity in Pa
        fugacity_pa = fugacity_coef * pressure_pa
        # Convert to bar
        fugacity = fugacity_pa / 100000.0

        reduced_temp = args.temperature / compound.tc
        # Pc is in Pa, convert to bar for comparison
        pc_bar = compound.pc / 100000.0
        reduced_pres = args.pressure / pc_bar

        if args.output_format == "json":
            output = {
                "compound": args.compound,
                "temperature": CLIFormatter.format_quantity(args.temperature, "K"),
                "pressure": CLIFormatter.format_quantity(args.pressure, "bar"),
                "reduced_temperature": round(reduced_temp, 3),
                "reduced_pressure": round(reduced_pres, 3),
                "phase": state.phase.value if state.phase else "unknown",
                "z_factor": round(state.z_factor, 6) if state.z_factor is not None else None,
                "fugacity_coefficient": round(fugacity_coef, 6),
                "fugacity": CLIFormatter.format_quantity(fugacity, "bar"),
            }
            print(json.dumps(output, indent=2))
        else:
            phase_value = state.phase.value if state.phase else "unknown"
            z_value = state.z_factor if state.z_factor is not None else 0.0
            text = CLIFormatter.format_text_state(
                args.compound,
                args.temperature,
                args.pressure,
                reduced_temp,
                reduced_pres,
                phase_value,
                z_value,
                fugacity_coef,
                fugacity,
            )
            print(text)

        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


def handle_mixture(args: argparse.Namespace) -> int:
    """Handle mixture command."""
    try:
        # Load mixture file
        mixture_path = Path(args.mixture_file)
        if not mixture_path.exists():
            raise FileNotFoundError(f"Mixture file not found: {args.mixture_file}")

        with open(mixture_path) as f:
            mixture_data = json.load(f)

        # Create mixture from JSON
        db = CompoundDatabase()
        component_names = []
        mole_fractions = []

        for comp in mixture_data["components"]:
            c = db.get(comp["name"])
            if c is None:
                raise ValueError(f"Compound not found: {comp['name']}")
            component_names.append(comp["name"])
            mole_fractions.append(comp["mole_fraction"])

        mixture = Mixture(compound_names=component_names, mole_fractions=mole_fractions)

        # Convert pressure from bar to Pa for calculations
        pressure_pa = args.pressure * 100000.0

        # Note: Mixture calculations not yet supported by PengRobinsonEOS
        # For now, use first component as approximation
        first_compound = db.get(component_names[0])
        if first_compound is None:
            raise ValueError(f"Compound not found: {component_names[0]}")

        # Calculate properties using first component
        eos = PengRobinsonEOS()
        z_factors = eos.calculate_z_factor(args.temperature, pressure_pa, first_compound)
        state = eos.calculate_state(args.temperature, pressure_pa, first_compound)

        # Use vapor phase Z factor (largest value)
        z_factor = z_factors[-1]

        if args.output_format == "json":
            output = {
                "mixture": mixture_data.get("name", "unknown"),
                "components": mixture_data["components"],
                "temperature": CLIFormatter.format_quantity(args.temperature, "K"),
                "pressure": CLIFormatter.format_quantity(args.pressure, "bar"),
                "phase": state.phase.value if state.phase else "unknown",
                "z_factor": round(z_factor, 6),
            }
            print(json.dumps(output, indent=2))
        else:
            print(f"Mixture: {mixture_data.get('name', 'unknown')}")
            print("Components:")
            for comp in mixture_data["components"]:
                print(f"  {comp['name']:<12} ({comp['mole_fraction'] * 100:.1f}%)")
            print(f"\nTemperature: {args.temperature:.2f} K")
            print(f"Pressure: {args.pressure:.2f} bar")
            print(f"Phase: {state.phase.value}")
            print("\nMixture Properties:")
            print(f"  Z factor: {z_factor:.6g}")

        return 0

    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


def handle_validate(args: argparse.Namespace) -> int:
    """Handle validate command."""
    try:
        validator = NISTValidation()
        nist_loader = NISTDataLoader()

        if args.compound:
            compounds = [args.compound]
        else:
            compounds = nist_loader.list_available_compounds()

        total_passed = 0
        total_tests = 0

        results: dict[str, dict[str, int | float]] = {}

        if args.output_format == "json":
            from typing import Any

            output: dict[str, Any] = {"validation_results": {}}

            for compound_name in compounds:
                try:
                    # Load NIST reference data for this compound
                    test_data = nist_loader.load_compound_data(compound_name)

                    compound_passed = 0
                    compound_total = 0

                    for test_case in test_data:
                        if (
                            "temperature" in test_case
                            and "pressure" in test_case
                            and "z_factor" in test_case
                        ):
                            passed, _deviation, _error = validator.validate_z_factor(
                                float(test_case["temperature"]),
                                float(test_case["pressure"]),
                                compound_name,
                                float(test_case["z_factor"]),
                            )
                            if passed:
                                compound_passed += 1
                            compound_total += 1

                    total_passed += compound_passed
                    total_tests += compound_total

                    output["validation_results"][compound_name] = {
                        "z_factor": {
                            "passed": compound_passed,
                            "total": compound_total,
                            "pass_rate": round(
                                compound_passed / compound_total if compound_total > 0 else 0, 3
                            ),
                        }
                    }
                except Exception:
                    output["validation_results"][compound_name] = {
                        "z_factor": {"passed": 0, "total": 0, "pass_rate": 0.0}
                    }

            output["validation_results"]["overall"] = {
                "passed": total_passed,
                "total": total_tests,
                "pass_rate": round(total_passed / total_tests if total_tests > 0 else 0, 3),
            }

            print(json.dumps(output, indent=2))
        else:
            print("NIST Validation Results")
            print("=" * 50)

            for compound_name in compounds:
                try:
                    # Load NIST reference data for this compound
                    test_data = nist_loader.load_compound_data(compound_name)

                    compound_passed = 0
                    compound_total = 0

                    for test_case in test_data:
                        if (
                            "temperature" in test_case
                            and "pressure" in test_case
                            and "z_factor" in test_case
                        ):
                            passed, _deviation, _error = validator.validate_z_factor(
                                float(test_case["temperature"]),
                                float(test_case["pressure"]),
                                compound_name,
                                float(test_case["z_factor"]),
                            )
                            if passed:
                                compound_passed += 1
                            compound_total += 1

                    total_passed += compound_passed
                    total_tests += compound_total

                    z_rate = (compound_passed / compound_total * 100) if compound_total > 0 else 0
                    print(f"\nCompound: {compound_name}")
                    print(
                        f"  Z factor: {compound_passed} / {compound_total} tests passed ({z_rate:.1f}%)"
                    )
                except Exception:
                    print(f"\nCompound: {compound_name}")
                    print("  Z factor: 0 / 0 tests passed (0.0%)")

            overall_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
            print(f"\nOverall: {total_passed} / {total_tests} tests passed ({overall_rate:.1f}%)")

        return 0 if total_passed == total_tests else 4

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


def handle_list_compounds(args: argparse.Namespace) -> int:
    """Handle list-compounds command."""
    try:
        db = CompoundDatabase()
        compound_names = db.list_compounds()

        if args.output_format == "json":
            compounds = [db.get(name) for name in compound_names]
            output = {
                "compounds": [
                    {
                        "name": c.name,
                        "cas_number": c.cas_number,
                        "molecular_weight": round(c.molecular_weight, 3),
                        "critical_temperature": CLIFormatter.format_quantity(c.tc, "K"),
                        "critical_pressure": CLIFormatter.format_quantity(c.pc / 100000.0, "bar"),
                        "acentric_factor": round(c.acentric_factor, 3),
                    }
                    for c in compounds
                    if c is not None
                ]
            }
            print(json.dumps(output, indent=2))
        else:
            print("Available Compounds")
            print("=" * 100)

            for name in compound_names:
                c = db.get(name)
                if c is not None:
                    pc_bar = c.pc / 100000.0
                    print(
                        f"{c.name:<15} ({c.cas_number:<12}) "
                        f"Tc={c.tc:>7.2f} K   Pc={pc_bar:>6.2f} bar   ω={c.acentric_factor:>6.3f}"
                    )

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


def main(argv: list | None = None) -> int:
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
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Dispatch to command handler
    if args.command == "z-factor":
        return handle_z_factor(args)
    elif args.command == "fugacity":
        return handle_fugacity(args)
    elif args.command == "vapor-pressure":
        return handle_vapor_pressure(args)
    elif args.command == "state":
        return handle_state(args)
    elif args.command == "mixture":
        return handle_mixture(args)
    elif args.command == "validate":
        return handle_validate(args)
    elif args.command == "list-compounds":
        return handle_list_compounds(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
