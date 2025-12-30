"""Unit conversion handler using Pint.

This module provides a protocol-based interface for unit conversions, with a Pint-based
implementation. The protocol allows for future alternative implementations if needed.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from pint import DimensionalityError as PintDimensionalityError
from pint import UndefinedUnitError

from chemeng_core.units.registry import get_unit_registry

if TYPE_CHECKING:
    from pint import Unit as PintUnit
    from pint import UnitRegistry

    from chemeng_core.compounds.models import QuantityDTO


class UnitHandler(Protocol):
    """Protocol for unit conversion operations.

    This protocol defines the interface for unit handlers, allowing for
    different implementations while maintaining a consistent API.
    """

    def convert(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert a scalar value between units.

        Args:
            value: Numerical value in from_unit
            from_unit: Source unit string
            to_unit: Target unit string

        Returns:
            Converted value in to_unit

        Raises:
            DimensionalityError: If units are incompatible
            UndefinedUnitError: If unit string is invalid
        """
        ...

    def convert_quantity(self, quantity: QuantityDTO, to_unit: str) -> QuantityDTO:
        """Convert a QuantityDTO to different units.

        Args:
            quantity: Source quantity with magnitude and unit
            to_unit: Target unit string

        Returns:
            New QuantityDTO in target units

        Raises:
            DimensionalityError: If units are incompatible
        """
        ...

    def is_compatible(self, unit1: str, unit2: str) -> bool:
        """Check if two units have compatible dimensions.

        Args:
            unit1: First unit string
            unit2: Second unit string

        Returns:
            True if units are dimensionally compatible
        """
        ...

    def parse_unit(self, unit_str: str) -> PintUnit:
        """Parse a unit string into a Pint Unit object.

        Args:
            unit_str: Unit string to parse

        Returns:
            Pint Unit object

        Raises:
            UndefinedUnitError: If unit string is invalid
        """
        ...


class PintUnitHandler:
    """Pint-based implementation of UnitHandler protocol.

    This class provides unit conversion operations using the Pint library,
    with proper error handling and dimensional consistency checks.

    Attributes:
        ureg: Shared Pint UnitRegistry instance
    """

    def __init__(self, ureg: UnitRegistry | None = None) -> None:
        """Initialize handler with optional custom UnitRegistry.

        Args:
            ureg: Optional custom UnitRegistry. If None, uses shared singleton.
        """
        self.ureg = ureg if ureg is not None else get_unit_registry()

    def convert(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert a scalar value between units.

        Args:
            value: Numerical value in from_unit
            from_unit: Source unit string
            to_unit: Target unit string

        Returns:
            Converted value in to_unit

        Raises:
            DimensionalityError: If units are incompatible
            UndefinedUnitError: If unit string is invalid

        Examples:
            >>> handler = PintUnitHandler()
            >>> handler.convert(100, "degC", "kelvin")
            373.15
            >>> handler.convert(101325, "pascal", "bar")
            1.01325
        """
        try:
            quantity = self.ureg.Quantity(value, from_unit)
            converted = quantity.to(to_unit)
            return float(converted.magnitude)
        except PintDimensionalityError as e:
            # Re-raise with custom exception for cleaner API
            raise DimensionalityError(
                f"Cannot convert from '{from_unit}' to '{to_unit}': incompatible dimensions"
            ) from e
        except UndefinedUnitError as e:
            raise UndefinedUnitError(f"Invalid unit: {e}") from e

    def convert_quantity(self, quantity: QuantityDTO, to_unit: str) -> QuantityDTO:
        """Convert a QuantityDTO to different units.

        Args:
            quantity: Source quantity with magnitude and unit
            to_unit: Target unit string

        Returns:
            New QuantityDTO in target units

        Raises:
            DimensionalityError: If units are incompatible

        Examples:
            >>> from chemeng_core.compounds.models import QuantityDTO
            >>> handler = PintUnitHandler()
            >>> q = QuantityDTO(magnitude=647.096, unit="kelvin")
            >>> q_celsius = handler.convert_quantity(q, "degC")
            >>> q_celsius.magnitude
            373.946
        """
        # Import here to avoid circular dependency
        from chemeng_core.compounds.models import QuantityDTO

        converted_value = self.convert(quantity.magnitude, quantity.unit, to_unit)
        return QuantityDTO(magnitude=converted_value, unit=to_unit)

    def is_compatible(self, unit1: str, unit2: str) -> bool:
        """Check if two units have compatible dimensions.

        Args:
            unit1: First unit string
            unit2: Second unit string

        Returns:
            True if units are dimensionally compatible

        Examples:
            >>> handler = PintUnitHandler()
            >>> handler.is_compatible("kelvin", "degC")
            True
            >>> handler.is_compatible("kelvin", "pascal")
            False
        """
        try:
            u1 = self.ureg.parse_units(unit1)
            u2 = self.ureg.parse_units(unit2)
            return u1.dimensionality == u2.dimensionality
        except (UndefinedUnitError, AttributeError):
            return False

    def parse_unit(self, unit_str: str) -> PintUnit:
        """Parse a unit string into a Pint Unit object.

        Args:
            unit_str: Unit string to parse

        Returns:
            Pint Unit object

        Raises:
            UndefinedUnitError: If unit string is invalid

        Examples:
            >>> handler = PintUnitHandler()
            >>> unit = handler.parse_unit("kg/m**3")
            >>> str(unit)
            'kilogram / meter ** 3'
        """
        return self.ureg.parse_units(unit_str)


class DimensionalityError(Exception):
    """Exception raised when attempting to convert between incompatible units."""

    pass
