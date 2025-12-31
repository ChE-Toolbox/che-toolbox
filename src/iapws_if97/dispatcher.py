"""Region dispatcher for IAPWS-IF97 property calculations.

Routes pressure-temperature conditions to the appropriate region (1, 2, or 3)
and delegates property calculation to that region's implementation.
"""

from . import models, router
from .regions import region1, region2, region3
from .units import ureg


def calculate_properties(pressure_pa: float, temperature_k: float) -> "models.SteamProperties":
    """Calculate steam properties at given pressure and temperature.

    Routes to the appropriate IAPWS-IF97 region based on P-T conditions
    and returns thermodynamic properties as a SteamProperties object.

    Args:
        pressure_pa: Absolute pressure in Pa
        temperature_k: Temperature in K

    Returns:
        SteamProperties dataclass with calculated values

    Raises:
        InputRangeError: If P or T outside valid range
        InvalidStateError: If conditions on saturation line (two-phase)
        NumericalInstabilityError: If calculation fails due to numerical issues
    """
    # Validate inputs and assign region
    assigned_region, diagnostic = router.assign_region(pressure_pa, temperature_k)

    # Dispatch to appropriate region calculator
    if assigned_region == models.Region.REGION1:
        props = region1.calculate_properties(pressure_pa, temperature_k)
    elif assigned_region == models.Region.REGION2:
        props = region2.calculate_properties(pressure_pa, temperature_k)
    elif assigned_region == models.Region.REGION3:
        props = region3.calculate_properties(pressure_pa, temperature_k)
    else:
        raise ValueError(f"Unknown region: {assigned_region}")

    # Create SteamProperties object with Pint Quantity units
    return models.SteamProperties(
        pressure=ureg.Quantity(pressure_pa, "Pa"),
        temperature=ureg.Quantity(temperature_k, "K"),
        enthalpy=ureg.Quantity(props["enthalpy_kJ_kg"], "kJ/kg"),
        entropy=ureg.Quantity(props["entropy_kJ_kg_K"], "kJ/(kg·K)"),
        internal_energy=ureg.Quantity(props["internal_energy_kJ_kg"], "kJ/kg"),
        density=ureg.Quantity(props["density_kg_m3"], "kg/m³"),
    )


__all__ = ["calculate_properties"]
