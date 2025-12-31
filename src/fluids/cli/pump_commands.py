"""CLI commands for pump sizing calculations."""

import argparse
import json
import sys
from typing import Any

from fluids.pump import (
    calculate_brake_power,
    calculate_hydraulic_power,
    calculate_npsh_available,
    calculate_npsh_required,
    calculate_total_head,
    check_cavitation_risk,
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


def cmd_head(args: argparse.Namespace) -> int:
    """Handle pump head calculation command."""
    try:
        result = calculate_total_head(
            elevation_change=args.elevation,
            pressure_drop=args.pressure_drop,
            velocity=args.velocity,
            fluid_density=args.density,
            unit_system=args.unit_system,
        )
        output = format_output(result, args.output_format, args.verbosity)
        print(output)
        return 0
    except Exception as e:
        print(f"Error calculating pump head: {e}", file=sys.stderr)
        return 1


def cmd_power(args: argparse.Namespace) -> int:
    """Handle pump power calculation command."""
    try:
        if args.efficiency is not None:
            # Calculate brake power (includes efficiency)
            result = calculate_brake_power(
                flow_rate=args.flow_rate,
                head=args.head,
                pump_efficiency=args.efficiency,
                fluid_density=args.density,
                unit_system=args.unit_system,
            )
        else:
            # Calculate hydraulic power (ideal)
            result = calculate_hydraulic_power(
                flow_rate=args.flow_rate,
                head=args.head,
                fluid_density=args.density,
                unit_system=args.unit_system,
            )
        output = format_output(result, args.output_format, args.verbosity)
        print(output)
        return 0
    except Exception as e:
        print(f"Error calculating pump power: {e}", file=sys.stderr)
        return 1


def cmd_npsh(args: argparse.Namespace) -> int:
    """Handle NPSH calculation command."""
    try:
        # Calculate NPSH available
        npsha_result = calculate_npsh_available(
            atmospheric_pressure=args.atmospheric_pressure,
            vapor_pressure=args.vapor_pressure,
            suction_head=args.suction_head,
            suction_losses=args.suction_losses,
            fluid_density=args.density,
            unit_system=args.unit_system,
        )

        # If pump type and flow rate provided, check cavitation risk
        if args.pump_type and args.flow_rate:
            try:
                npshr_result = calculate_npsh_required(
                    pump_design_point_flow=args.design_flow or args.flow_rate,
                    actual_flow=args.flow_rate,
                    npsh_required_at_design=1.0,
                )
                risk_result = check_cavitation_risk(
                    npsh_available=npsha_result["value"],
                    npsh_required=npshr_result["value"],
                )

                # Combine results
                combined_result = {
                    "npsh_available": npsha_result["value"],
                    "npsh_required": npshr_result["value"],
                    "margin": risk_result.get("margin", 0),
                    "risk_level": risk_result.get("risk_level", "unknown"),
                    "unit": npsha_result["unit"],
                    "warnings": npsha_result.get("warnings", []) + risk_result.get("warnings", []),
                }
                output = format_output(combined_result, args.output_format, args.verbosity)
            except Exception as e:
                # If NPSH required calculation fails, just show available
                print(
                    f"Warning: Could not calculate NPSH required: {e}",
                    file=sys.stderr,
                )
                output = format_output(npsha_result, args.output_format, args.verbosity)
        else:
            output = format_output(npsha_result, args.output_format, args.verbosity)

        print(output)
        return 0
    except Exception as e:
        print(f"Error calculating NPSH: {e}", file=sys.stderr)
        return 1


def register_commands(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """
    Register pump-related commands.

    Args:
        subparsers: Subparsers object from main parser
    """
    # Create pump command group
    pump_parser = subparsers.add_parser(
        "pump",
        help="Pump sizing calculations",
        description="Calculate pump head, power, and NPSH requirements",
    )

    pump_subparsers = pump_parser.add_subparsers(
        dest="pump_command",
        help="Pump calculation type",
        required=True,
    )

    # Head calculation command
    head_parser = pump_subparsers.add_parser(
        "head",
        help="Calculate pump head",
        description="Calculate total head required by pump",
    )
    head_parser.add_argument(
        "--elevation",
        type=float,
        required=True,
        help="Elevation change (m or ft)",
    )
    head_parser.add_argument(
        "--pressure-drop",
        type=float,
        required=True,
        help="System pressure drop (Pa or psi)",
    )
    head_parser.add_argument(
        "--velocity",
        type=float,
        required=True,
        help="Fluid velocity (m/s or ft/s)",
    )
    head_parser.add_argument(
        "--density",
        type=float,
        default=1000.0,
        help="Fluid density (kg/m³ or lb/ft³, default: 1000)",
    )
    head_parser.add_argument(
        "--unit-system",
        choices=["SI", "US"],
        default="SI",
        help="Unit system (default: SI)",
    )
    head_parser.add_argument(
        "--output-format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)",
    )
    head_parser.add_argument(
        "--verbosity",
        choices=["minimal", "standard", "detailed"],
        default="standard",
        help="Output verbosity (default: standard)",
    )
    head_parser.set_defaults(func=cmd_head)

    # Power calculation command
    power_parser = pump_subparsers.add_parser(
        "power",
        help="Calculate pump power",
        description="Calculate hydraulic or brake power required by pump",
    )
    power_parser.add_argument(
        "--flow-rate",
        type=float,
        required=True,
        help="Flow rate (m³/s or ft³/s)",
    )
    power_parser.add_argument(
        "--head",
        type=float,
        required=True,
        help="Total head (m or ft)",
    )
    power_parser.add_argument(
        "--efficiency",
        type=float,
        help="Pump efficiency (0-1), omit for hydraulic power",
    )
    power_parser.add_argument(
        "--density",
        type=float,
        default=1000.0,
        help="Fluid density (kg/m³ or lb/ft³, default: 1000)",
    )
    power_parser.add_argument(
        "--unit-system",
        choices=["SI", "US"],
        default="SI",
        help="Unit system (default: SI)",
    )
    power_parser.add_argument(
        "--output-format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)",
    )
    power_parser.add_argument(
        "--verbosity",
        choices=["minimal", "standard", "detailed"],
        default="standard",
        help="Output verbosity (default: standard)",
    )
    power_parser.set_defaults(func=cmd_power)

    # NPSH calculation command
    npsh_parser = pump_subparsers.add_parser(
        "npsh",
        help="Calculate NPSH",
        description="Calculate NPSH available and check cavitation risk",
    )
    npsh_parser.add_argument(
        "--atmospheric-pressure",
        type=float,
        required=True,
        help="Atmospheric pressure (Pa or psi)",
    )
    npsh_parser.add_argument(
        "--vapor-pressure",
        type=float,
        required=True,
        help="Vapor pressure (Pa or psi)",
    )
    npsh_parser.add_argument(
        "--suction-head",
        type=float,
        required=True,
        help="Suction elevation head (m or ft)",
    )
    npsh_parser.add_argument(
        "--suction-losses",
        type=float,
        default=0.0,
        help="Suction line pressure losses (Pa or psi, default: 0)",
    )
    npsh_parser.add_argument(
        "--density",
        type=float,
        default=1000.0,
        help="Fluid density (kg/m³ or lb/ft³, default: 1000)",
    )
    npsh_parser.add_argument(
        "--pump-type",
        type=str,
        help="Pump type for NPSH required lookup (optional)",
    )
    npsh_parser.add_argument(
        "--flow-rate",
        type=float,
        help="Flow rate for NPSH required lookup (m³/s or ft³/s, optional)",
    )
    npsh_parser.add_argument(
        "--unit-system",
        choices=["SI", "US"],
        default="SI",
        help="Unit system (default: SI)",
    )
    npsh_parser.add_argument(
        "--output-format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)",
    )
    npsh_parser.add_argument(
        "--verbosity",
        choices=["minimal", "standard", "detailed"],
        default="standard",
        help="Output verbosity (default: standard)",
    )
    npsh_parser.set_defaults(func=cmd_npsh)
