"""Data models for IAPWS-IF97 steam properties.

Defines enums and dataclasses for representing thermodynamic states,
regions, and property results.
"""

from dataclasses import dataclass
from enum import Enum


class Region(Enum):
    """IAPWS-IF97 thermodynamic region identification.

    Enum values map to specific pressure-temperature domains:
    - REGION1: Compressed liquid water
    - REGION2: Superheated steam/vapor
    - REGION3: Supercritical fluid
    - SATURATION: Two-phase region (liquid-vapor equilibrium)
    """

    REGION1 = 1
    REGION2 = 2
    REGION3 = 3
    SATURATION = 99

    def __str__(self) -> str:
        """Return human-readable region name."""
        names = {
            1: "Region 1 (Compressed Liquid)",
            2: "Region 2 (Superheated Steam)",
            3: "Region 3 (Supercritical)",
            99: "Saturation Line",
        }
        return names[self.value]


@dataclass(frozen=True)
class SteamProperties:
    """Thermodynamic properties at specified pressure-temperature conditions.

    All properties are Pint Quantity objects with embedded unit information.
    The dataclass is immutable (frozen=True) for thread safety.

    Attributes:
        pressure: Input pressure (Pa internally, Pint Quantity)
        temperature: Input temperature (K internally, Pint Quantity)
        enthalpy: Specific enthalpy h (kJ/kg)
        entropy: Specific entropy s (kJ/(kg·K))
        internal_energy: Specific internal energy u (kJ/kg)
        density: Density ρ (kg/m³)
        specific_heat_p: Specific heat at constant pressure cp (kJ/(kg·K)), optional
        specific_heat_v: Specific heat at constant volume cv (kJ/(kg·K)), optional
        speed_of_sound: Speed of sound w (m/s), optional
    """

    pressure: object  # Pint Quantity
    temperature: object  # Pint Quantity
    enthalpy: object  # Pint Quantity
    entropy: object  # Pint Quantity
    internal_energy: object  # Pint Quantity
    density: object  # Pint Quantity
    specific_heat_p: object | None = None  # Pint Quantity or None
    specific_heat_v: object | None = None  # Pint Quantity or None
    speed_of_sound: object | None = None  # Pint Quantity or None

    def __repr__(self) -> str:
        """Return detailed string representation of properties."""
        return (
            f"SteamProperties(P={self.pressure}, T={self.temperature}, "
            f"h={self.enthalpy}, s={self.entropy}, u={self.internal_energy}, "
            f"ρ={self.density})"
        )


@dataclass(frozen=True)
class SaturationProperties:
    """Thermodynamic properties at saturation line (liquid-vapor equilibrium).

    All properties are Pint Quantity objects. Subscript 'f' denotes saturated
    liquid, 'g' denotes saturated vapor.

    Attributes:
        saturation_temperature: Saturation temperature T_sat (K)
        saturation_pressure: Saturation pressure P_sat (Pa)
        enthalpy_liquid: Saturated liquid enthalpy h_f (kJ/kg)
        entropy_liquid: Saturated liquid entropy s_f (kJ/(kg·K))
        density_liquid: Saturated liquid density ρ_f (kg/m³)
        enthalpy_vapor: Saturated vapor enthalpy h_g (kJ/kg)
        entropy_vapor: Saturated vapor entropy s_g (kJ/(kg·K))
        density_vapor: Saturated vapor density ρ_g (kg/m³)
    """

    saturation_temperature: object  # Pint Quantity
    saturation_pressure: object  # Pint Quantity
    enthalpy_liquid: object  # Pint Quantity
    entropy_liquid: object  # Pint Quantity
    density_liquid: object  # Pint Quantity
    enthalpy_vapor: object  # Pint Quantity
    entropy_vapor: object  # Pint Quantity
    density_vapor: object  # Pint Quantity

    def heat_of_vaporization(self) -> object:
        """Calculate latent heat: h_fg = h_g - h_f.

        Returns:
            Latent heat as Pint Quantity (kJ/kg)
        """
        return self.enthalpy_vapor - self.enthalpy_liquid

    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"SaturationProperties(T_sat={self.saturation_temperature}, "
            f"P_sat={self.saturation_pressure}, "
            f"h_f={self.enthalpy_liquid}, h_g={self.enthalpy_vapor})"
        )
