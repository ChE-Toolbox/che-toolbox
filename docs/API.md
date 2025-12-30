# Heat Exchanger Calculations - API Reference

**Status**: This is a stub document. Full API reference will be generated after implementation.

## Module Overview

The heat_calc library is organized into four main calculation modules:

### 1. LMTD Module (`heat_calc.lmtd`)

Calculate heat transfer using Log Mean Temperature Difference.

```python
from heat_calc.lmtd import calculate_lmtd
from heat_calc.models import LMTDInput, FluidState, HeatExchangerConfiguration

result = calculate_lmtd(input_data: LMTDInput) -> LMTDResult
```

**Features**:
- Counterflow, parallel flow, and crossflow configurations
- Correction factor application (F_correction)
- Energy balance validation
- Edge case handling (near-zero LMTD)

### 2. NTU Module (`heat_calc.ntu`)

Calculate heat exchanger effectiveness using Number of Transfer Units.

```python
from heat_calc.ntu import calculate_ntu
from heat_calc.models import NTUInput

result = calculate_ntu(input_data: NTUInput) -> NTUResult
```

**Features**:
- Multiple configuration support
- Outlet temperature determination
- Effectiveness calculations
- Thermodynamic limit (Q_max)

### 3. Convection Module (`heat_calc.convection`)

Calculate convection heat transfer coefficients.

```python
from heat_calc.convection import calculate_convection
from heat_calc.models import ConvectionGeometry

result = calculate_convection(input_data: ConvectionGeometry) -> ConvectionResult
```

**Supported Geometries**:
- Flat plate (laminar and turbulent)
- Pipe flow (Dittus-Boelert)
- Cylinder in crossflow
- Natural convection (vertical plates)

### 4. Insulation Module (`heat_calc.insulation`)

Calculate optimal insulation thickness.

```python
from heat_calc.insulation import calculate_insulation
from heat_calc.models import InsulationInput

result = calculate_insulation(input_data: InsulationInput) -> InsulationResult
```

**Features**:
- Economic optimization
- Payback period analysis
- Temperature constraint satisfaction
- Heat loss reduction calculation

## Data Models

All input/output uses Pydantic models with Pint unit validation:

- **Inputs**: `LMTDInput`, `NTUInput`, `ConvectionGeometry`, `InsulationInput`
- **Results**: `LMTDResult`, `NTUResult`, `ConvectionResult`, `InsulationResult`

See [data-model.md](../specs/002-heat-exchanger-calc/data-model.md) for detailed model documentation.

## CLI Commands

Four CLI commands are available:

```bash
calculate-lmtd [OPTIONS] [INPUT_FILE]
calculate-ntu [OPTIONS] [INPUT_FILE]
calculate-convection [OPTIONS] [INPUT_FILE]
calculate-insulation [OPTIONS] [INPUT_FILE]
```

See [cli_interface.md](../specs/002-heat-exchanger-calc/contracts/cli_interface.md) for detailed options.

## Error Handling

All functions raise appropriate exceptions:

- `ValidationError` (Pydantic): Input validation failures
- `ValueError`: Calculation failures (non-convergence, invalid parameters)

## Examples

See [quickstart.md](../specs/002-heat-exchanger-calc/quickstart.md) for comprehensive usage examples.

## Type Safety

All functions are fully typed with Python 3.11+ type hints. mypy --strict compliance is guaranteed.
