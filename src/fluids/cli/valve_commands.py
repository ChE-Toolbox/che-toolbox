"""CLI commands for valve sizing calculations."""

import argparse
import json
import sys
from typing import Any

from fluids.valve import (
    calculate_cv_required,
    calculate_flow_rate_through_valve,
    calculate_valve_sizing,
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
        value = result.get("value", 0)
        unit = result.get("unit", "")
        return f"{value:.2f} {unit}"

    elif verbosity == "standard":
        # Key results with warnings
        lines = []
        value = result.get("value", 0)
        unit = result.get("unit", "")
        lines.append(f"Result: {value:.2f} {unit}")

        if "formula_used" in result:
            lines.append(f"Formula: {result['formula_used']}")

        # For valve sizing results, show recommendations
        if result.get("recommended_sizes"):
            lines.append("\nRecommended Valve Sizes:")
            for size in result["recommended_sizes"][:3]:  # Show top 3
                lines.append(f"  - {size}")

        if result.get("warnings"):
            lines.append("\nWarnings:")
            for warning in result["warnings"]:
                lines.append(f"  - {warning}")

        return "\n".join(lines)

    else:  # detailed
        # Full information
        lines = []
        for key, value in result.items():
            if key == "warnings" and value:
                lines.append("\nWarnings:")
                for warning in value:
                    lines.append(f"  - {warning}")
            elif key == "recommended_sizes" and value:
                lines.append("\nRecommended Sizes:")
                for size in value:
                    lines.append(f"  - {size}")
            elif isinstance(value, dict):
                lines.append(f"\n{key}:")
                for subkey, subvalue in value.items():
                    lines.append(f"  {subkey}: {subvalue}")
            elif isinstance(value, (list, tuple)):
                if value and key not in ["warnings", "recommended_sizes"]:
                    lines.append(f"{key}: {value}")
            else:
                lines.append(f"{key}: {value}")

        return "\n".join(lines)


def cmd_cv(args: argparse.Namespace) -> int:
    """Handle Cv calculation command."""
    try:
        result = calculate_cv_required(
            flow_rate=args.flow_rate,
            pressure_drop=args.pressure_drop,
            fluid_gravity=args.specific_gravity,
            unit_system=args.unit_system,
        )
        output = format_output(result, args.output_format, args.verbosity)
        print(output)
        return 0
    except Exception as e:
        print(f"Error calculating Cv: {e}", file=sys.stderr)
        return 1


def cmd_flow_rate(args: argparse.Namespace) -> int:
    """Handle flow rate calculation command."""
    try:
        result = calculate_flow_rate_through_valve(
            cv=args.cv,
            pressure_drop=args.pressure_drop,
            fluid_gravity=args.specific_gravity,
            unit_system=args.unit_system,
        )
        output = format_output(result, args.output_format, args.verbosity)
        print(output)
        return 0
    except Exception as e:
        print(f"Error calculating flow rate: {e}", file=sys.stderr)
        return 1


def cmd_sizing(args: argparse.Namespace) -> int:
    """Handle valve sizing command."""
    try:
        # Convert valve type to CV options if needed
        valve_cv_opts: list[float] = args.valve_cv_options if hasattr(args, 'valve_cv_options') else [25, 50, 75, 100]

        result = calculate_valve_sizing(
            flow_rate=args.flow_rate,
            pressure_drop=args.pressure_drop,
            valve_cv_options=valve_cv_opts,
            fluid_gravity=args.specific_gravity,
            unit_system=args.unit_system,
        )
        output = format_output(result, args.output_format, args.verbosity)
        print(output)
        return 0
    except Exception as e:
        print(f"Error performing valve sizing: {e}", file=sys.stderr)
        return 1


def register_commands(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """
    Register valve-related commands.

    Args:
        subparsers: Subparsers object from main parser
    """
    # Create valve command group
    valve_parser = subparsers.add_parser(
        "valve",
        help="Valve sizing calculations",
        description="Calculate valve Cv, flow rate, and perform valve sizing",
    )

    valve_subparsers = valve_parser.add_subparsers(
        dest="valve_command",
        help="Valve calculation type",
        required=True,
    )

    # Cv calculation command
    cv_parser = valve_subparsers.add_parser(
        "cv",
        help="Calculate Cv required",
        description="Calculate valve flow coefficient (Cv) required for given flow and pressure drop",
    )
    cv_parser.add_argument(
        "--flow-rate",
        type=float,
        required=True,
        help="Flow rate (m³/h or gpm)",
    )
    cv_parser.add_argument(
        "--pressure-drop",
        type=float,
        required=True,
        help="Pressure drop (bar or psi)",
    )
    cv_parser.add_argument(
        "--specific-gravity",
        type=float,
        default=1.0,
        help="Fluid specific gravity (default: 1.0 for water)",
    )
    cv_parser.add_argument(
        "--unit-system",
        choices=["SI", "US"],
        default="SI",
        help="Unit system (default: SI)",
    )
    cv_parser.add_argument(
        "--output-format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)",
    )
    cv_parser.add_argument(
        "--verbosity",
        choices=["minimal", "standard", "detailed"],
        default="standard",
        help="Output verbosity (default: standard)",
    )
    cv_parser.set_defaults(func=cmd_cv)

    # Flow rate calculation command
    flow_parser = valve_subparsers.add_parser(
        "flow-rate",
        help="Calculate flow rate through valve",
        description="Calculate flow rate through valve given Cv and pressure drop",
    )
    flow_parser.add_argument(
        "--cv",
        type=float,
        required=True,
        help="Valve flow coefficient (Cv)",
    )
    flow_parser.add_argument(
        "--pressure-drop",
        type=float,
        required=True,
        help="Pressure drop (bar or psi)",
    )
    flow_parser.add_argument(
        "--specific-gravity",
        type=float,
        default=1.0,
        help="Fluid specific gravity (default: 1.0 for water)",
    )
    flow_parser.add_argument(
        "--unit-system",
        choices=["SI", "US"],
        default="SI",
        help="Unit system (default: SI)",
    )
    flow_parser.add_argument(
        "--output-format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)",
    )
    flow_parser.add_argument(
        "--verbosity",
        choices=["minimal", "standard", "detailed"],
        default="standard",
        help="Output verbosity (default: standard)",
    )
    flow_parser.set_defaults(func=cmd_flow_rate)

    # Valve sizing command
    sizing_parser = valve_subparsers.add_parser(
        "sizing",
        help="Perform valve sizing",
        description="Find appropriate valve sizes for given flow conditions",
    )
    sizing_parser.add_argument(
        "--flow-rate",
        type=float,
        required=True,
        help="Flow rate (m³/h or gpm)",
    )
    sizing_parser.add_argument(
        "--pressure-drop",
        type=float,
        required=True,
        help="Pressure drop (bar or psi)",
    )
    sizing_parser.add_argument(
        "--valve-type",
        type=str,
        required=True,
        help="Valve type (e.g., 'ball', 'globe', 'butterfly')",
    )
    sizing_parser.add_argument(
        "--specific-gravity",
        type=float,
        default=1.0,
        help="Fluid specific gravity (default: 1.0 for water)",
    )
    sizing_parser.add_argument(
        "--unit-system",
        choices=["SI", "US"],
        default="SI",
        help="Unit system (default: SI)",
    )
    sizing_parser.add_argument(
        "--output-format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)",
    )
    sizing_parser.add_argument(
        "--verbosity",
        choices=["minimal", "standard", "detailed"],
        default="standard",
        help="Output verbosity (default: standard)",
    )
    sizing_parser.set_defaults(func=cmd_sizing)
