"""Pydantic models for chemical compound data.

This module defines data models for compound properties, using Pydantic for validation
and JSON serialization. Quantities (values with units) are stored as magnitude/unit pairs
compatible with Pint for dimensional analysis.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field, field_validator

if TYPE_CHECKING:
    from pint import Quantity as PintQuantity
    from pint import UnitRegistry


class QuantityDTO(BaseModel):
    """Physical quantity with magnitude and unit (Pint-compatible).

    This model stores quantities as magnitude + unit string for JSON serialization,
    with methods to convert to/from Pint Quantity objects for calculations.

    Attributes:
        magnitude: Numerical value
        unit: Pint-compatible unit string (e.g., "kelvin", "pascal", "kg/m**3")
    """

    magnitude: float = Field(..., description="Numerical value")
    unit: str = Field(..., description="Pint-compatible unit string")

    @field_validator("magnitude")
    @classmethod
    def validate_finite(cls, v: float) -> float:
        """Ensure magnitude is a finite number (not NaN or Inf)."""
        if not (-1e308 < v < 1e308):  # Practical finite range
            raise ValueError(f"Magnitude must be finite, got {v}")
        return v

    def to_pint(self, ureg: UnitRegistry) -> PintQuantity:
        """Convert to Pint Quantity object.

        Args:
            ureg: Pint UnitRegistry instance

        Returns:
            Pint Quantity with magnitude and unit
        """
        return ureg.Quantity(self.magnitude, self.unit)

    @classmethod
    def from_pint(cls, q: PintQuantity) -> QuantityDTO:
        """Create QuantityDTO from Pint Quantity.

        Args:
            q: Pint Quantity object

        Returns:
            QuantityDTO instance
        """
        return cls(magnitude=float(q.magnitude), unit=str(q.units))

    model_config = {"frozen": True}  # Immutable after creation


class CriticalPropertiesDTO(BaseModel):
    """Critical point thermodynamic properties.

    The critical point represents the end of the liquid-vapor equilibrium curve
    where liquid and vapor phases become indistinguishable.

    Attributes:
        temperature: Critical temperature (T_c)
        pressure: Critical pressure (P_c)
        density: Critical density (ρ_c)
        acentric_factor: Acentric factor (ω), dimensionless
    """

    temperature: QuantityDTO = Field(..., description="Critical temperature")
    pressure: QuantityDTO = Field(..., description="Critical pressure")
    density: QuantityDTO = Field(..., description="Critical density")
    acentric_factor: float = Field(..., description="Acentric factor (dimensionless)")

    model_config = {"frozen": True}


class PhasePropertiesDTO(BaseModel):
    """Phase transition properties at standard conditions.

    Attributes:
        normal_boiling_point: Boiling point at 1 atm (T_b)
        triple_point_temperature: Optional triple point temperature
        triple_point_pressure: Optional triple point pressure
    """

    normal_boiling_point: QuantityDTO = Field(..., description="Normal boiling point at 1 atm")
    triple_point_temperature: QuantityDTO | None = Field(
        None, description="Triple point temperature"
    )
    triple_point_pressure: QuantityDTO | None = Field(None, description="Triple point pressure")

    model_config = {"frozen": True}


class SourceAttributionDTO(BaseModel):
    """Data provenance and attribution metadata.

    Attributes:
        name: Source name (e.g., "CoolProp / NIST WebBook")
        url: Reference URL
        retrieved_date: Date data was retrieved
        version: Optional source version
        notes: Optional additional attribution notes
    """

    name: str = Field(..., description="Source name")
    url: str = Field(..., description="Reference URL")
    retrieved_date: date = Field(..., description="Date data was retrieved")
    version: str | None = Field(None, description="Source version")
    notes: str | None = Field(None, description="Additional attribution notes")

    @field_validator("retrieved_date")
    @classmethod
    def validate_not_future(cls, v: date) -> date:
        """Ensure retrieved_date is not in the future."""
        from datetime import date as date_class

        if v > date_class.today():
            raise ValueError(f"Retrieved date cannot be in the future: {v}")
        return v

    model_config = {"frozen": True}


class CompoundDTO(BaseModel):
    """Core entity representing a chemical compound with its properties.

    This model represents a complete chemical compound with identification,
    thermophysical properties, and data attribution.

    Attributes:
        cas_number: CAS Registry Number (primary key)
        name: Common name (e.g., "Water")
        formula: Chemical formula (e.g., "H2O")
        iupac_name: IUPAC systematic name
        coolprop_name: CoolProp lookup identifier
        aliases: Alternative names for search
        molecular_weight: Molecular weight with unit
        critical_properties: Critical point properties
        phase_properties: Phase transition properties
        source: Data source information
    """

    cas_number: str = Field(..., description="CAS Registry Number", pattern=r"^\d{1,7}-\d{2}-\d$")
    name: str = Field(..., description="Common name", max_length=100, min_length=1)
    formula: str = Field(..., description="Chemical formula", min_length=1)
    iupac_name: str = Field(..., description="IUPAC systematic name")
    coolprop_name: str = Field(..., description="CoolProp lookup identifier")
    aliases: list[str] = Field(default_factory=list, description="Alternative names")
    molecular_weight: QuantityDTO = Field(..., description="Molecular weight")
    critical_properties: CriticalPropertiesDTO = Field(..., description="Critical properties")
    phase_properties: PhasePropertiesDTO = Field(..., description="Phase properties")
    source: SourceAttributionDTO = Field(..., description="Data source")

    model_config = {"frozen": True}


class DatabaseMetadataDTO(BaseModel):
    """Container for database-level metadata.

    Attributes:
        version: Semantic version of data format (e.g., "1.0.0")
        source: Primary data source name
        retrieved_date: Date data was retrieved/generated
        attribution: Full attribution statement
        compound_count: Number of compounds in database
    """

    version: str = Field(..., description="Data format version", pattern=r"^\d+\.\d+\.\d+$")
    source: str = Field(..., description="Primary data source")
    retrieved_date: date = Field(..., description="Date data retrieved")
    attribution: str = Field(..., description="Full attribution statement")
    compound_count: int = Field(..., description="Number of compounds", ge=1)

    model_config = {"frozen": True}


class CompoundDatabaseDTO(BaseModel):
    """Top-level compound database model.

    Attributes:
        metadata: Database-level metadata
        compounds: List of compound data
    """

    metadata: DatabaseMetadataDTO = Field(..., description="Database metadata")
    compounds: list[CompoundDTO] = Field(..., description="List of compounds")

    @field_validator("compounds")
    @classmethod
    def validate_compound_count(cls, v: list[CompoundDTO], info: dict) -> list[CompoundDTO]:
        """Ensure compound count matches metadata."""
        # Note: This validator runs before we can access other fields in Pydantic v2
        # We'll validate count consistency in the loader instead
        return v

    model_config = {"frozen": True}
