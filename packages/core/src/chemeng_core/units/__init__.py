"""Unit handling module using Pint.

This module provides unit conversion and dimensional analysis capabilities
using the Pint library.

Public API:
    - create_unit_handler: Factory function to create a UnitHandler
    - PintUnitHandler: Main unit handler implementation
    - DimensionalityError: Exception for incompatible unit conversions
    - get_unit_registry: Get the shared Pint UnitRegistry
"""

from chemeng_core.units.handler import DimensionalityError, PintUnitHandler
from chemeng_core.units.registry import get_unit_registry


def create_unit_handler() -> PintUnitHandler:
    """Create a PintUnitHandler instance with the shared registry.

    Returns:
        PintUnitHandler instance

    Examples:
        >>> handler = create_unit_handler()
        >>> celsius = handler.convert(373.15, "kelvin", "degC")
        >>> print(f"{celsius:.2f}")
        100.00
    """
    return PintUnitHandler()


__all__ = [
    "DimensionalityError",
    "PintUnitHandler",
    "create_unit_handler",
    "get_unit_registry",
]
