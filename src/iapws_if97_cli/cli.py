"""Command-line interface for IAPWS-IF97 steam properties.

Provides convenient CLI commands for:
- Property calculations at P-T conditions
- Saturation property lookups
- Batch processing
"""

import json
import sys

import click

from iapws_if97 import SteamTable, ureg
from iapws_if97.exceptions import InputRangeError, NumericalInstabilityError

steam = SteamTable()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """IAPWS-IF97 Steam Property Calculator.

    Calculate thermodynamic properties of water and steam using the
    IAPWS Industrial Formulation 1997.
    """


@cli.command()
@click.option("--pressure", "-P", required=True, type=float, help="Pressure in MPa")
@click.option("--temperature", "-T", required=True, type=float, help="Temperature in K")
@click.option(
    "--property",
    "-p",
    type=click.Choice(["h", "s", "u", "rho", "all"], case_sensitive=False),
    default="all",
    help="Property to calculate (h=enthalpy, s=entropy, u=internal energy, rho=density)",
)
@click.option("--json", "output_json", is_flag=True, help="Output in JSON format")
def property(pressure: float, temperature: float, property: str, output_json: bool):
    """Calculate properties at given pressure and temperature.

    Examples:
        steam-table property -P 10 -T 500
        steam-table property -P 10 -T 500 -p h --json
    """
    try:
        # Convert to Pint quantities
        P = pressure * ureg.MPa
        T = temperature * ureg.K

        # Calculate requested properties
        results = {
            "pressure_MPa": pressure,
            "temperature_K": temperature,
        }

        if property == "all" or property == "h":
            h = steam.h_pt(P, T)
            results["enthalpy_kJ_kg"] = h.to("kJ/kg").magnitude

        if property == "all" or property == "s":
            s = steam.s_pt(P, T)
            results["entropy_kJ_kg_K"] = s.to("kJ/(kg*K)").magnitude

        if property == "all" or property == "u":
            u = steam.u_pt(P, T)
            results["internal_energy_kJ_kg"] = u.to("kJ/kg").magnitude

        if property == "all" or property == "rho":
            rho = steam.rho_pt(P, T)
            results["density_kg_m3"] = rho.to("kg/m**3").magnitude

        # Output results
        if output_json:
            click.echo(json.dumps(results, indent=2))
        else:
            click.echo(f"\nPressure: {pressure} MPa")
            click.echo(f"Temperature: {temperature} K")
            click.echo("-" * 40)
            if "enthalpy_kJ_kg" in results:
                click.echo(f"Enthalpy (h):         {results['enthalpy_kJ_kg']:.2f} kJ/kg")
            if "entropy_kJ_kg_K" in results:
                click.echo(f"Entropy (s):          {results['entropy_kJ_kg_K']:.4f} kJ/(kg·K)")
            if "internal_energy_kJ_kg" in results:
                click.echo(f"Internal Energy (u):  {results['internal_energy_kJ_kg']:.2f} kJ/kg")
            if "density_kg_m3" in results:
                click.echo(f"Density (ρ):          {results['density_kg_m3']:.2f} kg/m³")
            click.echo()

    except InputRangeError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except NumericalInstabilityError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--pressure", "-P", type=float, help="Pressure in MPa (for T_sat calculation)")
@click.option("--temperature", "-T", type=float, help="Temperature in K (for P_sat calculation)")
@click.option("--json", "output_json", is_flag=True, help="Output in JSON format")
def saturation(pressure: float | None, temperature: float | None, output_json: bool):
    """Calculate saturation properties.

    Provide either --pressure OR --temperature (not both).

    Examples:
        steam-table saturation -P 1.0
        steam-table saturation -T 373.15 --json
    """
    if (pressure is None and temperature is None) or (
        pressure is not None and temperature is not None
    ):
        click.echo("Error: Provide either --pressure OR --temperature (not both)", err=True)
        sys.exit(1)

    try:
        if pressure is not None:
            # Calculate T_sat from pressure
            P = pressure * ureg.MPa
            sat = steam.T_sat(P)

            results = {
                "saturation_pressure_MPa": pressure,
                "saturation_temperature_K": sat.saturation_temperature.to("K").magnitude,
                "enthalpy_liquid_kJ_kg": sat.enthalpy_liquid.to("kJ/kg").magnitude,
                "enthalpy_vapor_kJ_kg": sat.enthalpy_vapor.to("kJ/kg").magnitude,
                "entropy_liquid_kJ_kg_K": sat.entropy_liquid.to("kJ/(kg*K)").magnitude,
                "entropy_vapor_kJ_kg_K": sat.entropy_vapor.to("kJ/(kg*K)").magnitude,
                "density_liquid_kg_m3": sat.density_liquid.to("kg/m**3").magnitude,
                "density_vapor_kg_m3": sat.density_vapor.to("kg/m**3").magnitude,
                "heat_of_vaporization_kJ_kg": sat.heat_of_vaporization().to("kJ/kg").magnitude,
            }
        else:
            # Calculate P_sat from temperature
            T = temperature * ureg.K
            sat = steam.P_sat(T)

            results = {
                "saturation_temperature_K": temperature,
                "saturation_pressure_MPa": sat.saturation_pressure.to("MPa").magnitude,
                "enthalpy_liquid_kJ_kg": sat.enthalpy_liquid.to("kJ/kg").magnitude,
                "enthalpy_vapor_kJ_kg": sat.enthalpy_vapor.to("kJ/kg").magnitude,
                "entropy_liquid_kJ_kg_K": sat.entropy_liquid.to("kJ/(kg*K)").magnitude,
                "entropy_vapor_kJ_kg_K": sat.entropy_vapor.to("kJ/(kg*K)").magnitude,
                "density_liquid_kg_m3": sat.density_liquid.to("kg/m**3").magnitude,
                "density_vapor_kg_m3": sat.density_vapor.to("kg/m**3").magnitude,
                "heat_of_vaporization_kJ_kg": sat.heat_of_vaporization().to("kJ/kg").magnitude,
            }

        # Output results
        if output_json:
            click.echo(json.dumps(results, indent=2))
        else:
            click.echo("\nSaturation Properties:")
            click.echo(f"  T_sat: {results['saturation_temperature_K']:.2f} K")
            click.echo(f"  P_sat: {results['saturation_pressure_MPa']:.4f} MPa")
            click.echo("-" * 40)
            click.echo("Liquid phase (saturated):")
            click.echo(f"  h_f:   {results['enthalpy_liquid_kJ_kg']:.2f} kJ/kg")
            click.echo(f"  s_f:   {results['entropy_liquid_kJ_kg_K']:.4f} kJ/(kg·K)")
            click.echo(f"  ρ_f:   {results['density_liquid_kg_m3']:.2f} kg/m³")
            click.echo("\nVapor phase (saturated):")
            click.echo(f"  h_g:   {results['enthalpy_vapor_kJ_kg']:.2f} kJ/kg")
            click.echo(f"  s_g:   {results['entropy_vapor_kJ_kg_K']:.4f} kJ/(kg·K)")
            click.echo(f"  ρ_g:   {results['density_vapor_kg_m3']:.2f} kg/m³")
            click.echo("\nHeat of vaporization:")
            click.echo(f"  h_fg:  {results['heat_of_vaporization_kJ_kg']:.2f} kJ/kg")
            click.echo()

    except InputRangeError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except NumericalInstabilityError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def info():
    """Display information about IAPWS-IF97 implementation."""
    click.echo("\nIAPWS-IF97 Steam Property Calculator")
    click.echo("=" * 50)
    click.echo("\nImplementation: IAPWS Industrial Formulation 1997")
    click.echo("Version: 1.0.0")
    click.echo("\nValid Ranges:")
    click.echo("  Region 1 (Compressed Liquid):")
    click.echo("    P: 0.611657 MPa to 100 MPa")
    click.echo("    T: 273.15 K to saturation")
    click.echo("\n  Region 2 (Superheated Steam):")
    click.echo("    P: 0 to 100 MPa")
    click.echo("    T: 273.15 K to 863.15 K")
    click.echo("\n  Region 3 (Supercritical):")
    click.echo("    P: 16.6 MPa to 100 MPa")
    click.echo("    T: 623.15 K to 863.15 K")
    click.echo("\n  Saturation Line:")
    click.echo("    P: 611.657 Pa to 22.064 MPa")
    click.echo("    T: 273.16 K to 647.096 K")
    click.echo("\nAccuracy:")
    click.echo("  Region 1: ±0.03%")
    click.echo("  Region 2: ±0.06%")
    click.echo("  Region 3: ±0.2%")
    click.echo("  Saturation: ±0.1%")
    click.echo()


def main():
    """Entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()
