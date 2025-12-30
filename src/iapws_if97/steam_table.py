"""SteamTable: User-facing API for IAPWS-IF97 property calculations.

Provides convenient methods to calculate steam and water properties
at arbitrary pressure-temperature conditions with automatic region routing.
"""

from typing import Union

from . import dispatcher, models
from .units import ureg


class SteamTable:
    """Main API for calculating thermodynamic properties of steam and water.

    Example:
        st = SteamTable()
        props = st.properties(pressure_pa=3e6, temperature_k=300)
        print(f"Enthalpy: {props.enthalpy}")
        print(f"Density: {props.density}")
    """

    def properties(
        self, pressure_pa: float, temperature_k: float
    ) -> models.SteamProperties:
        """Calculate steam/water properties at given P-T conditions.

        Args:
            pressure_pa: Absolute pressure in Pa
            temperature_k: Temperature in K

        Returns:
            SteamProperties dataclass with enthalpy, entropy, internal energy, density

        Raises:
            InputRangeError: If P or T outside valid IAPWS-IF97 range
            InvalidStateError: If P-T point is on saturation line
            NumericalInstabilityError: If calculation fails numerically
        """
        return dispatcher.calculate_properties(pressure_pa, temperature_k)

    def enthalpy_pt(self, pressure_pa: float, temperature_k: float) -> object:
        """Get enthalpy at given P-T as Pint Quantity (kJ/kg).

        Args:
            pressure_pa: Absolute pressure in Pa
            temperature_k: Temperature in K

        Returns:
            Pint Quantity object with enthalpy in kJ/kg
        """
        props = self.properties(pressure_pa, temperature_k)
        return props.enthalpy

    def entropy_pt(self, pressure_pa: float, temperature_k: float) -> object:
        """Get entropy at given P-T as Pint Quantity (kJ/(kg·K)).

        Args:
            pressure_pa: Absolute pressure in Pa
            temperature_k: Temperature in K

        Returns:
            Pint Quantity object with entropy in kJ/(kg·K)
        """
        props = self.properties(pressure_pa, temperature_k)
        return props.entropy

    def density_pt(self, pressure_pa: float, temperature_k: float) -> object:
        """Get density at given P-T as Pint Quantity (kg/m³).

        Args:
            pressure_pa: Absolute pressure in Pa
            temperature_k: Temperature in K

        Returns:
            Pint Quantity object with density in kg/m³
        """
        props = self.properties(pressure_pa, temperature_k)
        return props.density

    def internal_energy_pt(self, pressure_pa: float, temperature_k: float) -> object:
        """Get internal energy at given P-T as Pint Quantity (kJ/kg).

        Args:
            pressure_pa: Absolute pressure in Pa
            temperature_k: Temperature in K

        Returns:
            Pint Quantity object with internal energy in kJ/kg
        """
        props = self.properties(pressure_pa, temperature_k)
        return props.internal_energy


__all__ = ["SteamTable"]
