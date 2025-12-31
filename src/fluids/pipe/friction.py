"""
Friction factor calculation for pipe flow using Colebrook and Churchill equations.

Friction factor depends on Reynolds number and pipe roughness.
"""

import math
from typing import Any

from scipy import optimize

from fluids.output.formatter import create_result


def calculate_friction_factor(
    reynolds: float,
    roughness: float,
    diameter: float,
    method: str = "churchill",
) -> dict[str, Any]:
    """
    Calculate friction factor for pipe flow.

    Friction factor is determined by flow regime:
    - Laminar (Re < 2300): f = 64/Re (Hagen-Poiseuille)
    - Transitional (2300 ≤ Re ≤ 4000): Warning + use laminar as conservative
    - Turbulent (Re > 4000): Churchill or Colebrook equation

    Args:
        reynolds: Reynolds number (dimensionless)
        roughness: Absolute roughness in m
        diameter: Pipe diameter in m
        method: 'churchill' (explicit) or 'colebrook' (implicit)

    Returns:
        Dictionary with:
        - friction_factor: Calculated friction factor (dimensionless)
        - method_used: Method used for calculation
        - warnings: List of warnings if any
    """
    warnings = []

    if reynolds < 0:
        raise ValueError("Reynolds number cannot be negative")
    if roughness < 0:
        raise ValueError("Roughness cannot be negative")
    if diameter <= 0:
        raise ValueError("Diameter must be positive")

    # Check if velocity is zero
    if reynolds == 0:
        # Zero velocity means no flow, but we'll handle gracefully
        return create_result(
            value=64.0,  # Laminar value at very low Re
            unit="dimensionless",
            formula_used="f = 64/Re (limit as Re→0)",
            intermediate_values={"reynolds": reynolds},
            warnings=["Zero Reynolds number indicates zero flow"],
            source="Hagen-Poiseuille solution",
        )

    # Laminar flow (Re < 2300)
    if reynolds < 2300:
        f = 64.0 / reynolds
        return create_result(
            value=f,
            unit="dimensionless",
            formula_used="f = 64/Re",
            intermediate_values={
                "reynolds": reynolds,
                "flow_regime": "laminar",
            },
            warnings=[],
            source="Hagen-Poiseuille exact solution",
        )

    # Transitional flow (2300 ≤ Re ≤ 4000) - use conservative laminar
    if reynolds <= 4000:
        f_laminar = 64.0 / reynolds
        warnings.append(
            f"Reynolds {reynolds:.0f} in transitional zone (2300-4000). "
            "Using laminar friction factor f = 64/Re as conservative estimate."
        )
        return create_result(
            value=f_laminar,
            unit="dimensionless",
            formula_used="f = 64/Re (transitional zone, conservative)",
            intermediate_values={
                "reynolds": reynolds,
                "flow_regime": "transitional",
            },
            warnings=warnings,
            source="Conservative approach for transitional flow",
        )

    # Turbulent flow (Re > 4000)
    relative_roughness = roughness / diameter

    if method == "churchill":
        f = _churchill_friction_factor(reynolds, relative_roughness)
        method_name = "Churchill (explicit)"
    else:  # colebrook
        f = _colebrook_friction_factor(reynolds, relative_roughness)
        method_name = "Colebrook (implicit)"

    return create_result(
        value=f,
        unit="dimensionless",
        formula_used=f"{method_name} correlation",
        intermediate_values={
            "reynolds": reynolds,
            "relative_roughness": relative_roughness,
            "flow_regime": "turbulent",
        },
        warnings=warnings,
        source=f"Crane TP-410 / {method_name}",
    )


def _churchill_friction_factor(reynolds: float, relative_roughness: float) -> float:
    """
    Calculate friction factor using Churchill equation (explicit, valid for all Re > 4000).

    Churchill, S. W. (1977). "Friction‐factor equation spans all fluid‐flow regimes."
    Chemical Engineering, 84(24), 91-92.

    Args:
        reynolds: Reynolds number
        relative_roughness: Absolute roughness / diameter

    Returns:
        Friction factor
    """
    # A and B coefficients
    a_inv = (-2.457 * math.log((relative_roughness / 3.7) ** 1.1 + 5.74 / reynolds**0.9)) ** 2
    a_inv = max(a_inv, 0)  # Ensure non-negative

    b_inv = (37530 / reynolds) ** 16
    b_inv = max(b_inv, 0)

    f: float = float(8 * ((8 / reynolds) ** 12 + 1 / (a_inv + b_inv) ** 1.5) ** (1 / 12))

    return f


def _colebrook_friction_factor(reynolds: float, relative_roughness: float) -> float:
    """
    Calculate friction factor using Colebrook equation (implicit).

    Colebrook, C. F., & White, C. M. (1937).
    "Experiments with Fluid Friction in Roughened Pipes."

    Uses scipy.optimize.brentq to solve the implicit equation.

    Args:
        reynolds: Reynolds number
        relative_roughness: Absolute roughness / diameter

    Returns:
        Friction factor
    """

    def colebrook_equation(f: float) -> float:
        """Colebrook implicit equation: residual."""
        if f <= 0:
            return float("inf")
        term1 = relative_roughness / 3.7
        term2 = 2.51 / (reynolds * math.sqrt(f))
        residual = 1 / math.sqrt(f) + 2 * math.log10(term1 + term2)
        return residual

    # Initial guess using Swamee-Jain approximation
    f_guess = 0.25 / (math.log10(relative_roughness / 3.7 + 5.74 / reynolds**0.9) ** 2)

    # Solve using Brent's method
    try:
        f = optimize.brentq(colebrook_equation, 0.008, 0.1, xtol=1e-6)
    except ValueError:
        # Fallback to initial guess if brentq fails
        f = f_guess

    return float(f)
