"""Data models for validation test cases and results."""

from pydantic import BaseModel, Field


class ValidationTestCase(BaseModel):
    """Represents a single NIST validation test case."""

    compound_name: str = Field(..., description="Name of compound being tested")
    temperature: float = Field(..., gt=0, description="Temperature in K")
    pressure: float = Field(..., gt=0, description="Pressure in Pa")
    expected_z_factor: float | None = Field(None, description="Reference Z factor from NIST")
    expected_fugacity: float | None = Field(None, description="Reference fugacity in Pa")
    expected_vapor_pressure: float | None = Field(None, description="Reference vapor pressure in Pa")
    tolerance_z: float = Field(0.05, description="Tolerance for Z factor (default 5%)")
    tolerance_fugacity: float = Field(0.10, description="Tolerance for fugacity (default 10%)")


class ValidationResult(BaseModel):
    """Stores results of validation test."""

    test_case: ValidationTestCase = Field(..., description="Test case that was run")
    calculated_z_factor: float | None = Field(None, description="Calculated Z factor")
    calculated_fugacity: float | None = Field(None, description="Calculated fugacity")
    z_factor_passed: bool | None = Field(None, description="Whether Z factor test passed")
    fugacity_passed: bool | None = Field(None, description="Whether fugacity test passed")
    z_factor_deviation: float | None = Field(None, description="Relative deviation in Z factor")
    fugacity_deviation: float | None = Field(None, description="Relative deviation in fugacity")
    error_message: str | None = Field(None, description="Error message if calculation failed")
