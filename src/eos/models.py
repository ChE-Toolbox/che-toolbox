"""Core data models for thermodynamic calculations."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class PhaseType(str, Enum):
    """Enumeration of thermodynamic phases."""

    VAPOR = "vapor"
    LIQUID = "liquid"
    SUPERCRITICAL = "supercritical"
    TWO_PHASE = "two_phase"
    UNKNOWN = "unknown"


class Mixture(BaseModel):
    """Represents a multi-component mixture with composition."""

    compound_names: list[str] = Field(..., description="List of compound names in mixture")
    mole_fractions: list[float] = Field(
        ..., description="Mole fractions of each compound (must sum to 1.0±1e-6)"
    )

    @field_validator("mole_fractions")
    @classmethod
    def validate_mole_fractions(cls, v: list[float]) -> list[float]:
        """Validate mole fractions sum to 1.0±1e-6 and no negative or NaN values."""
        if not v:
            raise ValueError("mole_fractions cannot be empty")

        for i, frac in enumerate(v):
            if frac < 0 or frac > 1:
                raise ValueError(f"mole_fractions[{i}]={frac} must be between 0 and 1")
            if frac != frac:  # NaN check
                raise ValueError(f"mole_fractions[{i}] is NaN")

        total = sum(v)
        if abs(total - 1.0) > 1e-6:
            raise ValueError(
                f"mole_fractions sum to {total}, must be 1.0±1e-6"
            )

        return v

    @model_validator(mode="after")
    def validate_consistency(self) -> "Mixture":
        """Validate compound_names and mole_fractions have same length."""
        if len(self.compound_names) != len(self.mole_fractions):
            raise ValueError(
                f"compound_names length {len(self.compound_names)} != "
                f"mole_fractions length {len(self.mole_fractions)}"
            )
        return self

    @classmethod
    def from_names(cls, compound_names: list[str], mole_fractions: list[float]) -> "Mixture":
        """Construct a mixture from compound names and mole fractions.

        Parameters
        ----------
        compound_names : list[str]
            Names of compounds in the mixture
        mole_fractions : list[float]
            Mole fraction of each compound

        Returns
        -------
        Mixture
            Validated mixture object
        """
        return cls(compound_names=compound_names, mole_fractions=mole_fractions)


class ThermodynamicState(BaseModel):
    """Represents a complete thermodynamic state."""

    temperature: float = Field(..., gt=0, description="Temperature in K")
    pressure: float = Field(..., gt=0, description="Pressure in Pa")
    composition: str | list[float] = Field(
        ..., description="Pure compound name or mole fractions for mixture"
    )
    phase: Optional[PhaseType] = Field(None, description="Identified phase")
    z_factor: Optional[float] = Field(None, description="Compressibility factor")
    fugacity_coefficient: Optional[float] = Field(None, description="Fugacity coefficient")
    fugacity: Optional[float] = Field(None, description="Fugacity in Pa")


class BinaryInteractionParameter(BaseModel):
    """Represents a binary interaction parameter between two compounds."""

    compound_i: str = Field(..., description="First compound name")
    compound_j: str = Field(..., description="Second compound name")
    kij: float = Field(
        ..., ge=-0.5, le=0.5, description="Binary interaction parameter (-0.5 < kij < 0.5)"
    )

    @model_validator(mode="after")
    def validate_symmetry(self) -> "BinaryInteractionParameter":
        """Validate that kij values are symmetric (kij = kji implicitly by design)."""
        # This validator is here for documentation; actual symmetry is enforced
        # at the database level where pairs are stored
        return self
