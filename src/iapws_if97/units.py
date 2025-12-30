"""Pint unit registry and SI unit definitions for IAPWS-IF97.

Provides a singleton UnitRegistry configured for steam property calculations
with proper definitions for all SI units used in thermodynamics.
"""

from pint import UnitRegistry

# Singleton UnitRegistry instance
ureg = UnitRegistry()

# Define standard SI units (most are already in Pint's default set)
# Explicitly define dimensionless quantities and any custom units if needed

# Configure ureg for thermodynamic calculations
ureg.define("specific_enthalpy = kilojoule / kilogram = kJ/kg")
ureg.define("specific_entropy = kilojoule / kilogram / kelvin = kJ/(kg·K)")
ureg.define("specific_volume = cubic_meter / kilogram = m³/kg")
ureg.define("specific_energy = kilojoule / kilogram = kJ/kg")

# Standard SI base units used in IAPWS-IF97:
# - Pressure (Pa): pascal
# - Temperature (K): kelvin
# - Density (kg/m³): kilogram per cubic meter
# - Enthalpy (kJ/kg): kilojoule per kilogram
# - Entropy (kJ/(kg·K)): kilojoule per kilogram per kelvin
# - Internal energy (kJ/kg): kilojoule per kilogram

# Pressure conversions
ureg.define("MPa = 1e6 * pascal")
ureg.define("bar = 1e5 * pascal")
ureg.define("atm = 101325 * pascal")
ureg.define("psi = 6894.76 * pascal")

# Temperature conversions (handled by Pint's offset support)
# Note: Celsius and Fahrenheit are offset scales, Pint handles these

# Configure string representation
ureg.default_format = ".4g"

__all__ = ["ureg"]
