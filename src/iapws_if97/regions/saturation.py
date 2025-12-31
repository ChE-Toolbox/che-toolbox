"""IAPWS-IF97 Saturation Line: Two-phase boundary calculations.

Valid range:
- Pressure: 611.657 Pa to 22.064 MPa (triple point to critical point)
- Temperature: 273.16 K to 647.096 K (triple point to critical point)
- Accuracy: ±0.1% for saturation properties

Uses Wagner-Pruss saturation pressure equation and IAPWS-IF97 property equations.
Implementation uses the verified iapws library backend to ensure correctness.

Source: IAPWS, Revised Release on the IAPWS Industrial Formulation 1997 for the
Thermodynamic Properties of Water and Steam, August 2007.
"""


from iapws import iapws97

from ..exceptions import InputRangeError, NumericalInstabilityError


def calculate_saturation_temperature(pressure_pa: float) -> dict[str, float]:
    """Calculate saturation temperature and properties at given pressure.

    Args:
        pressure_pa: Saturation pressure in Pa

    Returns:
        Dictionary with keys:
        - saturation_temperature_K: Saturation temperature in K
        - saturation_pressure_Pa: Input pressure (for consistency)
        - enthalpy_liquid_kJ_kg: Saturated liquid enthalpy
        - enthalpy_vapor_kJ_kg: Saturated vapor enthalpy
        - entropy_liquid_kJ_kg_K: Saturated liquid entropy
        - entropy_vapor_kJ_kg_K: Saturated vapor entropy
        - density_liquid_kg_m3: Saturated liquid density
        - density_vapor_kg_m3: Saturated vapor density

    Raises:
        InputRangeError: If pressure outside saturation range
        NumericalInstabilityError: If calculation fails
    """
    # Validate pressure range
    P_MIN = 611.657  # Pa (triple point)
    P_MAX = 22.064e6  # Pa (critical point)

    if pressure_pa < P_MIN or pressure_pa > P_MAX:
        raise InputRangeError("pressure", pressure_pa, P_MIN, P_MAX)

    try:
        # Convert to MPa for iapws library
        pressure_mpa = pressure_pa / 1e6

        # Calculate saturation temperature using IAPWS-IF97
        # The iapws library provides Psat->Tsat calculation
        steam_liquid = iapws97.IAPWS97(P=pressure_mpa, x=0)  # Saturated liquid (quality=0)
        steam_vapor = iapws97.IAPWS97(P=pressure_mpa, x=1)  # Saturated vapor (quality=1)

        if not hasattr(steam_liquid, "T") or steam_liquid.T is None:
            raise ValueError("Saturation calculation failed")

        # Saturation temperature (same for both phases)
        T_sat = steam_liquid.T

        return {
            "saturation_temperature_K": T_sat,
            "saturation_pressure_Pa": pressure_pa,
            "enthalpy_liquid_kJ_kg": steam_liquid.h,
            "enthalpy_vapor_kJ_kg": steam_vapor.h,
            "entropy_liquid_kJ_kg_K": steam_liquid.s,
            "entropy_vapor_kJ_kg_K": steam_vapor.s,
            "density_liquid_kg_m3": steam_liquid.rho,
            "density_vapor_kg_m3": steam_vapor.rho,
        }

    except (ValueError, AttributeError, TypeError) as e:
        raise NumericalInstabilityError(
            reason=f"Saturation calculation failed: {e}",
            location=f"P={pressure_pa / 1e6:.3f} MPa saturation line",
            suggestion="Try pressure away from critical point (< 21 MPa) or use different formulation",
        )


def calculate_saturation_pressure(temperature_k: float) -> dict[str, float]:
    """Calculate saturation pressure and properties at given temperature.

    Args:
        temperature_k: Saturation temperature in K

    Returns:
        Dictionary with keys:
        - saturation_temperature_K: Input temperature (for consistency)
        - saturation_pressure_Pa: Saturation pressure in Pa
        - enthalpy_liquid_kJ_kg: Saturated liquid enthalpy
        - enthalpy_vapor_kJ_kg: Saturated vapor enthalpy
        - entropy_liquid_kJ_kg_K: Saturated liquid entropy
        - entropy_vapor_kJ_kg_K: Saturated vapor entropy
        - density_liquid_kg_m3: Saturated liquid density
        - density_vapor_kg_m3: Saturated vapor density

    Raises:
        InputRangeError: If temperature outside saturation range
        NumericalInstabilityError: If calculation fails
    """
    # Validate temperature range
    T_MIN = 273.16  # K (triple point)
    T_MAX = 647.096  # K (critical point)

    if temperature_k < T_MIN or temperature_k > T_MAX:
        raise InputRangeError("temperature", temperature_k, T_MIN, T_MAX)

    try:
        # Calculate saturation properties using IAPWS-IF97
        # The iapws library provides Tsat->Psat calculation
        steam_liquid = iapws97.IAPWS97(T=temperature_k, x=0)  # Saturated liquid
        steam_vapor = iapws97.IAPWS97(T=temperature_k, x=1)  # Saturated vapor

        if not hasattr(steam_liquid, "P") or steam_liquid.P is None:
            raise ValueError("Saturation calculation failed")

        # Saturation pressure (same for both phases)
        P_sat_mpa = steam_liquid.P
        P_sat_pa = P_sat_mpa * 1e6

        return {
            "saturation_temperature_K": temperature_k,
            "saturation_pressure_Pa": P_sat_pa,
            "enthalpy_liquid_kJ_kg": steam_liquid.h,
            "enthalpy_vapor_kJ_kg": steam_vapor.h,
            "entropy_liquid_kJ_kg_K": steam_liquid.s,
            "entropy_vapor_kJ_kg_K": steam_vapor.s,
            "density_liquid_kg_m3": steam_liquid.rho,
            "density_vapor_kg_m3": steam_vapor.rho,
        }

    except (ValueError, AttributeError, TypeError) as e:
        raise NumericalInstabilityError(
            reason=f"Saturation calculation failed: {e}",
            location=f"T={temperature_k:.2f} K saturation line",
            suggestion="Try temperature away from critical point (< 640 K) or use different formulation",
        )


__all__ = ["calculate_saturation_temperature", "calculate_saturation_pressure"]
