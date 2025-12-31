"""IAPWS-IF97 Region 2: Superheated steam and vapor.

Valid range:
- Pressure: 0 to 100 MPa
- Temperature: 273.15 K to 863.15 K (above saturation)
- Accuracy: ±0.06% for enthalpy and entropy

Uses the IAPWS-IF97 fundamental equation for Region 2.
Implementation uses the verified iapws library backend to ensure correctness.

Source: IAPWS, Revised Release on the IAPWS Industrial Formulation 1997 for the
Thermodynamic Properties of Water and Steam, August 2007.
"""


from iapws import iapws97

from ..exceptions import NumericalInstabilityError


def calculate_properties(pressure_pa: float, temperature_k: float) -> dict[str, float]:
    """Calculate Region 2 thermodynamic properties at given P-T.

    Uses official IAPWS-IF97 equations via the iapws library.

    Args:
        pressure_pa: Pressure in Pa
        temperature_k: Temperature in K

    Returns:
        Dictionary with keys:
        - enthalpy_kJ_kg: Specific enthalpy in kJ/kg
        - entropy_kJ_kg_K: Specific entropy in kJ/(kg·K)
        - internal_energy_kJ_kg: Specific internal energy in kJ/kg
        - density_kg_m3: Density in kg/m³

    Raises:
        NumericalInstabilityError: If calculation fails due to numerical issues
    """
    if pressure_pa <= 0 or temperature_k <= 0:
        raise ValueError("Pressure and temperature must be positive")

    try:
        # Convert pressure from Pa to MPa for iapws library
        pressure_mpa = pressure_pa / 1e6

        # Calculate properties using IAPWS-IF97
        steam = iapws97.IAPWS97(P=pressure_mpa, T=temperature_k)

        # Check if calculation was successful
        if not hasattr(steam, "h") or steam.h is None:
            raise ValueError("IAPWS-IF97 calculation failed")

        return {
            "enthalpy_kJ_kg": steam.h,
            "entropy_kJ_kg_K": steam.s,
            "internal_energy_kJ_kg": steam.u,
            "density_kg_m3": steam.rho,
        }

    except (ValueError, AttributeError, TypeError) as e:
        raise NumericalInstabilityError(
            f"Region 2 calculation failed at P={pressure_pa:.2e} Pa, T={temperature_k:.2f} K: {e}"
        )


__all__ = ["calculate_properties"]
