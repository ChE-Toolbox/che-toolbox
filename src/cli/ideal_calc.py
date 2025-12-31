"""
Command-line interface for Ideal Gas EOS calculations.

Provides commands for calculating ideal gas volumes and demonstrating
ideal gas behavior as a reference baseline.
"""

import argparse
import json
import logging
import sys
from typing import Any

from src.eos import IdealGasEOS

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
        temperature: float,
        pressure: float,
        n_moles: float,
        volume: float,
    ) -> str:
        """Format ideal gas volume output as text."""
        lines = [
            "Ideal Gas Calculation",
            f"Temperature: {temperature:.2f} K",
            f"Pressure: {pressure:.2f} bar",
            f"Moles: {n_moles:.4f} mol",
            f"Volume: {volume:.6e} m³",
            f"Molar Volume: {volume/n_moles:.6e} m³/mol",
        ]
        return "\n".join(lines)

    @staticmethod
    def format_text_z_factor(
        temperature: float,
        pressure: float,
    ) -> str:
        """Format ideal gas Z factor output as text."""
        lines = [
            "Ideal Gas Calculation",
            f"Temperature: {temperature:.2f} K",
            f"Pressure: {pressure:.2f} bar",
            "Z factor: 1.000000 (ideal gas)",
        ]
        return "\n".join(lines)

    @staticmethod
    def format_text_state(
        temperature: float,
        pressure: float,
        n_moles: float,
        volume: float,
    ) -> str:
        """Format ideal gas state as text."""
        lines = [
            "Ideal Gas State",
            f"Temperature: {temperature:.2f} K",
            f"Pressure: {pressure:.2f} bar",
            f"Moles: {n_moles:.4f} mol",
            f"Volume: {volume:.6e} m³",
            "",
            "Properties:",
            f"  Molar Volume: {volume/n_moles:.6e} m³/mol",
            "  Z factor: 1.000000 (ideal)",
            "  Phase: vapor",
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
    """Create the argument parser for ideal-calc command."""
    parser = argparse.ArgumentParser(
        prog="ideal-calc",
        description="Ideal Gas EOS calculations",
    )

    parser.add_argument(
        "--version", action="version", version="%(prog)s 1.0.0"
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # volume command
    volume_parser = subparsers.add_parser(
        "volume", help="Calculate ideal gas volume"
    )
    volume_parser.add_argument(
        "--temperature", "-T", type=float, required=True, help="Temperature in K"
    )
    volume_parser.add_argument(
        "--pressure", "-P", type=float, required=True, help="Pressure in bar"
    )
    volume_parser.add_argument(
        "--moles", "-n", type=float, default=1.0, help="Number of moles (default: 1.0)"
    )
    add_global_options(volume_parser)

    # z-factor command
    z_factor_parser = subparsers.add_parser(
        "z-factor", help="Calculate compressibility factor (always 1.0)"
    )
    z_factor_parser.add_argument(
        "--temperature", "-T", type=float, required=True, help="Temperature in K"
    )
    z_factor_parser.add_argument(
        "--pressure", "-P", type=float, required=True, help="Pressure in bar"
    )
    add_global_options(z_factor_parser)

    # state command
    state_parser = subparsers.add_parser(
        "state", help="Calculate ideal gas state"
    )
    state_parser.add_argument(
        "--temperature", "-T", type=float, required=True, help="Temperature in K"
    )
    state_parser.add_argument(
        "--pressure", "-P", type=float, required=True, help="Pressure in bar"
    )
    state_parser.add_argument(
        "--moles", "-n", type=float, default=1.0, help="Number of moles (default: 1.0)"
    )
    add_global_options(state_parser)

    return parser


def handle_volume(args: argparse.Namespace) -> int:
    """Handle volume command."""
    try:
        # Convert pressure from bar to Pa for calculations
        pressure_pa = args.pressure * 100000.0

        eos = IdealGasEOS()
        volume = eos.calculate_volume(args.moles, args.temperature, pressure_pa)

        if args.output_format == "json":
            output = {
                "temperature": CLIFormatter.format_quantity(args.temperature, "K"),
                "pressure": CLIFormatter.format_quantity(args.pressure, "bar"),
                "moles": args.moles,
                "volume": CLIFormatter.format_quantity(volume, "m³"),
                "molar_volume": CLIFormatter.format_quantity(volume / args.moles, "m³/mol"),
            }
            print(json.dumps(output, indent=2))
        else:
            text = CLIFormatter.format_text_volume(
                args.temperature,
                args.pressure,
                args.moles,
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
        # For ideal gas, Z is always 1.0
        z_factor = 1.0

        if args.output_format == "json":
            output = {
                "temperature": CLIFormatter.format_quantity(args.temperature, "K"),
                "pressure": CLIFormatter.format_quantity(args.pressure, "bar"),
                "z_factor": z_factor,
                "note": "Ideal gas Z factor is always exactly 1.0 by definition",
            }
            print(json.dumps(output, indent=2))
        else:
            text = CLIFormatter.format_text_z_factor(
                args.temperature,
                args.pressure,
            )
            print(text)

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


def handle_state(args: argparse.Namespace) -> int:
    """Handle state command."""
    try:
        # Convert pressure from bar to Pa for calculations
        pressure_pa = args.pressure * 100000.0

        eos = IdealGasEOS()
        volume = eos.calculate_volume(args.moles, args.temperature, pressure_pa)
        z_factor = IdealGasEOS.calculate_Z(pressure_pa, args.temperature, volume)

        if args.output_format == "json":
            output = {
                "temperature": CLIFormatter.format_quantity(args.temperature, "K"),
                "pressure": CLIFormatter.format_quantity(args.pressure, "bar"),
                "moles": args.moles,
                "volume": CLIFormatter.format_quantity(volume, "m³"),
                "molar_volume": CLIFormatter.format_quantity(volume / args.moles, "m³/mol"),
                "z_factor": z_factor,
                "phase": "vapor",
            }
            print(json.dumps(output, indent=2))
        else:
            text = CLIFormatter.format_text_state(
                args.temperature,
                args.pressure,
                args.moles,
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
    elif args.command == "state":
        return handle_state(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
