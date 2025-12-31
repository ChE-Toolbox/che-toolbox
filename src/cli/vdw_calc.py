"""
Command-line interface for Van der Waals EOS calculations.

Provides commands for calculating molar volumes, compressibility factors,
and cross-model comparisons with other EOS models.
"""

import argparse
import json
import logging
import sys
from typing import Any

from src.compounds.database import CompoundDatabase
from src.eos import VanDerWaalsEOS, compare_compressibility_factors

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
    def format_text_volume(
        compound_name: str,
        temperature: float,
        pressure: float,
        volume: float,
    ) -> str:
        """Format molar volume output as text."""
        lines = [
            f"Compound: {compound_name}",
            f"Temperature: {temperature:.2f} K",
            f"Pressure: {pressure:.2f} bar",
            f"Molar Volume: {volume:.6e} m³/mol",
        ]
        return "\n".join(lines)

    @staticmethod
    def format_text_z_factor(
        compound_name: str,
        temperature: float,
        pressure: float,
        z_factor: float,
    ) -> str:
        """Format Z factor output as text."""
        lines = [
            f"Compound: {compound_name}",
            f"Temperature: {temperature:.2f} K",
            f"Pressure: {pressure:.2f} bar",
            f"Z factor (VDW): {z_factor:.6g}",
        ]
        return "\n".join(lines)

    @staticmethod
    def format_text_comparison(
        compound_name: str,
        temperature: float,
        pressure: float,
        ideal_z: float,
        vdw_z: float,
        pr_z: float,
    ) -> str:
        """Format cross-model comparison as text."""
        lines = [
            f"Compound: {compound_name}",
            f"Temperature: {temperature:.2f} K",
            f"Pressure: {pressure:.2f} bar",
            "",
            "Compressibility Factors:",
            f"  Ideal Gas:      {ideal_z:.6g}",
            f"  Van der Waals:  {vdw_z:.6g}",
            f"  Peng-Robinson:  {pr_z:.6g}",
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
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for vdw-calc command."""
    parser = argparse.ArgumentParser(
        prog="vdw-calc",
        description="Van der Waals EOS thermodynamic calculations",
    )

    parser.add_argument(
        "--version", action="version", version="%(prog)s 1.0.0"
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # volume command
    volume_parser = subparsers.add_parser(
        "volume", help="Calculate molar volume"
    )
    volume_parser.add_argument("compound", help="Compound name")
    volume_parser.add_argument(
        "--temperature", "-T", type=float, required=True, help="Temperature in K"
    )
    volume_parser.add_argument(
        "--pressure", "-P", type=float, required=True, help="Pressure in bar"
    )
    add_global_options(volume_parser)

    # z-factor command
    z_factor_parser = subparsers.add_parser(
        "z-factor", help="Calculate compressibility factor"
    )
    z_factor_parser.add_argument("compound", help="Compound name")
    z_factor_parser.add_argument(
        "--temperature", "-T", type=float, required=True, help="Temperature in K"
    )
    z_factor_parser.add_argument(
        "--pressure", "-P", type=float, required=True, help="Pressure in bar"
    )
    add_global_options(z_factor_parser)

    # compare command
    compare_parser = subparsers.add_parser(
        "compare", help="Compare with other EOS models"
    )
    compare_parser.add_argument("compound", help="Compound name")
    compare_parser.add_argument(
        "--temperature", "-T", type=float, required=True, help="Temperature in K"
    )
    compare_parser.add_argument(
        "--pressure", "-P", type=float, required=True, help="Pressure in bar"
    )
    add_global_options(compare_parser)

    # list-compounds command
    list_parser = subparsers.add_parser("list-compounds", help="List available compounds")
    add_global_options(list_parser)

    return parser


def handle_volume(args: argparse.Namespace) -> int:
    """Handle volume command."""
    try:
        db = CompoundDatabase()
        compound = db.get(args.compound)
        if compound is None:
            raise ValueError(f"Compound not found: {args.compound}")

        # Convert pressure from bar to Pa for calculations
        pressure_pa = args.pressure * 100000.0

        eos = VanDerWaalsEOS()
        volume = eos.calculate_volume(compound.tc, compound.pc, args.temperature, pressure_pa)

        if args.output_format == "json":
            output = {
                "compound": args.compound,
                "temperature": CLIFormatter.format_quantity(args.temperature, "K"),
                "pressure": CLIFormatter.format_quantity(args.pressure, "bar"),
                "molar_volume": CLIFormatter.format_quantity(volume, "m³/mol"),
            }
            print(json.dumps(output, indent=2))
        else:
            text = CLIFormatter.format_text_volume(
                args.compound,
                args.temperature,
                args.pressure,
                volume,
            )
            print(text)

        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


def handle_z_factor(args: argparse.Namespace) -> int:
    """Handle z-factor command."""
    try:
        db = CompoundDatabase()
        compound = db.get(args.compound)
        if compound is None:
            raise ValueError(f"Compound not found: {args.compound}")

        # Convert pressure from bar to Pa for calculations
        pressure_pa = args.pressure * 100000.0

        eos = VanDerWaalsEOS()
        volume = eos.calculate_volume(compound.tc, compound.pc, args.temperature, pressure_pa)
        z_factor = VanDerWaalsEOS.calculate_Z(pressure_pa, args.temperature, volume)

        if args.output_format == "json":
            output = {
                "compound": args.compound,
                "temperature": CLIFormatter.format_quantity(args.temperature, "K"),
                "pressure": CLIFormatter.format_quantity(args.pressure, "bar"),
                "z_factor": round(z_factor, 6),
            }
            print(json.dumps(output, indent=2))
        else:
            text = CLIFormatter.format_text_z_factor(
                args.compound,
                args.temperature,
                args.pressure,
                z_factor,
            )
            print(text)

        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


def handle_compare(args: argparse.Namespace) -> int:
    """Handle compare command."""
    try:
        db = CompoundDatabase()
        compound = db.get(args.compound)
        if compound is None:
            raise ValueError(f"Compound not found: {args.compound}")

        # Convert pressure from bar to Pa for calculations
        pressure_pa = args.pressure * 100000.0

        # Get comparison results
        results = compare_compressibility_factors(compound, args.temperature, pressure_pa)

        if args.output_format == "json":
            output = {
                "compound": args.compound,
                "temperature": CLIFormatter.format_quantity(args.temperature, "K"),
                "pressure": CLIFormatter.format_quantity(args.pressure, "bar"),
                "z_factors": {
                    "ideal_gas": round(results['ideal_Z'], 6),
                    "van_der_waals": round(results['vdw_Z'], 6),
                    "peng_robinson": round(results['pr_Z'], 6),
                },
            }
            print(json.dumps(output, indent=2))
        else:
            text = CLIFormatter.format_text_comparison(
                args.compound,
                args.temperature,
                args.pressure,
                results['ideal_Z'],
                results['vdw_Z'],
                results['pr_Z'],
            )
            print(text)

        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
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
                        "critical_pressure": CLIFormatter.format_quantity(
                            c.pc / 100000.0, "bar"
                        ),
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
    if hasattr(args, 'verbose') and args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Dispatch to command handler
    if args.command == "volume":
        return handle_volume(args)
    elif args.command == "z-factor":
        return handle_z_factor(args)
    elif args.command == "compare":
        return handle_compare(args)
    elif args.command == "list-compounds":
        return handle_list_compounds(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
