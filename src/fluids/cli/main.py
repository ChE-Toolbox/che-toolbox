#!/usr/bin/env python3
"""
Main CLI router for fluids calculations.

Provides command-line interface for:
- Pipe flow analysis (reynolds, friction, pressure-drop)
- Pump sizing (head, power, npsh)
- Valve sizing (cv, flow-rate, sizing)
"""

import argparse
import sys
from typing import List, Optional


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="fluids",
        description="Fluid mechanics calculations for pipes, pumps, and valves",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )

    # Create subparsers for main commands
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available calculation modules",
        required=True,
    )

    # Import command modules
    from fluids.cli import pipe_commands, pump_commands, valve_commands

    # Register pipe commands
    pipe_commands.register_commands(subparsers)

    # Register pump commands
    pump_commands.register_commands(subparsers)

    # Register valve commands
    valve_commands.register_commands(subparsers)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    try:
        # The func attribute is set by each subcommand's handler
        return args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
