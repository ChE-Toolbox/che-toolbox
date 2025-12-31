"""
Compound API Contract Definitions

This file defines the Python API interfaces for the chemical compound database.
These are CONTRACT definitions - not implementations. They specify the expected
behavior that implementations must satisfy.

Feature: 001-data-foundations
Date: 2025-12-29
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import Protocol, runtime_checkable

from pint import Quantity, UnitRegistry
from pydantic import BaseModel, Field

# =============================================================================
# Pydantic Models (Data Transfer Objects)
# =============================================================================


class QuantityDTO(BaseModel):
    """Serializable representation of a physical quantity."""

    magnitude: float = Field(..., description="Numerical value")
    unit: str = Field(..., description="Pint-compatible unit string")

    def to_pint(self, ureg: UnitRegistry) -> Quantity:
        """Convert to Pint Quantity."""
        ...

    @classmethod
    def from_pint(cls, q: Quantity) -> "QuantityDTO":
        """Create from Pint Quantity."""
        ...


class CriticalPropertiesDTO(BaseModel):
    """Critical point thermodynamic properties."""

    temperature: QuantityDTO = Field(..., description="Critical temperature (T_c)")
    pressure: QuantityDTO = Field(..., description="Critical pressure (P_c)")
    density: QuantityDTO = Field(..., description="Critical density (rho_c)")
    acentric_factor: float = Field(..., description="Acentric factor (omega)")


class PhasePropertiesDTO(BaseModel):
    """Phase transition properties."""

    normal_boiling_point: QuantityDTO = Field(..., description="Boiling point at 1 atm")
    triple_point_temperature: QuantityDTO | None = Field(
        None, description="Triple point temperature"
    )
    triple_point_pressure: QuantityDTO | None = Field(None, description="Triple point pressure")


class SourceAttributionDTO(BaseModel):
    """Data source attribution metadata."""

    name: str = Field(..., description="Source name")
    url: str = Field(..., description="Reference URL")
    retrieved_date: date = Field(..., description="Date data was retrieved")
    version: str | None = Field(None, description="Source version")
    notes: str | None = Field(None, description="Additional notes")


class CompoundDTO(BaseModel):
    """Complete compound data transfer object."""

    cas_number: str = Field(..., description="CAS Registry Number (primary key)")
    name: str = Field(..., description="Common name")
    formula: str = Field(..., description="Chemical formula")
    iupac_name: str = Field(..., description="IUPAC systematic name")
    coolprop_name: str = Field(..., description="CoolProp identifier")
    aliases: list[str] = Field(default_factory=list, description="Alternative names")
    molecular_weight: QuantityDTO = Field(..., description="Molecular weight")
    critical_properties: CriticalPropertiesDTO
    phase_properties: PhasePropertiesDTO
    source: SourceAttributionDTO


class DatabaseMetadataDTO(BaseModel):
    """Database-level metadata."""

    version: str = Field(..., description="Data format version")
    source: str = Field(..., description="Primary data source")
    retrieved_date: date = Field(..., description="Date data was retrieved")
    attribution: str = Field(..., description="Full attribution statement")
    compound_count: int = Field(..., ge=1, description="Number of compounds")


class CompoundDatabaseDTO(BaseModel):
    """Complete database container."""

    metadata: DatabaseMetadataDTO
    compounds: list[CompoundDTO]


# =============================================================================
# Service Interfaces (Contracts)
# =============================================================================


@runtime_checkable
class CompoundRegistry(Protocol):
    """
    Contract for compound lookup and retrieval.

    Implementations must provide efficient lookup by multiple identifiers
    and support iteration over all compounds.
    """

    def get_by_cas(self, cas_number: str) -> CompoundDTO | None:
        """
        Retrieve compound by CAS number.

        Args:
            cas_number: CAS Registry Number (e.g., "7732-18-5")

        Returns:
            CompoundDTO if found, None otherwise

        Example:
            >>> registry.get_by_cas("7732-18-5")
            CompoundDTO(name="Water", ...)
        """
        ...

    def get_by_name(self, name: str) -> CompoundDTO | None:
        """
        Retrieve compound by common name (case-insensitive).

        Args:
            name: Common name (e.g., "Water", "water", "WATER")

        Returns:
            CompoundDTO if found, None otherwise
        """
        ...

    def get_by_formula(self, formula: str) -> list[CompoundDTO]:
        """
        Retrieve compounds by chemical formula.

        Args:
            formula: Chemical formula (e.g., "H2O")

        Returns:
            List of matching compounds (may be empty)

        Note:
            Multiple compounds may have the same formula (isomers).
        """
        ...

    def search(self, query: str) -> list[CompoundDTO]:
        """
        Search compounds by name, formula, or alias.

        Args:
            query: Search string (case-insensitive)

        Returns:
            List of matching compounds, ordered by relevance
        """
        ...

    def list_all(self) -> list[CompoundDTO]:
        """
        List all compounds in the database.

        Returns:
            List of all compounds
        """
        ...

    @property
    def metadata(self) -> DatabaseMetadataDTO:
        """Database metadata."""
        ...


@runtime_checkable
class UnitHandler(Protocol):
    """
    Contract for unit conversions.

    Implementations must support all standard chemical engineering units
    and maintain dimensional consistency.
    """

    def convert(self, value: float, from_unit: str, to_unit: str) -> float:
        """
        Convert value between compatible units.

        Args:
            value: Numerical value to convert
            from_unit: Source unit string
            to_unit: Target unit string

        Returns:
            Converted value

        Raises:
            DimensionalityError: If units are incompatible

        Example:
            >>> handler.convert(100, "degC", "kelvin")
            373.15
        """
        ...

    def convert_quantity(self, quantity: QuantityDTO, to_unit: str) -> QuantityDTO:
        """
        Convert a QuantityDTO to different units.

        Args:
            quantity: Source quantity with magnitude and unit
            to_unit: Target unit string

        Returns:
            New QuantityDTO with converted value
        """
        ...

    def is_compatible(self, unit1: str, unit2: str) -> bool:
        """
        Check if two units are dimensionally compatible.

        Args:
            unit1: First unit string
            unit2: Second unit string

        Returns:
            True if units can be converted, False otherwise
        """
        ...

    def parse_unit(self, unit_string: str) -> Quantity:
        """
        Parse a unit string into a Pint unit.

        Args:
            unit_string: Unit string (e.g., "kg/m**3")

        Returns:
            Pint Quantity with magnitude 1 and parsed unit

        Raises:
            UndefinedUnitError: If unit string is not recognized
        """
        ...


class CompoundLoader(ABC):
    """
    Abstract base class for compound data loading.

    Implementations load compound data from various sources
    (JSON files, CoolProp, etc.) into the standard format.
    """

    @abstractmethod
    def load(self) -> CompoundDatabaseDTO:
        """
        Load compound database from source.

        Returns:
            Complete database with metadata and compounds

        Raises:
            FileNotFoundError: If data file not found
            ValidationError: If data fails schema validation
        """
        ...

    @abstractmethod
    def validate(self, database: CompoundDatabaseDTO) -> list[str]:
        """
        Validate database against schema and constraints.

        Args:
            database: Database to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        ...


# =============================================================================
# Exception Types
# =============================================================================


class CompoundNotFoundError(Exception):
    """Raised when a compound lookup fails."""

    def __init__(self, identifier: str, identifier_type: str = "cas_number"):
        self.identifier = identifier
        self.identifier_type = identifier_type
        super().__init__(f"Compound not found: {identifier_type}='{identifier}'")


class DimensionalityError(Exception):
    """Raised when unit conversion fails due to incompatible dimensions."""

    def __init__(self, from_unit: str, to_unit: str):
        self.from_unit = from_unit
        self.to_unit = to_unit
        super().__init__(
            f"Cannot convert from '{from_unit}' to '{to_unit}': incompatible dimensions"
        )


class ValidationError(Exception):
    """Raised when data fails schema validation."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__(f"Validation failed: {len(errors)} error(s)")


# =============================================================================
# Factory Functions (Contract)
# =============================================================================


def create_registry() -> CompoundRegistry:
    """
    Create and return the default compound registry.

    Returns:
        Initialized CompoundRegistry with all compounds loaded

    Raises:
        FileNotFoundError: If compound data file not found
    """
    ...


def create_unit_handler() -> UnitHandler:
    """
    Create and return the default unit handler.

    Returns:
        Initialized UnitHandler with chemical engineering units
    """
    ...


def get_compound(identifier: str) -> CompoundDTO:
    """
    Convenience function to get a compound by any identifier.

    Tries lookup by CAS number first, then name, then formula.

    Args:
        identifier: CAS number, name, or formula

    Returns:
        CompoundDTO

    Raises:
        CompoundNotFoundError: If no compound matches
    """
    ...
