# Data Model & Module Contracts

**Date**: 2025-12-30
**Feature**: Thermodynamic Extension (002-thermodynamic-models)
**Status**: Phase 1 - Design

---

## Domain Model

### Core Entities

#### CompoundProperties (existing, extends from `models.py`)

```python
from dataclasses import dataclass

@dataclass
class Compound:
    """Physical properties of a pure substance."""
    name: str
    cas_number: str
    molar_mass: float          # kg/mol
    tc: float                  # Critical temperature [K]
    pc: float                  # Critical pressure [Pa]
    omega: float               # Acentric factor [-]
    # Additional properties (existing)
```

**Constraints**:
- `tc > 0` and `pc > 0` and `omega >= 0`
- Sourced from: NIST WebBook, CoolProp
- Validation: Pydantic v2.x models

---

#### ThermodynamicState (existing, extends from `models.py`)

```python
@dataclass
class ThermodynamicState:
    """Result of an EOS calculation."""
    T: float                   # Temperature [K]
    P: float                   # Pressure [Pa]
    n: float                   # Moles [mol]
    z: float                   # Compressibility factor [-]
    v_molar: float             # Molar volume [m^3/mol]
    phase: PhaseType           # PhaseType.LIQUID | VAPOR | SUPERCRITICAL
```

**Constraints**:
- `T > 0`, `P >= 0`, `n > 0`
- `0 < z <= 1.5` (typical range for real gases)
- `v_molar = (n*R*T*z) / P`

---

### New Data Models for This Feature

#### 1. VanDerWaalsState

```python
from dataclasses import dataclass
from .models import ThermodynamicState

@dataclass
class VanDerWaalsState(ThermodynamicState):
    """Van der Waals EOS calculation result."""
    a: float                   # 'a' parameter [Pa*m^6*mol^-2]
    b: float                   # 'b' parameter [m^3*mol^-1]

    # Inherited from ThermodynamicState:
    # T, P, n, z, v_molar, phase
```

**Derivation**:
- `a = 27*R²*Tc²/(64*Pc)`
- `b = R*Tc/(8*Pc)`
- `z = PV/nRT` (computed)

**Validation Rules**:
- `a > 0` and `b > 0` (physically required)
- For pure substance: `a` depends only on critical properties, not T independently
- For mixture: `a` calculated via mixing rules (later enhancement)

---

#### 2. IdealGasState

```python
@dataclass
class IdealGasState(ThermodynamicState):
    """Ideal Gas Law calculation result."""
    # Inherited from ThermodynamicState:
    # T, P, n, z=1.0, v_molar, phase=VAPOR
    pass
```

**Special Properties**:
- `z` always exactly `1.0`
- `phase` always `PhaseType.VAPOR` (ideal gas has no liquid phase)
- `v_molar = R*T/P` (by definition)

---

#### 3. FlashResult (NEW - Core for PT Flash)

```python
from dataclasses import dataclass
from typing import Optional
import numpy as np
from enum import Enum

class FlashConvergence(Enum):
    """Flash calculation convergence status."""
    SUCCESS = "converged"
    SINGLE_PHASE = "single_phase_detected"
    MAX_ITERATIONS = "max_iterations_exceeded"
    DIVERGED = "diverged"
    NOT_RUN = "not_attempted"

@dataclass
class FlashResult:
    """Result of a PT flash calculation."""

    # Phase split (mol fractions)
    L: float                    # Liquid mole fraction [0, 1]
    V: float                    # Vapor mole fraction [0, 1]

    # Compositions
    x: np.ndarray              # Liquid mole fractions by component
    y: np.ndarray              # Vapor mole fractions by component

    # Equilibrium data
    K_values: np.ndarray       # Partitioning ratios K_i = y_i/x_i

    # Convergence metrics
    iterations: int            # Number of RR iterations performed
    tolerance_achieved: float  # Final |f_i^v / f_i^l - 1| value
    convergence: FlashConvergence

    # Validation flags
    material_balance_error: Optional[float]  # max(|z_i - (L*x_i + V*y_i)|)

    @property
    def success(self) -> bool:
        """True if flash converged successfully."""
        return self.convergence == FlashConvergence.SUCCESS
```

**Constraints**:
- `L + V = 1.0` (mole basis)
- `sum(x) = 1.0` and `sum(y) = 1.0` (mole fractions)
- `K_values = y / x` (by definition, K_i ≥ 0)
- `iterations ≤ 50` (specification constraint)
- `tolerance_achieved < 1e-6` (equilibrium criterion)
- `material_balance_error < 1e-6` (material balance criterion)

**Phase Detection Rules**:
```python
# If T > Tc: Single-phase vapor
L = 0.0
V = 1.0
x = None  # Undefined
y = feed  # Vapor composition = feed

# If n_components == 1: Pure component
# Check saturation: If P > P_sat(T), liquid (L=1, V=0)
#                   If P < P_sat(T), vapor (L=0, V=1)

# Otherwise: Two-phase RR iteration (or single-phase if RR fails to split)
```

---

#### 4. Mixture (existing, extends from `models.py`)

```python
@dataclass
class Mixture:
    """Multi-component mixture definition."""
    components: list[Compound]  # Ordered list of pure compound properties
    z: np.ndarray               # Overall mole fractions [sum=1]

    # Optional: binary interaction parameters (for EOS mixing rules)
    kij: Optional[np.ndarray]  # n x n matrix of k_ij values
```

**For This Feature**:
- 2-5 component mixtures
- `z` provides feed composition
- `kij` defaults to 0 (for PR and VDW without enhancement)

---

## Module API Contracts

### `ideal_gas.py` - IdealGasEOS

```python
class IdealGasEOS:
    """Ideal Gas Law solver: PV = nRT"""

    R: float = 8.314462618  # Pa*m^3/(mol*K)

    @staticmethod
    def calculate_volume(
        n: float,          # Moles [mol]
        T: float,          # Temperature [K]
        P: float           # Pressure [Pa]
    ) -> float:
        """Calculate molar volume using V = RT/P.

        Parameters
        ----------
        n : float
            Number of moles [mol]
        T : float
            Temperature [K], must be > 0
        P : float
            Pressure [Pa], must be > 0

        Returns
        -------
        float
            Molar volume [m^3/mol]

        Raises
        ------
        ValueError
            If T <= 0 or P <= 0
        """
        if T <= 0:
            raise ValueError(f"Temperature must be positive, got {T}")
        if P <= 0:
            raise ValueError(f"Pressure must be positive, got {P}")

        return IdealGasEOS.R * T / P

    @staticmethod
    def calculate_Z(
        P: float,          # Pressure [Pa]
        T: float,          # Temperature [K]
        V: float           # Total volume [m^3]
    ) -> float:
        """Calculate compressibility factor Z = PV/(nRT).

        Returns
        -------
        float
            Compressibility factor, always 1.0 for ideal gas
        """
        return 1.0  # By definition

    @staticmethod
    def calculate_state(
        compound: Compound,
        T: float,
        P: float,
        n: float = 1.0
    ) -> IdealGasState:
        """Calculate complete thermodynamic state.

        Returns
        -------
        IdealGasState
            With z=1.0, phase=VAPOR
        """
        # Implementation
```

---

### `van_der_waals.py` - VanDerWaalsEOS

```python
class VanDerWaalsEOS:
    """Van der Waals equation of state: (P + A/V²)(V - B) = RT"""

    R: float = 8.314462618  # Pa*m^3/(mol*K)

    @staticmethod
    def calculate_a(
        tc: float,         # Critical temperature [K]
        pc: float,         # Critical pressure [Pa]
        T: Optional[float] = None  # Temperature [K] (not used for VDW)
    ) -> float:
        """Calculate 'a' parameter: a = 27*R²*Tc²/(64*Pc).

        Parameters
        ----------
        tc : float
            Critical temperature [K]
        pc : float
            Critical pressure [Pa]
        T : Optional[float]
            Temperature (ignored for VDW, included for API consistency with PR)

        Returns
        -------
        float
            Parameter a [Pa*m^6*mol^-2]

        Note
        ----
        Unlike Peng-Robinson, VDW 'a' is independent of temperature.
        """
        if tc <= 0:
            raise ValueError(f"Critical temperature must be positive, got {tc}")
        if pc <= 0:
            raise ValueError(f"Critical pressure must be positive, got {pc}")

        a = (27 * VanDerWaalsEOS.R**2 * tc**2) / (64 * pc)
        return a

    @staticmethod
    def calculate_b(
        tc: float,         # Critical temperature [K]
        pc: float          # Critical pressure [Pa]
    ) -> float:
        """Calculate 'b' parameter: b = R*Tc/(8*Pc).

        Returns
        -------
        float
            Parameter b [m^3*mol^-1]
        """
        if tc <= 0 or pc <= 0:
            raise ValueError("Critical properties must be positive")

        b = (VanDerWaalsEOS.R * tc) / (8 * pc)
        return b

    def calculate_volume(
        self,
        tc: float,         # Critical temperature [K]
        pc: float,         # Critical pressure [Pa]
        T: float,          # Temperature [K]
        P: float           # Pressure [Pa]
    ) -> float:
        """Calculate molar volume by solving cubic: (P + a/V²)(V - B) = RT.

        Parameters
        ----------
        tc, pc : float
            Critical properties [K, Pa]
        T : float
            Temperature [K]
        P : float
            Pressure [Pa]

        Returns
        -------
        float
            Molar volume [m^3/mol]

        Raises
        ------
        ValueError
            If cubic has no real roots or if solution is unphysical
        """
        # Uses cubic_solver.py (existing module)
        # Detailed implementation in van_der_waals.py
```

---

### `flash_pt.py` - FlashPT

```python
class FlashPT:
    """PT Flash (Pressure-Temperature) calculator."""

    def __init__(self):
        """Initialize PT flash calculator."""
        self.max_iterations: int = 50
        self.tolerance: float = 1e-6

    def calculate(
        self,
        mixture: Mixture,
        T: float,                  # Temperature [K]
        P: float,                  # Pressure [Pa]
        eos: PengRobinsonEOS,
        tolerance: Optional[float] = None,
        max_iterations: Optional[int] = None
    ) -> FlashResult:
        """Perform PT flash calculation using Rachford-Rice iteration.

        Parameters
        ----------
        mixture : Mixture
            Feed composition and component properties
        T : float
            Temperature [K]
        P : float
            Pressure [Pa]
        eos : PengRobinsonEOS
            EOS solver for fugacity calculations
        tolerance : float, optional
            Equilibrium tolerance (default 1e-6 for |f_v/f_l - 1|)
        max_iterations : int, optional
            Maximum RR iterations (default 50)

        Returns
        -------
        FlashResult
            Complete flash result with compositions, K-values, convergence data

        Algorithm
        ---------
        1. Check single-phase conditions:
           - If T > Tc_mix: return V=1, L=0
           - If n_components == 1: check saturation
        2. Initialize K_i via Wilson correlation
        3. Rachford-Rice iteration:
           - Compute liquid, vapor fractions
           - Update K_i from fugacity ratios
           - Check convergence: |f_i^v / f_i^l - 1| < 1e-6
           - Stop when converged or max_iterations reached
        4. Validate material balance: |z_i - (L*x_i + V*y_i)| < 1e-6
        5. Return FlashResult with all outputs
        """
        # Detailed implementation in flash_pt.py
```

---

## Data Flow Diagrams

### Van der Waals Calculation

```
User Input:
  Compound (Tc, Pc)
  T, P
    ↓
VanDerWaalsEOS.calculate_a() → a
VanDerWaalsEOS.calculate_b() → b
    ↓
cubic_solver.solve_cubic(a, b, T, P) → [V_roots]
    ↓
Select root: V closest to ideal gas volume
    ↓
Calculate Z = P*V / (R*T)
    ↓
Return: VanDerWaalsState(T, P, n, z, v_molar, a, b, phase)
```

### Ideal Gas Calculation

```
User Input:
  T, P, n
    ↓
IdealGasEOS.calculate_volume() → V = nRT/P
IdealGasEOS.calculate_Z() → Z = 1.0
    ↓
Return: IdealGasState(T, P, n, Z=1.0, v_molar, phase=VAPOR)
```

### PT Flash Calculation

```
User Input:
  Mixture (z_feed, [compounds])
  T, P
  EOS: PengRobinsonEOS
    ↓
Check single-phase:
  T > Tc? → return V=1, L=0
  n_comp=1? → return L=1 or V=1
    ↓
Initialize K_i (Wilson correlation)
    ↓
RR Iteration Loop (max 50 times):
  1. Calculate V, L from RR equation
  2. Calculate phi_i^v, phi_i^l from PR EOS
  3. Update K_i = phi_i^v / phi_i^l
  4. Check: max(|f_i^v / f_i^l - 1|) < 1e-6?
  5. If converged or max_iterations: break
    ↓
Validate:
  Material balance: |z_i - (L*x_i + V*y_i)| < 1e-6
  Energy balance: Compare enthalpy
    ↓
Return: FlashResult(L, V, x, y, K, iter, tol, success)
```

---

## Validation Rules by Entity

### Compound
- `tc > 0`, `pc > 0`
- `omega >= 0` (acentric factor always non-negative)
- Source: NIST WebBook only

### VanDerWaalsState
- `a > 0`, `b > 0` (derived from positive Tc, Pc)
- `0 < z <= 1.5` (typical for non-ideal gases)
- `v_molar = R*T*z / P` (consistency check)

### IdealGasState
- `z == 1.0` exactly (enforced)
- `phase == PhaseType.VAPOR` (enforced)

### FlashResult
- `L + V = 1.0` (mole balance)
- `sum(x) = 1.0`, `sum(y) = 1.0` (composition sums)
- `K_i = y_i / x_i >= 0` (all K-values non-negative)
- If single-phase: `L=0, V=1` (vapor) or `L=1, V=0` (liquid)
- `iterations <= 50` (convergence constraint)
- `tolerance_achieved < 1e-6` (equilibrium constraint)
- `material_balance_error < 1e-6` (composition balance)

---

## Integration with Existing Code

### Reused from `models.py`
- `ThermodynamicState` (base class for VanDerWaalsState, IdealGasState)
- `Mixture` (feed specification for flash)
- `PhaseType` enum
- `Compound` dataclass

### Reused from `peng_robinson.py`
- `cubic_solver.solve_cubic()` (for VDW volume calculation)
- `PengRobinsonEOS.calculate_fugacity()` (for PT flash)

### New in EOS Package
- `VanDerWaalsEOS` class (new module: vdw.py)
- `IdealGasEOS` class (new module: ideal.py)
- `FlashPT` class (new module: flash_pt.py)
- `FlashResult` dataclass (new, in flash_pt.py or models.py)

### Package Exports (`eos/__init__.py`)
```python
from .van_der_waals import VanDerWaalsEOS
from .ideal_gas import IdealGasEOS
from .flash_pt import FlashPT, FlashResult, FlashConvergence

__all__ = [
    "PengRobinsonEOS",
    "VanDerWaalsEOS",
    "IdealGasEOS",
    "FlashPT",
    "FlashResult",
    "FlashConvergence",
    "PhaseType",
    "Mixture",
    "ThermodynamicState",
    "BinaryInteractionParameter",
]
```

---

**Status**: Phase 1 Design Complete ✓
