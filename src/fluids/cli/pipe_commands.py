"""CLI commands for pipe flow calculations."""

import argparse
import json
import sys
from typing import Any

from fluids.pipe import (
    calculate_friction_factor,
    calculate_pressure_drop,
    calculate_reynolds,
)


def format_output(result: dict[str, Any], format: str, verbosity: str) -> str:
    """
    Format calculation result for output.

    Args:
        result: Result dictionary from calculation
        format: Output format ('json' or 'text')
        verbosity: Verbosity level ('minimal', 'standard', or 'detailed')

    Returns:
        Formatted output string
    """
    if format == "json":
        return json.dumps(result, indent=2)

    # Text format
    if verbosity == "minimal":
        # Just the key result
        if "reynolds_number" in result:
            regime = result.get("flow_regime", "unknown")
            return f"Re = {result['reynolds_number']:.2f} ({regime})"
        elif "friction_factor" in result:
            return f"f = {result['friction_factor']:.6f}"
        elif "pressure_drop" in result:
            unit = result.get("unit", "Pa")
            return f"ΔP = {result['pressure_drop']:.2f} {unit}"
        else:
            return str(result.get("value", result))

    elif verbosity == "standard":
        # Intermediate values and key results
        lines = []
        if "reynolds_number" in result:
            lines.append(f"Reynolds Number: {result['reynolds_number']:.2f}")
            lines.append(f"Flow Regime: {result['flow_regime']}")
        elif "friction_factor" in result:
            lines.append(f"Friction Factor: {result['friction_factor']:.6f}")
            if "method_used" in result:
                lines.append(f"Method: {result['method_used']}")
        elif "pressure_drop" in result:
            unit = result.get("unit", "Pa")
            lines.append(f"Pressure Drop: {result['pressure_drop']:.2f} {unit}")

        if result.get("warnings"):
            lines.append("\nWarnings:")
            for warning in result["warnings"]:
                lines.append(f"  - {warning}")

        return "\n".join(lines)

    else:  # detailed
        # Full information including formulas
        lines = []
        for key, value in result.items():
            if key == "warnings" and value:
                lines.append("\nWarnings:")
                for warning in value:
                    lines.append(f"  - {warning}")
            elif isinstance(value, dict):
                lines.append(f"\n{key}:")
                for subkey, subvalue in value.items():
                    lines.append(f"  {subkey}: {subvalue}")
            elif isinstance(value, (list, tuple)):
                if value:
                    lines.append(f"{key}: {value}")
            else:
                lines.append(f"{key}: {value}")

        return "\n".join(lines)


def cmd_reynolds(args: argparse.Namespace) -> int:
    """Handle reynolds number calculation command."""
    try:
        result = calculate_reynolds(
            density=args.density,
            velocity=args.velocity,
            diameter=args.diameter,
            viscosity=args.viscosity,
            _unit_system=args.unit_system,
        )
        output = format_output(result, args.output_format, args.verbosity)
        print(output)
        return 0
    except Exception as e:
        print(f"Error calculating Reynolds number: {e}", file=sys.stderr)
        return 1


def cmd_friction(args: argparse.Namespace) -> int:
    """Handle friction factor calculation command."""
    try:
        result = calculate_friction_factor(
            reynolds=args.reynolds,
            roughness=args.roughness,
            diameter=args.diameter,
        )
        output = format_output(result, args.output_format, args.verbosity)
        print(output)
        return 0
    except Exception as e:
        print(f"Error calculating friction factor: {e}", file=sys.stderr)
        return 1


def cmd_pressure_drop(args: argparse.Namespace) -> int:
    """Handle pressure drop calculation command."""
    try:
        result = calculate_pressure_drop(
            friction_factor=args.friction,
            length=args.length,
            diameter=args.diameter,
            velocity=args.velocity,
            density=args.density,
            unit_system=args.unit_system,
        )
        output = format_output(result, args.output_format, args.verbosity)
        print(output)
        return 0
    except Exception as e:
        print(f"Error calculating pressure drop: {e}", file=sys.stderr)
        return 1


def register_commands(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """
    Register pipe-related commands.

    Args:
        subparsers: Subparsers object from main parser
    """
    # Create pipe command group
    pipe_parser = subparsers.add_parser(
        "pipe",
        help="Pipe flow calculations",
        description="Calculate Reynolds number, friction factor, and pressure drop",
    )

    pipe_subparsers = pipe_parser.add_subparsers(
        dest="pipe_command",
        help="Pipe calculation type",
        required=True,
    )

    # Reynolds number command
    reynolds_parser = pipe_subparsers.add_parser(
        "reynolds",
        help="Calculate Reynolds number",
        description="Calculate Reynolds number and determine flow regime",
    )
    reynolds_parser.add_argument(
        "--density", type=float, required=True, help="Fluid density (kg/m³ or lb/ft³)"
    )
    reynolds_parser.add_argument(
        "--velocity", type=float, required=True, help="Flow velocity (m/s or ft/s)"
    )
    reynolds_parser.add_argument(
        "--diameter", type=float, required=True, help="Pipe diameter (m or ft)"
    )
    reynolds_parser.add_argument(
        "--viscosity",
        type=float,
        required=True,
        help="Dynamic viscosity (Pa·s or lb/(ft·s))",
    )
    reynolds_parser.add_argument(
        "--unit-system",
        choices=["SI", "US"],
        default="SI",
        help="Unit system (default: SI)",
    )
    reynolds_parser.add_argument(
        "--output-format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)",
    )
    reynolds_parser.add_argument(
        "--verbosity",
        choices=["minimal", "standard", "detailed"],
        default="standard",
        help="Output verbosity (default: standard)",
    )
    reynolds_parser.set_defaults(func=cmd_reynolds)

    # Friction factor command
    friction_parser = pipe_subparsers.add_parser(
        "friction",
        help="Calculate friction factor",
        description="Calculate Darcy friction factor for pipe flow",
    )
    friction_parser.add_argument(
        "--reynolds", type=float, required=True, help="Reynolds number"
    )
    friction_parser.add_argument(
        "--roughness",
        type=float,
        required=True,
        help="Absolute pipe roughness (m or ft)",
    )
    friction_parser.add_argument(
        "--diameter", type=float, required=True, help="Pipe diameter (m or ft)"
    )
    friction_parser.add_argument(
        "--output-format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)",
    )
    friction_parser.add_argument(
        "--verbosity",
        choices=["minimal", "standard", "detailed"],
        default="standard",
        help="Output verbosity (default: standard)",
    )
    friction_parser.set_defaults(func=cmd_friction)

    # Pressure drop command
    pressure_parser = pipe_subparsers.add_parser(
        "pressure-drop",
        help="Calculate pressure drop",
        description="Calculate Darcy-Weisbach pressure drop in pipe",
    )
    pressure_parser.add_argument(
        "--friction", type=float, required=True, help="Darcy friction factor"
    )
    pressure_parser.add_argument(
        "--length", type=float, required=True, help="Pipe length (m or ft)"
    )
    pressure_parser.add_argument(
        "--diameter", type=float, required=True, help="Pipe diameter (m or ft)"
    )
    pressure_parser.add_argument(
        "--velocity", type=float, required=True, help="Flow velocity (m/s or ft/s)"
    )
    pressure_parser.add_argument(
        "--density", type=float, required=True, help="Fluid density (kg/m³ or lb/ft³)"
    )
    pressure_parser.add_argument(
        "--unit-system",
        choices=["SI", "US"],
        default="SI",
        help="Unit system (default: SI)",
    )
    pressure_parser.add_argument(
        "--output-format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)",
    )
    pressure_parser.add_argument(
        "--verbosity",
        choices=["minimal", "standard", "detailed"],
        default="standard",
        help="Output verbosity (default: standard)",
    )
    pressure_parser.set_defaults(func=cmd_pressure_drop)
