"""Heat Exchanger Calculations CLI - Main entry point.

Provides Click-based command-line interface for heat transfer calculations.
Supports four calculation methods: LMTD, NTU, Convection, and Insulation.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import click
import yaml


@click.group()
@click.version_option()
def cli() -> None:
    """Heat Exchanger Calculations - Command Line Interface.

    Calculate heat transfer rates, effectiveness, convection coefficients,
    and optimal insulation thickness using industry-standard methods.

    Examples:
        calculate-lmtd input.json
        calculate-ntu input.yaml --output result.json
        calculate-convection --temperature 300 --velocity 5.0
        calculate-insulation input.yaml --format table
    """
    pass


@cli.command()
@click.argument("input_file", required=False, type=click.Path(exists=True))
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    default=None,
    help="Output file path (JSON or YAML). If not specified, writes to stdout.",
)
@click.option(
    "-f",
    "--format",
    type=click.Choice(["json", "yaml", "table"]),
    default="json",
    help="Output format (json, yaml, or table).",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output with intermediate values.",
)
def calculate_lmtd(
    input_file: Optional[str],
    output: Optional[str],
    format: str,
    verbose: bool,
) -> None:
    """Calculate heat transfer using Log Mean Temperature Difference (LMTD) method.

    INPUT_FILE: Path to JSON or YAML file with calculation parameters.

    Supports counterflow, parallel flow, and crossflow heat exchanger configurations.
    Applies correction factors automatically for non-ideal flows.

    Example:
        calculate-lmtd exchanger.json --output result.json --format json
    """
    try:
        # Import here to avoid circular imports
        from heat_calc.lmtd import calculate_lmtd as calc_lmtd
        from heat_calc.models import (
            FluidState,
            HeatExchangerConfiguration,
            LMTDInput,
        )

        if not input_file:
            click.echo("Error: INPUT_FILE is required", err=True)
            sys.exit(1)

        # Load and parse input file
        input_data = load_input_file(input_file)

        # Parse into LMTDInput model
        hot_inlet = FluidState(
            temperature=input_data["hot_inlet"]["temperature"],
            mass_flow_rate=input_data["hot_inlet"]["mass_flow_rate"],
            specific_heat=input_data["hot_inlet"].get("specific_heat"),
        )
        hot_outlet = FluidState(
            temperature=input_data["hot_outlet"]["temperature"],
            mass_flow_rate=input_data["hot_outlet"]["mass_flow_rate"],
            specific_heat=input_data["hot_outlet"].get("specific_heat"),
        )
        cold_inlet = FluidState(
            temperature=input_data["cold_inlet"]["temperature"],
            mass_flow_rate=input_data["cold_inlet"]["mass_flow_rate"],
            specific_heat=input_data["cold_inlet"].get("specific_heat"),
        )
        cold_outlet = FluidState(
            temperature=input_data["cold_outlet"]["temperature"],
            mass_flow_rate=input_data["cold_outlet"]["mass_flow_rate"],
            specific_heat=input_data["cold_outlet"].get("specific_heat"),
        )

        config = HeatExchangerConfiguration(
            configuration=input_data["heat_exchanger"]["configuration"],
            area=input_data["heat_exchanger"]["area"],
            correction_factor=input_data["heat_exchanger"].get("correction_factor"),
            overall_heat_transfer_coefficient=input_data["heat_exchanger"].get(
                "overall_heat_transfer_coefficient"
            ),
        )

        lmtd_input = LMTDInput(
            hot_fluid_inlet=hot_inlet,
            hot_fluid_outlet=hot_outlet,
            cold_fluid_inlet=cold_inlet,
            cold_fluid_outlet=cold_outlet,
            heat_exchanger=config,
            overall_ua=input_data.get("overall_ua"),
        )

        # Calculate
        result = calc_lmtd(lmtd_input)

        # Format output
        output_dict = {
            "success": result.success,
            "calculation_method": result.calculation_method,
            "heat_transfer_rate_w": result.heat_transfer_rate,
            "lmtd_arithmetic_k": result.lmtd_arithmetic,
            "lmtd_effective_k": result.lmtd_effective,
            "correction_factor": result.correction_factor,
            "configuration": result.configuration_used,
            "effectiveness": result.effectiveness,
            "capacity_ratio": result.capacity_ratio,
            "energy_balance_error_percent": result.energy_balance_error_percent,
            "overall_ua_w_k": result.overall_ua,
        }

        if verbose:
            output_dict["intermediate_values"] = result.intermediate_values

        if result.error_message:
            output_dict["error_message"] = result.error_message

        # Output result
        if format == "table":
            click.echo(format_table_output(output_dict))
        elif format == "json":
            click.echo(json.dumps(output_dict, indent=2, default=str))
        elif format == "yaml":
            click.echo(yaml.dump(output_dict, default_flow_style=False, sort_keys=False))

        if output:
            save_output_file(output_dict, output, format)

        # Exit code based on success
        sys.exit(0 if result.success else 2)

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(2)


@cli.command()
@click.argument("input_file", required=False, type=click.Path(exists=True))
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    default=None,
    help="Output file path (JSON or YAML). If not specified, writes to stdout.",
)
@click.option(
    "-f",
    "--format",
    type=click.Choice(["json", "yaml", "table"]),
    default="json",
    help="Output format (json, yaml, or table).",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output with intermediate values.",
)
def calculate_ntu(
    input_file: Optional[str],
    output: Optional[str],
    format: str,
    verbose: bool,
) -> None:
    """Calculate heat exchanger effectiveness using Number of Transfer Units (NTU) method.

    INPUT_FILE: Path to JSON or YAML file with calculation parameters.

    Determines outlet temperatures and calculates effectiveness for various
    heat exchanger configurations.

    Example:
        calculate-ntu input.yaml --output result.yaml --format yaml
    """
    click.echo("NTU calculation stub - implementation in Phase 4", err=False)


@cli.command()
@click.argument("input_file", required=False, type=click.Path(exists=True))
@click.option(
    "-t",
    "--temperature",
    type=float,
    default=None,
    help="Fluid temperature (K). Overrides input file if specified.",
)
@click.option(
    "-v",
    "--velocity",
    type=float,
    default=None,
    help="Fluid velocity (m/s). Overrides input file if specified.",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    default=None,
    help="Output file path. If not specified, writes to stdout.",
)
@click.option(
    "-f",
    "--format",
    type=click.Choice(["json", "yaml", "table"]),
    default="json",
    help="Output format (json, yaml, or table).",
)
def calculate_convection(
    input_file: Optional[str],
    temperature: Optional[float],
    velocity: Optional[float],
    output: Optional[str],
    format: str,
) -> None:
    """Calculate convection heat transfer coefficients.

    INPUT_FILE: Path to JSON or YAML file with calculation parameters.

    Supports multiple geometries: flat plate (laminar/turbulent),
    pipe flow, cylinder in crossflow, and natural convection.

    Example:
        calculate-convection --temperature 300 --velocity 5.0 --format json
    """
    click.echo("Convection calculation stub - implementation in Phase 5", err=False)


@cli.command()
@click.argument("input_file", required=False, type=click.Path(exists=True))
@click.option(
    "-q",
    "--heat-loss",
    type=float,
    default=None,
    help="Current heat loss rate (W). Overrides input file if specified.",
)
@click.option(
    "-c",
    "--annual-cost",
    type=float,
    default=None,
    help="Annual energy cost factor ($). Overrides input file if specified.",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    default=None,
    help="Output file path. If not specified, writes to stdout.",
)
@click.option(
    "-f",
    "--format",
    type=click.Choice(["json", "yaml", "table"]),
    default="json",
    help="Output format (json, yaml, or table).",
)
def calculate_insulation(
    input_file: Optional[str],
    heat_loss: Optional[float],
    annual_cost: Optional[float],
    output: Optional[str],
    format: str,
) -> None:
    """Calculate optimal insulation thickness with economic analysis.

    INPUT_FILE: Path to JSON or YAML file with calculation parameters.

    Optimizes insulation thickness to minimize total annual cost while
    satisfying surface temperature constraints.

    Example:
        calculate-insulation --heat-loss 1000 --annual-cost 5000 --format table
    """
    click.echo("Insulation calculation stub - implementation in Phase 6", err=False)


def load_input_file(file_path: str) -> Dict[str, Any]:
    """Load input data from JSON or YAML file.

    Parameters
    ----------
    file_path : str
        Path to input file (JSON or YAML).

    Returns
    -------
    Dict[str, Any]
        Parsed input data.

    Raises
    ------
    FileNotFoundError
        If file does not exist.
    ValueError
        If file format is not supported or JSON/YAML is invalid.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    try:
        if path.suffix.lower() in [".json"]:
            with open(path, "r") as f:
                return json.load(f)
        elif path.suffix.lower() in [".yaml", ".yml"]:
            with open(path, "r") as f:
                data = yaml.safe_load(f)
                return data if data is not None else {}
        else:
            raise ValueError(
                f"Unsupported file format: {path.suffix}. Use .json or .yaml"
            )
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {file_path}: {e}") from e
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {file_path}: {e}") from e


def save_output_file(data: Dict[str, Any], file_path: str, format: str) -> None:
    """Save output data to file in specified format.

    Parameters
    ----------
    data : Dict[str, Any]
        Data to save.
    file_path : str
        Output file path.
    format : str
        Output format (json or yaml).

    Raises
    ------
    ValueError
        If format is not supported.
    """
    path = Path(file_path)

    try:
        if format.lower() == "json":
            with open(path, "w") as f:
                json.dump(data, f, indent=2, default=str)
        elif format.lower() in ["yaml", "yml"]:
            with open(path, "w") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        else:
            raise ValueError(f"Unsupported output format: {format}")
    except Exception as e:
        raise ValueError(f"Failed to write output file {file_path}: {e}") from e


def format_table_output(data: Dict[str, Any]) -> str:
    """Format calculation results as ASCII table.

    Parameters
    ----------
    data : Dict[str, Any]
        Result data to format.

    Returns
    -------
    str
        Formatted table output.
    """
    lines: list[str] = []

    if "primary_value" in data:
        lines.append(f"Primary Value: {data.get('primary_value', 'N/A')}")
    if "calculation_method" in data:
        lines.append(f"Method: {data.get('calculation_method', 'N/A')}")

    if "intermediate_values" in data and data["intermediate_values"]:
        lines.append("\nIntermediate Values:")
        for key, value in data["intermediate_values"].items():
            lines.append(f"  {key}: {value}")

    return "\n".join(lines)


if __name__ == "__main__":
    cli()
