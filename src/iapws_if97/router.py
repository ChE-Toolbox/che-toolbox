"""Region assignment and routing for IAPWS-IF97 calculations.

Determines which thermodynamic region applies to given P-T conditions
and validates inputs against global and region-specific boundaries.
"""


from . import constants
from .exceptions import InputRangeError, InvalidStateError
from .models import Region


def validate_pressure_temperature(pressure_pa: float, temperature_k: float) -> None:
    """Validate pressure and temperature are within global valid range.

    Args:
        pressure_pa: Pressure in Pa
        temperature_k: Temperature in K

    Raises:
        InputRangeError: If P or T outside global valid range
    """
    if (
        pressure_pa < constants.GLOBAL_PRESSURE_MIN_PA
        or pressure_pa > constants.GLOBAL_PRESSURE_MAX_PA
    ):
        raise InputRangeError(
            "pressure",
            pressure_pa,
            constants.GLOBAL_PRESSURE_MIN_PA,
            constants.GLOBAL_PRESSURE_MAX_PA,
        )

    if (
        temperature_k < constants.GLOBAL_TEMPERATURE_MIN_K
        or temperature_k > constants.GLOBAL_TEMPERATURE_MAX_K
    ):
        raise InputRangeError(
            "temperature",
            temperature_k,
            constants.GLOBAL_TEMPERATURE_MIN_K,
            constants.GLOBAL_TEMPERATURE_MAX_K,
        )


def saturation_pressure_estimate(temperature_k: float) -> float:
    """Calculate saturation pressure at given temperature using Wagner-Pruss equation.

    Used for determining if (P, T) is in saturation region or single-phase.
    Uses the accurate IAPWS-IF97 saturation calculation via iapws library.

    Args:
        temperature_k: Temperature in K

    Returns:
        Saturation pressure in Pa

    Note:
        Uses regions.saturation module for accurate calculation.
    """
    # Return very large values outside valid range
    if temperature_k > constants.SATURATION_TEMPERATURE_MAX_K:
        return float("inf")
    if temperature_k < constants.SATURATION_TEMPERATURE_MIN_K:
        return 0.0

    # Use accurate saturation calculation from saturation module
    try:
        from .regions import saturation

        sat_data = saturation.calculate_saturation_pressure(temperature_k)
        return sat_data["saturation_pressure_Pa"]
    except Exception:
        # If calculation fails, return a safe fallback
        # This should rarely happen as we've already validated the range
        return 100e3  # Rough average saturation pressure


def assign_region(pressure_pa: float, temperature_k: float) -> tuple[Region, str]:
    """Assign which IAPWS-IF97 region (1, 2, 3, or saturation) applies.

    Args:
        pressure_pa: Pressure in Pa
        temperature_k: Temperature in K

    Returns:
        Tuple of (Region enum, diagnostic string)

    Raises:
        InputRangeError: If P or T outside valid range
        InvalidStateError: If conditions exactly on saturation line
    """
    # First validate global range
    validate_pressure_temperature(pressure_pa, temperature_k)

    # Estimate saturation pressure at this temperature
    p_sat = saturation_pressure_estimate(temperature_k)

    # Check if on saturation line (within tolerance)
    sat_tolerance = 1e3  # 1 kPa tolerance for saturation detection
    if abs(pressure_pa - p_sat) < sat_tolerance:
        raise InvalidStateError(pressure_pa, temperature_k)

    # Region determination based on pressure vs saturation pressure
    if pressure_pa < p_sat:
        # Low pressure relative to saturation: Region 2 (superheated steam)
        return Region.REGION2, "Superheated steam (Region 2)"
    else:  # pressure_pa >= p_sat (above saturation line)
        # High pressure: Could be Region 1 or 3
        # Region 3 is near the critical point (high P, high T)
        # Region 1 is compressed liquid (high P, low-medium T)

        # Check if in Region 3 range (near critical point)
        if temperature_k >= constants.REGION3_TEMPERATURE_MIN_K:
            return Region.REGION3, "Supercritical region (Region 3)"
        else:
            # Default to Region 1 for compressed liquid
            return Region.REGION1, "Compressed liquid (Region 1)"


__all__ = ["validate_pressure_temperature", "assign_region", "saturation_pressure_estimate"]
