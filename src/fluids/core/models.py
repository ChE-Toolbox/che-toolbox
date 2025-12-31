"""
Pydantic data models for fluid mechanics calculations.

Provides type-safe data validation for fluids, pipes, pumps, valves, and systems.
"""

from typing import Any

from pydantic import BaseModel, Field


class Fluid(BaseModel):
    """Fluid properties used in calculations."""

    name: str = Field(..., description="Fluid name (e.g., 'water', 'oil')")
    density: float = Field(..., gt=0, description="Fluid density in kg/m³")
    dynamic_viscosity: float = Field(
        ..., gt=0, description="Dynamic viscosity in Pa·s"
    )
    specific_gravity: float = Field(
        default=1.0, gt=0, description="Specific gravity (dimensionless)"
    )
    temperature: float = Field(
        default=293.15, description="Temperature in Kelvin"
    )
    pressure: float = Field(default=101325, description="Pressure in Pa")
    vapor_pressure: float = Field(default=0.0, ge=0, description="Vapor pressure in Pa")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "water",
                "density": 998.0,
                "dynamic_viscosity": 0.001002,
                "specific_gravity": 0.998,
                "temperature": 293.15,
                "pressure": 101325,
                "vapor_pressure": 2337,
            }
        }


class Pipe(BaseModel):
    """Pipe geometry and material properties."""

    diameter: float = Field(..., gt=0, description="Pipe inner diameter in meters")
    length: float = Field(..., gt=0, description="Pipe length in meters")
    absolute_roughness: float = Field(
        ..., ge=0, description="Absolute roughness in meters"
    )
    material: str = Field(
        default="steel", description="Pipe material (steel, copper, pvc, etc.)"
    )
    fluid: Fluid | None = Field(default=None, description="Fluid in the pipe")

    class Config:
        json_schema_extra = {
            "example": {
                "diameter": 0.05,
                "length": 100.0,
                "absolute_roughness": 0.000045,
                "material": "steel",
            }
        }


class PumpPoint(BaseModel):
    """Pump operating point (flow, head, power)."""

    flow_rate: float = Field(..., gt=0, description="Volumetric flow rate in m³/s")
    head: float = Field(..., gt=0, description="Pump head in meters")
    power: float = Field(..., gt=0, description="Power required in Watts")


class Pump(BaseModel):
    """Pump specifications and performance data."""

    name: str = Field(..., description="Pump model name")
    type: str = Field(..., description="Pump type (centrifugal, positive_displacement)")
    design_point: PumpPoint = Field(..., description="Design point specifications")
    efficiency: float = Field(
        default=0.75,
        ge=0,
        le=1,
        description="Pump efficiency (0-1)",
    )
    npsh_required: float = Field(..., ge=0, description="NPSH required in meters")
    efficiency_curve: dict[float, float] = Field(
        default_factory=dict,
        description="Efficiency curve {flow_rate: efficiency}",
    )
    source: str = Field(
        default="reference_library", description="Data source (reference_library, user_provided)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Centrifugal Pump Model A",
                "type": "centrifugal",
                "design_point": {
                    "flow_rate": 0.05,
                    "head": 50.0,
                    "power": 25000,
                },
                "efficiency": 0.75,
                "npsh_required": 0.5,
                "efficiency_curve": {0.02: 0.65, 0.05: 0.75, 0.08: 0.73},
            }
        }


class Valve(BaseModel):
    """Valve specifications and performance data."""

    name: str = Field(..., description="Valve model name")
    type: str = Field(..., description="Valve type (ball, gate, globe)")
    nominal_size: str = Field(..., description="Valve nominal size (e.g., '2 inch')")
    cv_rating: float | dict[str, float] = Field(
        ..., description="Cv rating (single value or dict with opening %)"
    )
    rangeability: float = Field(
        default=1.0,
        gt=0,
        description="Valve rangeability (max_flow / min_flow)",
    )
    source: str = Field(
        default="reference_library", description="Data source (reference_library, user_provided)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Ball Valve 2in",
                "type": "ball",
                "nominal_size": "2 inch",
                "cv_rating": 4.4,
                "rangeability": 4.0,
            }
        }


class System(BaseModel):
    """Complete fluid system with multiple components."""

    pipes: list[Pipe] = Field(default_factory=list, description="List of pipes")
    pumps: list[Pump] = Field(default_factory=list, description="List of pumps")
    valves: list[Valve] = Field(default_factory=list, description="List of valves")
    elevation_changes: list[float] = Field(
        default_factory=list, description="Elevation changes in meters"
    )
    operating_conditions: dict[str, Any] = Field(
        default_factory=dict, description="Operating conditions (flow rate, etc.)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "pipes": [
                    {
                        "diameter": 0.05,
                        "length": 100.0,
                        "absolute_roughness": 0.000045,
                        "material": "steel",
                    }
                ],
                "pumps": [],
                "valves": [],
                "elevation_changes": [10.0, -5.0],
                "operating_conditions": {"flow_rate": 0.05},
            }
        }
