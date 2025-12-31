"""Data models for compound properties."""

from pydantic import BaseModel, Field, field_validator


class Compound(BaseModel):
    """Represents a pure chemical compound with critical properties."""

    name: str = Field(..., description="Compound name")
    cas_number: str = Field(..., description="CAS registry number")
    molecular_weight: float = Field(..., gt=0, description="Molecular weight in g/mol")
    tc: float = Field(..., gt=0, description="Critical temperature in K")
    pc: float = Field(..., gt=0, description="Critical pressure in Pa")
    acentric_factor: float = Field(..., ge=-1, le=2, description="Acentric factor ω (-1 < ω < 2)")

    @field_validator("acentric_factor")
    @classmethod
    def validate_acentric_factor(cls, v: float) -> float:
        """Validate acentric factor is in typical range."""
        if not (-1 < v < 2):
            raise ValueError(f"acentric_factor={v} must be between -1 and 2")
        return v
