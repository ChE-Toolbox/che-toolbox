"""SteamTable: User-facing API for IAPWS-IF97 property calculations.

Provides convenient methods to calculate steam and water properties
at arbitrary pressure-temperature conditions with automatic region routing.
All methods accept and return Pint Quantity objects for unit safety.
"""

from pint import Quantity

from . import dispatcher, models
from .regions import saturation
from .units import ureg


class SteamTable:
    """Main API for calculating thermodynamic properties of steam and water.

    All input methods accept Pint Quantity objects with units.
    All return values are Pint Quantity objects with embedded units.

    Example:
        >>> from iapws_if97 import SteamTable, ureg
        >>> steam = SteamTable()
        >>> h = steam.h_pt(10 * ureg.MPa, 500 * ureg.K)
        >>> print(h)  # Returns Quantity in kJ/kg
    """

    def h_pt(self, pressure: Quantity, temperature: Quantity) -> Quantity:
        """Calculate specific enthalpy at given pressure and temperature.

        Args:
            pressure: Pressure as Pint Quantity (e.g., 10 * ureg.MPa)
            temperature: Temperature as Pint Quantity (e.g., 500 * ureg.K)

        Returns:
            Specific enthalpy as Pint Quantity in kJ/kg

        Raises:
            InputRangeError: If P or T outside valid IAPWS-IF97 range
            InvalidStateError: If P-T point is on saturation line
            NumericalInstabilityError: If calculation fails numerically
        """
        # Convert to base SI units (Pa, K)
        p_pa = pressure.to("Pa").magnitude
        t_k = temperature.to("K").magnitude

        # Calculate properties
        props = dispatcher.calculate_properties(p_pa, t_k)

        return props.enthalpy

    def s_pt(self, pressure: Quantity, temperature: Quantity) -> Quantity:
        """Calculate specific entropy at given pressure and temperature.

        Args:
            pressure: Pressure as Pint Quantity
            temperature: Temperature as Pint Quantity

        Returns:
            Specific entropy as Pint Quantity in kJ/(kg·K)
        """
        p_pa = pressure.to("Pa").magnitude
        t_k = temperature.to("K").magnitude
        props = dispatcher.calculate_properties(p_pa, t_k)
        return props.entropy

    def u_pt(self, pressure: Quantity, temperature: Quantity) -> Quantity:
        """Calculate specific internal energy at given pressure and temperature.

        Args:
            pressure: Pressure as Pint Quantity
            temperature: Temperature as Pint Quantity

        Returns:
            Specific internal energy as Pint Quantity in kJ/kg
        """
        p_pa = pressure.to("Pa").magnitude
        t_k = temperature.to("K").magnitude
        props = dispatcher.calculate_properties(p_pa, t_k)
        return props.internal_energy

    def rho_pt(self, pressure: Quantity, temperature: Quantity) -> Quantity:
        """Calculate density at given pressure and temperature.

        Args:
            pressure: Pressure as Pint Quantity
            temperature: Temperature as Pint Quantity

        Returns:
            Density as Pint Quantity in kg/m³
        """
        p_pa = pressure.to("Pa").magnitude
        t_k = temperature.to("K").magnitude
        props = dispatcher.calculate_properties(p_pa, t_k)
        return props.density

    def T_sat(self, pressure: Quantity) -> models.SaturationProperties:
        """Calculate saturation temperature and properties at given pressure.

        Args:
            pressure: Saturation pressure as Pint Quantity

        Returns:
            SaturationProperties dataclass with:
            - saturation_temperature: Temperature at saturation
            - saturation_pressure: Input pressure
            - enthalpy_liquid, enthalpy_vapor: Liquid and vapor enthalpies
            - entropy_liquid, entropy_vapor: Liquid and vapor entropies
            - density_liquid, density_vapor: Liquid and vapor densities
            - heat_of_vaporization: Latent heat (h_g - h_f)

        Raises:
            InputRangeError: If pressure outside saturation range
        """
        p_pa = pressure.to("Pa").magnitude

        # Calculate saturation properties
        sat_data = saturation.calculate_saturation_temperature(p_pa)

        # Convert to SaturationProperties dataclass with Pint quantities
        return models.SaturationProperties(
            saturation_temperature=sat_data["saturation_temperature_K"] * ureg.K,
            saturation_pressure=sat_data["saturation_pressure_Pa"] * ureg.Pa,
            enthalpy_liquid=sat_data["enthalpy_liquid_kJ_kg"] * ureg.kJ / ureg.kg,
            enthalpy_vapor=sat_data["enthalpy_vapor_kJ_kg"] * ureg.kJ / ureg.kg,
            entropy_liquid=sat_data["entropy_liquid_kJ_kg_K"] * ureg.kJ / (ureg.kg * ureg.K),
            entropy_vapor=sat_data["entropy_vapor_kJ_kg_K"] * ureg.kJ / (ureg.kg * ureg.K),
            density_liquid=sat_data["density_liquid_kg_m3"] * ureg.kg / ureg.m**3,
            density_vapor=sat_data["density_vapor_kg_m3"] * ureg.kg / ureg.m**3,
        )

    def P_sat(self, temperature: Quantity) -> models.SaturationProperties:
        """Calculate saturation pressure and properties at given temperature.

        Args:
            temperature: Saturation temperature as Pint Quantity

        Returns:
            SaturationProperties dataclass with all saturation properties

        Raises:
            InputRangeError: If temperature outside saturation range
        """
        t_k = temperature.to("K").magnitude

        # Calculate saturation properties
        sat_data = saturation.calculate_saturation_pressure(t_k)

        # Convert to SaturationProperties dataclass with Pint quantities
        return models.SaturationProperties(
            saturation_temperature=sat_data["saturation_temperature_K"] * ureg.K,
            saturation_pressure=sat_data["saturation_pressure_Pa"] * ureg.Pa,
            enthalpy_liquid=sat_data["enthalpy_liquid_kJ_kg"] * ureg.kJ / ureg.kg,
            enthalpy_vapor=sat_data["enthalpy_vapor_kJ_kg"] * ureg.kJ / ureg.kg,
            entropy_liquid=sat_data["entropy_liquid_kJ_kg_K"] * ureg.kJ / (ureg.kg * ureg.K),
            entropy_vapor=sat_data["entropy_vapor_kJ_kg_K"] * ureg.kJ / (ureg.kg * ureg.K),
            density_liquid=sat_data["density_liquid_kg_m3"] * ureg.kg / ureg.m**3,
            density_vapor=sat_data["density_vapor_kg_m3"] * ureg.kg / ureg.m**3,
        )

    # Legacy methods for backward compatibility
    def properties(self, pressure_pa: float, temperature_k: float) -> models.SteamProperties:
        """Calculate steam/water properties at given P-T conditions.

        Legacy method - prefer using h_pt(), s_pt(), etc. with Pint Quantities.

        Args:
            pressure_pa: Absolute pressure in Pa (float)
            temperature_k: Temperature in K (float)

        Returns:
            SteamProperties dataclass with enthalpy, entropy, internal energy, density
        """
        return dispatcher.calculate_properties(pressure_pa, temperature_k)

    def enthalpy_pt(self, pressure_pa: float, temperature_k: float) -> Quantity:
        """Get enthalpy at given P-T (legacy float interface).

        Args:
            pressure_pa: Absolute pressure in Pa
            temperature_k: Temperature in K

        Returns:
            Pint Quantity object with enthalpy in kJ/kg
        """
        props = self.properties(pressure_pa, temperature_k)
        return props.enthalpy

    def entropy_pt(self, pressure_pa: float, temperature_k: float) -> Quantity:
        """Get entropy at given P-T (legacy float interface)."""
        props = self.properties(pressure_pa, temperature_k)
        return props.entropy

    def density_pt(self, pressure_pa: float, temperature_k: float) -> Quantity:
        """Get density at given P-T (legacy float interface)."""
        props = self.properties(pressure_pa, temperature_k)
        return props.density

    def internal_energy_pt(self, pressure_pa: float, temperature_k: float) -> Quantity:
        """Get internal energy at given P-T (legacy float interface)."""
        props = self.properties(pressure_pa, temperature_k)
        return props.internal_energy


__all__ = ["SteamTable"]
