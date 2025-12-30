# Data Model: Heat Exchanger Calculations

**Feature**: 002-heat-exchanger-calc
**Date**: 2025-12-30
**Status**: Phase 1 Design

## Overview

The heat exchanger calculations library uses a data model structured around four calculation domains:
1. **LMTD Method** (Log Mean Temperature Difference)
2. **NTU Method** (Number of Transfer Units - Effectiveness)
3. **Convection Correlations** (Heat transfer coefficients)
4. **Insulation Sizing** (Economic thickness optimization)

All input/output data flows through **Pydantic models** with **Pint** for dimensional analysis. Results objects are comprehensive, including primary values, intermediate calculations, method references, and confidence bounds.

---

## Core Data Types

### Base Model (Shared)

All Pydantic models inherit from a base that enforces:
- Unit validation via Pint (all quantities carry explicit units)
- JSON/YAML serialization support
- Type safety with Python 3.11+ annotations

```python
# Pseudo-model structure (actual models in src/heat_calc/models/)
class BaseCalculationInput(BaseModel):
    """Base for all calculation inputs with unit validation."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

class BaseCalculationResult(BaseModel):
    """Base for all calculation results with traceability."""
    calculation_method: str           # e.g., "LMTD_Counterflow_v1"
    source_reference: str             # e.g., "Incropera_9e_p452"
    confidence_tolerance: float       # Accuracy bound as percentage
    intermediate_values: dict[str, float]  # All intermediate calcs for inspection
```

---

## Domain 1: LMTD Method

**Purpose**: Calculate heat transfer rate using Log Mean Temperature Difference; supports counterflow, parallel flow, and crossflow configurations with correction factors.

### Input Entity: LMTDInput

**Pydantic Model**: `src/heat_calc/models/lmtd_input.py`

```python
class FluidState(BaseModel):
    """Single fluid stream state."""
    T_inlet: Quantity = Field(..., description="Inlet temperature with units")
    T_outlet: Quantity = Field(..., description="Outlet temperature with units")
    mdot: Quantity = Field(..., description="Mass flow rate with units")

class HeatExchangerConfiguration(BaseModel):
    """Geometry and type of heat exchanger."""
    configuration: Literal["counterflow", "parallel_flow", "crossflow_unmixed_both",
                          "crossflow_unmixed_hot_mixed_cold", "crossflow_mixed_both"]
    area: Quantity = Field(..., description="Heat transfer surface area with units")
    # Optional correction factor override (usually calculated)
    F_correction: float = Field(default=None, ge=0.0, le=1.0,
                               description="Correction factor for non-ideal geometry")

class LMTDInput(BaseCalculationInput):
    """Complete input for LMTD heat transfer calculation."""
    hot_fluid: FluidState
    cold_fluid: FluidState
    exchanger: HeatExchangerConfiguration
    overall_h_times_area: Quantity | None = Field(
        default=None,
        description="Optional pre-calculated UA; if provided, overrides area-based calculation"
    )
```

### Output Entity: LMTDResult

**Pydantic Model**: `src/heat_calc/models/lmtd_results.py`

```python
class LMTDResult(BaseCalculationResult):
    """Complete results from LMTD calculation."""
    # Primary results
    heat_transfer_rate: Quantity          # Calculated Q [W or kW]
    LMTD_arithmetic: Quantity             # Log mean temperature difference [K or °C]
    LMTD_effective: Quantity              # After correction factor: F × LMTD_log

    # Secondary results (intermediate values)
    T_difference_hot: Quantity            # ΔT_hot = T_h,in - T_h,out
    T_difference_cold: Quantity           # ΔT_cold = T_c,out - T_c,in
    configuration_used: str               # Which formula applied

    # Validation
    energy_balance_hot: Quantity          # mdot_h × cp_h × ΔT_h (for validation)
    energy_balance_cold: Quantity         # mdot_c × cp_c × ΔT_c (for validation)
    energy_balance_error_percent: float   # |(Q_hot - Q_cold)| / Q_avg × 100
```

**Validation Rules**:
- `energy_balance_error_percent` must be < 1% (heat balance sanity check)
- `LMTD_effective` ≤ `LMTD_arithmetic` (correction factor decreases LMTD)
- All temperatures must be physically realistic (no infinite/NaN values)

---

## Domain 2: NTU Method

**Purpose**: Calculate heat exchanger effectiveness and determine outlet temperature given inlet conditions and UA product.

### Input Entity: NTUInput

**Pydantic Model**: `src/heat_calc/models/ntu_input.py`

```python
class NTUInput(BaseCalculationInput):
    """Complete input for NTU-effectiveness calculation."""
    # Inlet conditions
    T_hot_inlet: Quantity
    T_cold_inlet: Quantity
    mdot_hot: Quantity
    mdot_cold: Quantity
    cp_hot: Quantity = Field(..., description="Specific heat capacity hot fluid [J/(kg·K)]")
    cp_cold: Quantity = Field(..., description="Specific heat capacity cold fluid [J/(kg·K)]")

    # Heat exchanger characteristics
    UA: Quantity = Field(..., description="Overall heat transfer coefficient × area [W/K]")
    configuration: Literal["counterflow", "parallel_flow", "shell_and_tube_1_2",
                          "crossflow_unmixed_both", "crossflow_mixed_one"]

    # Optional: supply one to get outlet temperature for the other
    T_hot_outlet: Quantity | None = Field(default=None,
                                         description="If given, calculate T_cold_outlet instead")
    T_cold_outlet: Quantity | None = Field(default=None,
                                          description="If given, calculate T_hot_outlet instead")
```

### Output Entity: NTUResult

**Pydantic Model**: `src/heat_calc/models/ntu_results.py`

```python
class NTUResult(BaseCalculationResult):
    """Complete results from NTU-effectiveness calculation."""
    # Primary results
    NTU: float                             # Number of Transfer Units [-]
    effectiveness: float                  # Heat exchanger effectiveness [-], 0 ≤ ε ≤ 1
    heat_transfer_rate: Quantity          # Calculated Q [W or kW]

    # Outlet temperatures (calculated)
    T_hot_outlet: Quantity
    T_cold_outlet: Quantity

    # Heat capacity rates
    C_hot: Quantity                        # mdot_hot × cp_hot [W/K]
    C_cold: Quantity                       # mdot_cold × cp_cold [W/K]
    C_min: Quantity                        # Minimum of C_hot, C_cold
    C_max: Quantity                        # Maximum
    C_ratio: float                         # C_min / C_max (used in correlations)

    # Thermodynamic limits
    Q_max: Quantity                        # Maximum possible heat transfer (counter-current limit)
    effectiveness_theoretical_max: float  # Based on configuration (approaches 1.0 as NTU → ∞)

    # Energy balance validation
    energy_balance_error_percent: float
```

**Validation Rules**:
- `effectiveness` bounded to [0, 1]
- `Q_max` ≥ `heat_transfer_rate` (actual ≤ maximum possible)
- `NTU` > 0
- Outlet temperatures must satisfy energy balance

---

## Domain 3: Convection Correlations

**Purpose**: Calculate convection heat transfer coefficients (h) for various geometries and flow regimes using published correlations.

### Input Entity: ConvectionInput (Polymorphic)

**Pydantic Model**: `src/heat_calc/models/convection_input.py`

```python
class FluidProperties(BaseModel):
    """Standard thermal properties for convection calculations."""
    density: Quantity = Field(..., description="ρ [kg/m³]")
    dynamic_viscosity: Quantity = Field(..., description="μ [Pa·s]")
    specific_heat: Quantity = Field(..., description="cp [J/(kg·K)]")
    thermal_conductivity: Quantity = Field(..., description="k [W/(m·K)]")

# Base union type for different geometries
ConvectionGeometry = Annotated[
    Union[
        "FlatPlateConvection",
        "CylinderCrossflowConvection",
        "PipeFlowConvection",
        "VerticalPlateNaturalConvection"
    ],
    Field(discriminator="geometry_type")
]

class FlatPlateConvection(BaseCalculationInput):
    geometry_type: Literal["flat_plate"]
    length: Quantity = Field(..., description="Characteristic length [m]")
    flow_velocity: Quantity
    fluid_properties: FluidProperties
    surface_temperature: Quantity
    bulk_fluid_temperature: Quantity
    roughness: float = Field(default=0.0, ge=0.0, description="Surface roughness [-]")

class CylinderCrossflowConvection(BaseCalculationInput):
    geometry_type: Literal["cylinder_crossflow"]
    diameter: Quantity
    flow_velocity: Quantity
    fluid_properties: FluidProperties
    # Similar fields...

class PipeFlowConvection(BaseCalculationInput):
    geometry_type: Literal["pipe_flow"]
    diameter: Quantity
    length: Quantity
    flow_velocity: Quantity
    fluid_properties: FluidProperties
    surface_temperature: Quantity
    bulk_fluid_temperature: Quantity

class VerticalPlateNaturalConvection(BaseCalculationInput):
    geometry_type: Literal["vertical_plate_natural"]
    height: Quantity
    surface_temperature: Quantity
    bulk_fluid_temperature: Quantity
    fluid_properties: FluidProperties
    pressure: Quantity = Field(default=Quantity(101325, "Pa"), description="Ambient pressure")
```

### Output Entity: ConvectionResult

**Pydantic Model**: `src/heat_calc/models/convection_results.py`

```python
class ConvectionResult(BaseCalculationResult):
    """Complete results from convection correlation calculation."""
    # Primary result
    h: Quantity                            # Convection coefficient [W/(m²·K)]

    # Dimensionless numbers
    Reynolds: float                        # Re [-]
    Prandtl: float                         # Pr [-]
    Nusselt: float                         # Nu [-]
    Grashof: float | None                  # Gr [-] (natural convection only)
    Rayleigh: float | None                 # Ra [-] (natural convection only)

    # Flow regime identification
    flow_regime: str                       # e.g., "laminar", "turbulent", "transitional"

    # Correlation accuracy
    applicable_range: dict[str, tuple[float, float]]  # {param: (min, max)} for validity
    is_within_correlation_range: bool      # True if input parameters within published bounds

    # Intermediate correlations
    correlation_equation: str              # e.g., "Gnielinski (turbulent pipe)"
    correlation_coefficients: dict[str, float]  # a, b, c from Nu = a × Re^b × Pr^c
```

**Validation Rules**:
- `h` > 0
- Dimensionless numbers computed consistently
- Warning if parameters outside correlation's published range (but calculation proceeds)

---

## Domain 4: Insulation Sizing

**Purpose**: Calculate economic insulation thickness for cylindrical pipes, optimizing payback period given energy cost.

### Input Entity: InsulationInput

**Pydantic Model**: `src/heat_calc/models/insulation_input.py`

```python
class InsulationInput(BaseCalculationInput):
    """Input for insulation sizing and economic optimization."""
    # Pipe geometry
    pipe_diameter: Quantity = Field(..., description="OD of uninsulated pipe [m]")
    pipe_length: Quantity

    # Thermal conditions
    T_surface_uninsulated: Quantity = Field(..., description="Pipe surface temp (uninsulated) [K]")
    T_ambient: Quantity = Field(default=Quantity(298, "K"))
    h_ambient: Quantity = Field(..., description="Natural convection h to ambient [W/(m²·K)]")

    # Insulation material properties
    insulation_material: str = Field(..., description="Name (e.g., 'fiberglass', 'mineral_wool')")
    thermal_conductivity_insulation: Quantity = Field(...)  # k_ins [W/(m·K)]
    density_insulation: Quantity = Field(...)  # for cost estimation

    # Economic parameters
    energy_cost: Quantity = Field(..., description="Cost per unit energy [$/MWh or $/GJ]")
    energy_annual_operating_hours: int = Field(default=8760)
    insulation_cost_per_thickness: Quantity = Field(..., description="$/m² per m thickness")

    # Constraints
    surface_temp_limit: Quantity | None = Field(
        default=None,
        description="Max surface temp (safety, e.g., 60°C) [K]; if given, overrides economic optimization"
    )
    insulation_thickness_min: Quantity = Field(default=Quantity(0.01, "m"))
    insulation_thickness_max: Quantity = Field(default=Quantity(0.15, "m"))

    # Analysis period
    analysis_period_years: int = Field(default=10)
```

### Output Entity: InsulationResult

**Pydantic Model**: `src/heat_calc/models/insulation_results.py`

```python
class InsulationResult(BaseCalculationResult):
    """Complete results from insulation sizing calculation."""
    # Optimal thickness (economic or constrained)
    optimal_insulation_thickness: Quantity
    optimization_mode: Literal["economic_payback", "temperature_constraint"]

    # Heat loss comparison
    Q_uninsulated: Quantity                # Heat loss without insulation [W]
    Q_insulated: Quantity                  # Heat loss with optimal insulation [W]
    heat_loss_reduction_percent: float     # (Q_un - Q_ins) / Q_un × 100

    # Economic analysis (if optimization_mode == "economic_payback")
    annual_energy_savings: Quantity        # Energy saved per year [kWh or GJ]
    annual_cost_savings: float             # $ saved per year
    annual_insulation_cost: float          # $ per year (amortized over analysis period)
    net_annual_savings: float              # annual_cost_savings - annual_insulation_cost
    payback_period_years: float            # Years to recoup insulation cost

    # Temperature constraint (if optimization_mode == "temperature_constraint")
    T_surface_insulated: Quantity          # Surface temperature with optimal insulation
    T_surface_required: Quantity | None    # The constraint temperature (if applied)

    # Sensitivity analysis (optional)
    sensitivity: dict[str, dict]  # E.g., {"energy_cost": {"+20%": {...}, "-20%": {...}}}
```

**Validation Rules**:
- `optimal_insulation_thickness` within [`insulation_thickness_min`, `insulation_thickness_max`]
- `Q_insulated` ≤ `Q_uninsulated`
- `payback_period_years` > 0 if economic mode
- `T_surface_insulated` < `T_surface_uninsulated`

---

## Relationships & State Transitions

### Cross-Domain Dependencies

```
┌─────────────────────────────────────────────────────┐
│         Properties Module (001-data-foundations)    │
│  (Provides fluid properties: ρ, μ, cp, k)          │
└─────────────────────┬───────────────────────────────┘
                      │
        ┌─────────────┼─────────────┬──────────────┐
        │             │             │              │
    ┌───▼───┐   ┌────▼────┐  ┌────▼─────┐  ┌────▼──────┐
    │ LMTD  │   │   NTU   │  │Convection│  │Insulation │
    └───────┘   └─────────┘  └──────────┘  └───────────┘
```

### Typical Workflow

1. **User starts with Convection**: Calculate `h` for a specific geometry/fluid combination
   - Input: `ConvectionInput` (geometry-specific)
   - Output: `ConvectionResult` (includes `h`)

2. **User proceeds to LMTD**: Design heat exchanger
   - Input: `LMTDInput` (requires `h` from step 1, or provides it directly)
   - Output: `LMTDResult` (includes `Q`, `LMTD`, effectiveness)

3. **Optionally use NTU**: Verify with alternative method or find outlet temp
   - Input: `NTUInput` (requires `UA` from LMTD step)
   - Output: `NTUResult` (includes outlet temps, effectiveness)

4. **Design Insulation**: Economic analysis for pipe protection
   - Input: `InsulationInput` (uses heat loss from LMTD step)
   - Output: `InsulationResult` (thickness, payback period, cost savings)

---

## Serialization & I/O

### JSON Export Format

All Pydantic models support `.model_dump_json()` for serialization:

```json
{
  "calculation_method": "LMTD_Counterflow_v1",
  "source_reference": "Incropera_9e_p452",
  "confidence_tolerance": 1.0,
  "heat_transfer_rate": "100.5 kW",
  "LMTD_arithmetic": "45.2 K",
  "intermediate_values": {
    "T_hot_difference": "50.0 K",
    "T_cold_difference": "40.0 K"
  }
}
```

### YAML Equivalents

CLI accepts YAML input files for batch processing:

```yaml
hot_fluid:
  T_inlet: 373 K
  T_outlet: 363 K
  mdot: 10 kg/s
cold_fluid:
  T_inlet: 293 K
  T_outlet: 303 K
  mdot: 12 kg/s
exchanger:
  configuration: counterflow
  area: 50 m²
```

---

## Validation & Constraints

### Field-Level Validation

- **Temperature**: Must be >= 0 K (absolute zero check)
- **Mass flow rate**: Must be > 0
- **Dimensionless numbers**: Bounded by physically meaningful ranges (e.g., 0 ≤ effectiveness ≤ 1)
- **Energy balance**: Heat in must equal heat out within tolerance

### Model-Level Validation (Pydantic validators)

```python
@field_validator('LMTD_effective')
def validate_lmtd_effective(cls, v, info):
    """Ensure correction factor applied properly."""
    if 'LMTD_arithmetic' in info.data:
        if v > info.data['LMTD_arithmetic']:
            raise ValueError("LMTD_effective cannot exceed LMTD_arithmetic")
    return v
```

---

## Type Coverage

All models enforce **100% type hints** (mypy --strict compliance):
- No `Any` types
- Union types explicit (e.g., `Quantity | None`)
- Discriminated unions for polymorphic inputs (e.g., `ConvectionGeometry`)

---

## Summary Table

| Domain | Input Model | Output Model | Key Entities |
|--------|-------------|--------------|--------------|
| LMTD | `LMTDInput` | `LMTDResult` | FluidState, HeatExchangerConfiguration |
| NTU | `NTUInput` | `NTUResult` | Heat capacity rates, C_min/C_max, NTU, effectiveness |
| Convection | `ConvectionInput` (polymorphic) | `ConvectionResult` | Dimensionless numbers (Re, Pr, Nu, Gr, Ra), h |
| Insulation | `InsulationInput` | `InsulationResult` | Economic params, payback period, optimal thickness |

