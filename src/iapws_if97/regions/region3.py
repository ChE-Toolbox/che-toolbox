"""IAPWS-IF97 Region 3: Supercritical fluid.

Valid range:
- Pressure: 16.6 MPa to 100 MPa
- Temperature: 623.15 K to 863.15 K
- Accuracy: ±0.2% for density

Uses the IAPWS-IF97 fundamental equation for Region 3.
Implementation uses the verified iapws library backend to ensure correctness.
Includes singularity detection near critical point.

Source: IAPWS, Revised Release on the IAPWS Industrial Formulation 1997 for the
Thermodynamic Properties of Water and Steam, August 2007.
"""

import math

from iapws import iapws97

from ..exceptions import NumericalInstabilityError

# Critical point constants
CRITICAL_PRESSURE_MPA = 22.064
CRITICAL_TEMPERATURE_K = 647.096
SINGULARITY_THRESHOLD = 0.05  # 5% distance threshold


def calculate_properties(pressure_pa: float, temperature_k: float) -> dict[str, float]:
    """Calculate Region 3 thermodynamic properties at given P-T.

    Uses official IAPWS-IF97 equations via the iapws library.
    Includes singularity detection near critical point.

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
        NumericalInstabilityError: If too close to critical point or calculation fails
    """
    if pressure_pa <= 0 or temperature_k <= 0:
        raise ValueError("Pressure and temperature must be positive")

    try:
        # Convert pressure from Pa to MPa
        pressure_mpa = pressure_pa / 1e6

        # Check distance from critical point
        p_normalized = (pressure_mpa - CRITICAL_PRESSURE_MPA) / CRITICAL_PRESSURE_MPA
        t_normalized = (temperature_k - CRITICAL_TEMPERATURE_K) / CRITICAL_TEMPERATURE_K
        distance = math.sqrt(p_normalized**2 + t_normalized**2)

        if distance < SINGULARITY_THRESHOLD:
            raise NumericalInstabilityError(
                f"Conditions too close to critical point "
                f"({CRITICAL_PRESSURE_MPA} MPa, {CRITICAL_TEMPERATURE_K} K) for reliable computation. "
                f"Distance: {distance * 100:.1f}%. "
                f"Suggestion: Move at least 5% away (e.g., P > {CRITICAL_PRESSURE_MPA * 1.05:.1f} MPa "
                f"or T > {CRITICAL_TEMPERATURE_K * 1.05:.1f} K)"
            )

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

    except NumericalInstabilityError:
        # Re-raise singularity errors
        raise
    except (ValueError, AttributeError, TypeError) as e:
        raise NumericalInstabilityError(
            f"Region 3 calculation failed at P={pressure_pa:.2e} Pa, T={temperature_k:.2f} K: {e}"
        )


__all__ = ["calculate_properties"]
