"""Heat Exchanger Calculations CLI - Main entry point.

Provides Click-based command-line interface for heat transfer calculations.
Supports four calculation methods: LMTD, NTU, Convection, and Insulation.
"""

import json
import sys
from pathlib import Path
from typing import Any

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
    input_file: str | None,
    output: str | None,
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
    input_file: str | None,
    output: str | None,
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
    try:
        # Import here to avoid circular imports
        from heat_calc.models.ntu_input import NTUInput
        from heat_calc.ntu import calculate_ntu as calc_ntu

        if not input_file:
            click.echo("Error: INPUT_FILE is required", err=True)
            sys.exit(1)

        # Load and parse input file
        input_data = load_input_file(input_file)

        # Parse into NTUInput model
        try:
            ntu_input = NTUInput(**input_data)
        except Exception as e:
            click.echo(f"Error parsing input data: {e}", err=True)
            sys.exit(2)

        # Calculate NTU
        result = calc_ntu(ntu_input)

        # Check if calculation was successful
        if not result.success:
            click.echo(f"Calculation failed: {result.error_message}", err=True)
            sys.exit(2)

        # Prepare output data
        output_data = result.model_dump()

        # Output results
        if format == "table":
            table_output = format_ntu_table(result, verbose)
            if output:
                Path(output).write_text(table_output)
            else:
                click.echo(table_output)
        else:
            # JSON or YAML output
            if output:
                save_output_file(output_data, output, format)
                click.echo(f"Results saved to {output}")
            else:
                if format == "json":
                    click.echo(json.dumps(output_data, indent=2, default=str))
                elif format == "yaml":
                    click.echo(yaml.dump(output_data, default_flow_style=False, sort_keys=False))

        sys.exit(0)

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(2)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


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
    input_file: str | None,
    _temperature: float | None,
    _velocity: float | None,
    output: str | None,
    format: str,
) -> None:
    """Calculate convection heat transfer coefficients.

    INPUT_FILE: Path to JSON or YAML file with calculation parameters.

    Supports multiple geometries: flat plate (laminar/turbulent),
    pipe flow, cylinder in crossflow, and natural convection.

    Example:
        calculate-convection input.yaml --output result.json --format json
    """
    try:
        # Import here to avoid circular imports
        from heat_calc.convection import calculate_convection as calc_convection
        from heat_calc.models.convection_input import (
            CylinderCrossflowConvection,
            FlatPlateConvection,
            FluidProperties,
            PipeFlowConvection,
            VerticalPlateNaturalConvection,
        )

        if not input_file:
            click.echo("Error: INPUT_FILE is required", err=True)
            sys.exit(1)

        # Load and parse input file
        input_data = load_input_file(input_file)

        # Parse fluid properties
        fluid_props_data = input_data.get("fluid_properties", {})
        fluid_props = FluidProperties(**fluid_props_data)

        # Determine geometry type and create appropriate input model
        geometry_type = input_data.get("geometry_type")

        if geometry_type == "flat_plate":
            convection_input = FlatPlateConvection(
                fluid_properties=fluid_props,
                **{k: v for k, v in input_data.items() if k not in ["fluid_properties"]}
            )
        elif geometry_type == "pipe_flow":
            convection_input = PipeFlowConvection(
                fluid_properties=fluid_props,
                **{k: v for k, v in input_data.items() if k not in ["fluid_properties"]}
            )
        elif geometry_type == "cylinder_crossflow":
            convection_input = CylinderCrossflowConvection(
                fluid_properties=fluid_props,
                **{k: v for k, v in input_data.items() if k not in ["fluid_properties"]}
            )
        elif geometry_type == "vertical_plate_natural":
            convection_input = VerticalPlateNaturalConvection(
                fluid_properties=fluid_props,
                **{k: v for k, v in input_data.items() if k not in ["fluid_properties"]}
            )
        else:
            click.echo(
                f"Error: Unknown geometry_type '{geometry_type}'. "
                f"Must be one of: flat_plate, pipe_flow, cylinder_crossflow, vertical_plate_natural",
                err=True
            )
            sys.exit(2)

        # Calculate convection
        result = calc_convection(convection_input)

        # Check if calculation was successful
        if not result.success:
            click.echo(f"Calculation failed: {result.error_message}", err=True)
            sys.exit(2)

        # Prepare output data
        output_data = result.model_dump()

        # Output results
        if format == "table":
            table_output = format_convection_table(result)
            if output:
                Path(output).write_text(table_output)
            else:
                click.echo(table_output)
        else:
            # JSON or YAML output
            if output:
                save_output_file(output_data, output, format)
                click.echo(f"Results saved to {output}")
            else:
                if format == "json":
                    click.echo(json.dumps(output_data, indent=2, default=str))
                elif format == "yaml":
                    click.echo(yaml.dump(output_data, default_flow_style=False, sort_keys=False))

        sys.exit(0)

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(2)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


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
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output with intermediate values.",
)
def calculate_insulation(
    input_file: str | None,
    _heat_loss: float | None,
    _annual_cost: float | None,
    output: str | None,
    format: str,
    verbose: bool,
) -> None:
    """Calculate optimal insulation thickness with economic analysis.

    INPUT_FILE: Path to JSON or YAML file with calculation parameters.

    Optimizes insulation thickness to minimize total annual cost while
    satisfying surface temperature constraints.

    Example:
        calculate-insulation input.yaml --output result.json --format json
    """
    try:
        # Import here to avoid circular imports
        from heat_calc.insulation import calculate_insulation as calc_insulation
        from heat_calc.models.insulation_input import InsulationInput

        if not input_file:
            click.echo("Error: INPUT_FILE is required", err=True)
            sys.exit(1)

        # Load and parse input file
        input_data = load_input_file(input_file)

        # Parse into InsulationInput model
        try:
            insulation_input = InsulationInput(**input_data)
        except Exception as e:
            click.echo(f"Error parsing input data: {e}", err=True)
            sys.exit(2)

        # Calculate optimal insulation
        result = calc_insulation(insulation_input)

        # Check if calculation was successful
        if not result.success:
            click.echo(f"Calculation failed: {result.error_message}", err=True)
            sys.exit(2)

        # Prepare output data
        output_data = {
            "success": result.success,
            "calculation_method": result.calculation_method,
            "optimal_insulation_thickness_m": result.optimal_insulation_thickness,
            "optimization_mode": result.optimization_mode,
            "heat_loss_uninsulated_w": result.Q_uninsulated,
            "heat_loss_insulated_w": result.Q_insulated,
            "heat_loss_reduction_percent": result.heat_loss_reduction_percent,
            "annual_energy_savings_mwh": result.annual_energy_savings,
            "annual_cost_savings_usd": result.annual_cost_savings,
            "annual_insulation_cost_usd": result.annual_insulation_cost,
            "net_annual_savings_usd": result.net_annual_savings,
            "payback_period_years": result.payback_period_years,
            "T_surface_insulated_k": result.T_surface_insulated,
            "insulation_volume_m3": result.insulation_volume,
            "insulation_mass_kg": result.insulation_mass,
            "total_insulation_cost_usd": result.total_insulation_cost,
        }

        if result.T_surface_required is not None:
            output_data["T_surface_required_k"] = result.T_surface_required

        if verbose:
            output_data["intermediate_values"] = result.intermediate_values

        if result.error_message:
            output_data["error_message"] = result.error_message

        # Output results
        if format == "table":
            table_output = format_insulation_table(result, verbose)
            if output:
                Path(output).write_text(table_output)
            else:
                click.echo(table_output)
        else:
            output_text = None
            if format == "json":
                output_text = json.dumps(output_data, indent=2, default=str)
            elif format == "yaml":
                output_text = yaml.dump(output_data, default_flow_style=False, sort_keys=False)

            if output:
                Path(output).write_text(output_text)
            else:
                click.echo(output_text)

        sys.exit(0)

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(2)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


def load_input_file(file_path: str) -> dict[str, Any]:
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
            with path.open() as f:
                return json.load(f)
        elif path.suffix.lower() in [".yaml", ".yml"]:
            with path.open() as f:
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


def save_output_file(data: dict[str, Any], file_path: str, format: str) -> None:
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
            with path.open("w") as f:
                json.dump(data, f, indent=2, default=str)
        elif format.lower() in ["yaml", "yml"]:
            with path.open("w") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        else:
            raise ValueError(f"Unsupported output format: {format}")
    except Exception as e:
        raise ValueError(f"Failed to write output file {file_path}: {e}") from e


def format_table_output(data: dict[str, Any]) -> str:
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

    if data.get("intermediate_values"):
        lines.append("\nIntermediate Values:")
        for key, value in data["intermediate_values"].items():
            lines.append(f"  {key}: {value}")

    return "\n".join(lines)


def format_ntu_table(result: Any, verbose: bool = False) -> str:
    """Format NTU calculation results as ASCII table.

    Parameters
    ----------
    result : NTUResult
        NTU calculation result.
    verbose : bool
        If True, include all intermediate values.

    Returns
    -------
    str
        Formatted table output.
    """
    lines: list[str] = []
    lines.append("=" * 60)
    lines.append("NTU Method Heat Exchanger Calculation Results")
    lines.append("=" * 60)
    lines.append("")

    # Primary results
    lines.append("PRIMARY RESULTS:")
    lines.append(f"  NTU:                    {result.NTU:.4f}")
    lines.append(f"  Effectiveness:          {result.effectiveness:.4f} ({result.effectiveness*100:.2f}%)")
    lines.append(f"  Heat Transfer Rate:     {result.heat_transfer_rate:.2f} W")
    lines.append("")

    # Outlet temperatures
    lines.append("OUTLET TEMPERATURES:")
    lines.append(f"  Hot Outlet:             {result.T_hot_outlet:.2f} K ({result.T_hot_outlet - 273.15:.2f} °C)")
    lines.append(f"  Cold Outlet:            {result.T_cold_outlet:.2f} K ({result.T_cold_outlet - 273.15:.2f} °C)")
    lines.append("")

    # Heat capacity rates
    lines.append("HEAT CAPACITY RATES:")
    lines.append(f"  C_hot:                  {result.C_hot:.2f} W/K")
    lines.append(f"  C_cold:                 {result.C_cold:.2f} W/K")
    lines.append(f"  C_min:                  {result.C_min:.2f} W/K")
    lines.append(f"  C_max:                  {result.C_max:.2f} W/K")
    lines.append(f"  C_ratio (C_min/C_max):  {result.C_ratio:.4f}")
    lines.append("")

    # Thermodynamic limits
    lines.append("THERMODYNAMIC LIMITS:")
    lines.append(f"  Q_max:                  {result.Q_max:.2f} W")
    lines.append(f"  Effectiveness Max:      {result.effectiveness_theoretical_max:.4f}")
    lines.append(f"  Q_actual / Q_max:       {result.heat_transfer_rate/result.Q_max:.4f}")
    lines.append("")

    # Energy balance
    lines.append("VALIDATION:")
    lines.append(f"  Energy Balance Error:   {result.energy_balance_error_percent:.4f}%")
    lines.append(f"  Calculation Method:     {result.calculation_method}")
    lines.append("")

    # Intermediate values (if verbose)
    if verbose and result.intermediate_values:
        lines.append("INTERMEDIATE VALUES:")
        for key, value in result.intermediate_values.items():
            lines.append(f"  {key}: {value}")
        lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)


def format_convection_table(result: Any) -> str:
    """Format convection calculation results as ASCII table.

    Parameters
    ----------
    result : ConvectionResult
        Convection calculation result.

    Returns
    -------
    str
        Formatted table output.
    """
    lines: list[str] = []
    lines.append("=" * 60)
    lines.append("Convection Heat Transfer Calculation Results")
    lines.append("=" * 60)
    lines.append("")

    # Primary results
    lines.append("PRIMARY RESULTS:")
    lines.append(f"  Heat Transfer Coefficient: {result.h:.2f} W/(m²·K)")
    lines.append(f"  Flow Regime:                {result.flow_regime}")
    lines.append(f"  Correlation:                {result.correlation_equation}")
    lines.append(f"  Geometry Type:              {result.geometry_type}")
    lines.append("")

    # Dimensionless numbers
    lines.append("DIMENSIONLESS NUMBERS:")
    if result.Reynolds > 0:
        lines.append(f"  Reynolds Number (Re):       {result.Reynolds:.2e}")
    lines.append(f"  Prandtl Number (Pr):        {result.Prandtl:.4f}")
    lines.append(f"  Nusselt Number (Nu):        {result.Nusselt:.2f}")
    if result.Grashof is not None:
        lines.append(f"  Grashof Number (Gr):        {result.Grashof:.2e}")
    if result.Rayleigh is not None:
        lines.append(f"  Rayleigh Number (Ra):       {result.Rayleigh:.2e}")
    lines.append("")

    # Correlation validity
    lines.append("CORRELATION VALIDITY:")
    lines.append(f"  Within Valid Range:         {'Yes' if result.is_within_correlation_range else 'No'}")
    if result.applicable_range:
        lines.append("  Applicable Ranges:")
        for param, (min_val, max_val) in result.applicable_range.items():
            lines.append(f"    {param}: [{min_val:.2e}, {max_val:.2e}]")
    lines.append("")

    # Intermediate values (if present)
    if result.intermediate_values:
        lines.append("INTERMEDIATE VALUES:")
        for key, value in result.intermediate_values.items():
            if isinstance(value, float):
                lines.append(f"  {key}: {value:.4e}")
            else:
                lines.append(f"  {key}: {value}")
        lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)


def format_insulation_table(result: Any, verbose: bool = False) -> str:
    """Format insulation calculation results as ASCII table.

    Parameters
    ----------
    result : InsulationResult
        Insulation calculation result.
    verbose : bool
        If True, include all intermediate values.

    Returns
    -------
    str
        Formatted table output.
    """
    lines: list[str] = []
    lines.append("=" * 70)
    lines.append("Insulation Sizing and Economic Optimization Results")
    lines.append("=" * 70)
    lines.append("")

    # Optimization summary
    lines.append("OPTIMIZATION SUMMARY:")
    lines.append(f"  Mode:                           {result.optimization_mode}")
    lines.append(f"  Optimal Insulation Thickness:   {result.optimal_insulation_thickness:.4f} m ({result.optimal_insulation_thickness*1000:.1f} mm)")
    lines.append("")

    # Heat loss comparison
    lines.append("HEAT LOSS ANALYSIS:")
    lines.append(f"  Uninsulated Heat Loss:          {result.Q_uninsulated:.2f} W")
    lines.append(f"  Insulated Heat Loss:            {result.Q_insulated:.2f} W")
    lines.append(f"  Heat Loss Reduction:            {result.heat_loss_reduction_percent:.2f}%")
    lines.append("")

    # Temperature profile
    lines.append("TEMPERATURE PROFILE:")
    lines.append(f"  Surface Temperature (Insulated):{result.T_surface_insulated:.2f} K ({result.T_surface_insulated - 273.15:.2f} °C)")
    if result.T_surface_required is not None:
        lines.append(f"  Required Surface Temperature:   {result.T_surface_required:.2f} K ({result.T_surface_required - 273.15:.2f} °C)")
    lines.append("")

    # Economic analysis
    lines.append("ECONOMIC ANALYSIS:")
    lines.append(f"  Annual Energy Savings:          {result.annual_energy_savings:.2f} MWh/year")
    lines.append(f"  Annual Cost Savings:            ${result.annual_cost_savings:.2f}/year")
    lines.append(f"  Annual Insulation Cost:         ${result.annual_insulation_cost:.2f}/year")
    lines.append(f"  Net Annual Savings:             ${result.net_annual_savings:.2f}/year")
    if result.payback_period_years > 0:
        lines.append(f"  Simple Payback Period:          {result.payback_period_years:.2f} years")
    lines.append("")

    # Material quantities
    lines.append("MATERIAL REQUIREMENTS:")
    lines.append(f"  Insulation Volume:              {result.insulation_volume:.3f} m³")
    lines.append(f"  Insulation Mass:                {result.insulation_mass:.2f} kg")
    lines.append(f"  Total Insulation Cost:          ${result.total_insulation_cost:.2f}")
    lines.append("")

    # Metadata
    lines.append("CALCULATION METADATA:")
    lines.append(f"  Calculation Method:             {result.calculation_method}")
    lines.append(f"  Success:                        {result.success}")
    lines.append("")

    # Intermediate values (if verbose)
    if verbose and result.intermediate_values:
        lines.append("INTERMEDIATE VALUES:")
        for key, value in result.intermediate_values.items():
            if isinstance(value, float):
                lines.append(f"  {key}: {value:.6f}")
            else:
                lines.append(f"  {key}: {value}")
        lines.append("")

    lines.append("=" * 70)
    return "\n".join(lines)


if __name__ == "__main__":
    cli()
