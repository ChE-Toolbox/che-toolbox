"""EOS (Equation of State) package."""

from typing import Dict

from ..compounds.models import Compound
from .flash_pt import FlashConvergence, FlashPT, FlashResult
from .ideal_gas import IdealGasEOS
from .models import BinaryInteractionParameter, Mixture, PhaseType, ThermodynamicState
from .peng_robinson import PengRobinsonEOS
from .van_der_waals import VanDerWaalsEOS

__all__ = [
    "BinaryInteractionParameter",
    "FlashConvergence",
    "FlashPT",
    "FlashResult",
    "IdealGasEOS",
    "Mixture",
    "PengRobinsonEOS",
    "PhaseType",
    "ThermodynamicState",
    "VanDerWaalsEOS",
    "compare_compressibility_factors",
]


def compare_compressibility_factors(
    compound: Compound,
    temperature: float,
    pressure: float,
) -> dict[str, float]:
    """Compare compressibility factors across all three EOS models.

    Calculates Z-factors for Ideal Gas, Van der Waals, and Peng-Robinson
    equations of state at the same conditions for direct comparison.

    Parameters
    ----------
    compound : Compound
        Pure substance with critical properties (tc, pc, omega)
    temperature : float
        Temperature in K
    pressure : float
        Pressure in Pa

    Returns
    -------
    Dict[str, float]
        Dictionary with keys:
        - 'ideal_Z': Ideal gas compressibility (always 1.0)
        - 'vdw_Z': Van der Waals compressibility
        - 'pr_Z': Peng-Robinson compressibility

    Raises
    ------
    ValueError
        If temperature <= 0 or pressure <= 0
        If compound is missing critical properties

    Examples
    --------
    >>> from src.compounds.models import Compound
    >>> methane = Compound(name="methane", tc=190.564, pc=4.5992e6, omega=0.0115)
    >>> results = compare_compressibility_factors(methane, 300, 50e6)
    >>> results['ideal_Z']
    1.0
    >>> results['vdw_Z']  # doctest: +SKIP
    0.864
    >>> results['pr_Z']  # doctest: +SKIP
    0.851

    Notes
    -----
    For real gases at moderate to high pressure:
    - Z_ideal = 1.0 (by definition)
    - Z_vdw < 1.0 (attractive forces dominate)
    - Z_pr typically most accurate (accounts for acentric factor)

    At low pressure, all models converge to ideal gas behavior (Z → 1.0).
    """
    # Input validation
    if temperature <= 0:
        raise ValueError(f"Temperature must be positive, got {temperature}")
    if pressure <= 0:
        raise ValueError(f"Pressure must be positive, got {pressure}")
    if not hasattr(compound, "tc") or compound.tc <= 0:
        raise ValueError("Compound must have valid critical temperature (tc)")
    if not hasattr(compound, "pc") or compound.pc <= 0:
        raise ValueError("Compound must have valid critical pressure (pc)")

    # Initialize EOS solvers
    vdw_eos = VanDerWaalsEOS()
    pr_eos = PengRobinsonEOS()

    # Calculate ideal gas Z-factor (always 1.0)
    ideal_Z = IdealGasEOS.calculate_Z(pressure, temperature, v_molar=1.0)  # Value irrelevant

    # Calculate Van der Waals Z-factor
    vdw_volume = vdw_eos.calculate_volume(compound.tc, compound.pc, temperature, pressure)
    vdw_Z = VanDerWaalsEOS.calculate_Z(pressure, temperature, vdw_volume)

    # Calculate Peng-Robinson Z-factor
    # Returns tuple of Z factors (smallest=liquid, largest=vapor)
    pr_z_factors = pr_eos.calculate_z_factor(temperature, pressure, compound)
    # Use largest Z factor (vapor phase) for comparison
    pr_Z = pr_z_factors[-1]

    return {
        "ideal_Z": ideal_Z,
        "vdw_Z": vdw_Z,
        "pr_Z": pr_Z,
    }
