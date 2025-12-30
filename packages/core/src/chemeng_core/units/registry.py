"""Pint UnitRegistry singleton for chemical engineering units.

This module provides a shared UnitRegistry instance configured with chemical engineering
units. Using a singleton ensures consistent unit definitions across the application.
"""

from pint import UnitRegistry

# Create shared UnitRegistry instance
# Pint includes chemical engineering units by default:
# - Temperature: K, degC, degF, degR
# - Pressure: Pa, bar, atm, psi, mmHg, torr
# - Energy: J, cal, BTU
# - Mass/Volume: kg, g, lb, m**3, L, ft**3
# - Amount: mol, kmol
_ureg: UnitRegistry | None = None


def get_unit_registry() -> UnitRegistry:
    """Get or create the shared UnitRegistry instance.

    Returns:
        Shared Pint UnitRegistry configured for chemical engineering
    """
    global _ureg
    if _ureg is None:
        _ureg = UnitRegistry()
        # Enable automatic conversion context for temperature offsets
        _ureg.autoconvert_offset_to_baseunit = False
    return _ureg


# Convenience alias
ureg = get_unit_registry()
Q_ = ureg.Quantity
