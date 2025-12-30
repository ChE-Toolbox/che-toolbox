"""IAPWS-IF97 Steam Property Calculations Library.

High-accuracy thermodynamic property calculations for steam/water across
all IAPWS-IF97 regions (1, 2, 3) and saturation line, with Pint unit handling
and comprehensive validation against official IAPWS reference tables.

Main API:
    - SteamTable: Convenient class for property lookups
    - SteamProperties: Return type for single-phase calculations
    - SaturationProperties: Return type for saturation line calculations
    - Region: Enum for thermodynamic region identification

Exceptions:
    - InputRangeError: Pressure/temperature out of valid range
    - NumericalInstabilityError: Singularities or convergence failure
    - InvalidStateError: Two-phase conditions in single-phase API

Units:
    - ureg: Pint UnitRegistry singleton for unit handling
    - All properties returned with embedded units (Pint Quantity objects)

Example:
    >>> from iapws_if97 import SteamTable, ureg
    >>> steam = SteamTable()
    >>> h = steam.h_pt(10 * ureg.MPa, 500 * ureg.K)
    >>> print(h)  # 3373.7 kJ/kg ± 0.03%
"""

__version__ = "1.0.0"
__author__ = "ChemEng Toolbox"

from .exceptions import (
    InvalidStateError,
    InputRangeError,
    NumericalInstabilityError,
    SteamTableError,
)
from .models import Region, SaturationProperties, SteamProperties
from .steam_table import SteamTable
from .units import ureg

__all__ = [
    "SteamTable",
    "SteamProperties",
    "SaturationProperties",
    "Region",
    "InputRangeError",
    "NumericalInstabilityError",
    "InvalidStateError",
    "SteamTableError",
    "ureg",
]
