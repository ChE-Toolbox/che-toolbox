"""Solvers for cubic equations of the form: a*x^3 + b*x^2 + c*x + d = 0."""

import logging
import math
from typing import Literal

import numpy as np

logger = logging.getLogger(__name__)


def solve_cubic_analytical(a: float, b: float, c: float, d: float) -> tuple[float, ...]:
    """Solve cubic equation using Cardano's analytical method.

    Solves: a*x^3 + b*x^2 + c*x + d = 0

    Parameters
    ----------
    a : float
        Coefficient of x^3
    b : float
        Coefficient of x^2
    c : float
        Coefficient of x
    d : float
        Constant term

    Returns
    -------
    tuple[float, ...]
        Real roots of the cubic equation
    """
    # Normalize to x^3 + px^2 + qx + r = 0
    if abs(a) < 1e-15:
        raise ValueError("Coefficient 'a' must be non-zero for cubic equation")

    p = b / a
    q = c / a
    r = d / a

    # Convert to depressed cubic: t^3 + At + B = 0
    # using substitution x = t - p/3
    A = q - p**2 / 3
    B = 2 * p**3 / 27 - p * q / 3 + r

    # Use Cardano's formula
    sqrt_part = B**2 / 4 + A**3 / 27
    sqrt_abs = abs(sqrt_part)

    if sqrt_part >= 0:
        cbrt_arg1 = -B / 2 + math.sqrt(sqrt_abs)
    else:
        # Complex cube roots - handle complex arithmetic
        real_part = -B / 2
        imag_part = math.sqrt(sqrt_abs)
        magnitude = math.sqrt(real_part**2 + imag_part**2)
        angle = math.atan2(imag_part, real_part)

        cbrt_arg1_mag = magnitude ** (1 / 3)
        cbrt_arg1_angle = angle / 3
        cbrt_arg1 = cbrt_arg1_mag * math.cos(cbrt_arg1_angle)

    roots = []

    # First root
    if abs(cbrt_arg1) > 1e-15:
        C = cbrt_arg1 ** (1 / 3) if cbrt_arg1 > 0 else -(abs(cbrt_arg1) ** (1 / 3))
        t1 = C - A / (3 * C) if abs(C) > 1e-15 else 0
    else:
        t1 = 0

    x1 = t1 - p / 3
    roots.append(x1)

    # Second and third roots (using complex cube roots)
    omega = (-1 + 1j * math.sqrt(3)) / 2

    if abs(sqrt_abs) > 1e-15 or abs(sqrt_part) > 1e-15:
        C_val = cbrt_arg1 ** (1 / 3) if abs(cbrt_arg1) > 1e-15 else 0

        if abs(C_val) > 1e-15:
            t2 = omega * C_val - A / (3 * omega * C_val)
            t3 = omega**2 * C_val - A / (3 * omega**2 * C_val)

            # Extract real parts if they're actually real
            if abs(t2.imag) < 1e-10:
                roots.append(t2.real - p / 3)
            if abs(t3.imag) < 1e-10:
                roots.append(t3.real - p / 3)

    return tuple(sorted([r for r in roots if isinstance(r, float)]))


def solve_cubic_numpy(a: float, b: float, c: float, d: float) -> tuple[float, ...]:
    """Solve cubic equation using NumPy polynomial root finder.

    Solves: a*x^3 + b*x^2 + c*x + d = 0

    Parameters
    ----------
    a : float
        Coefficient of x^3
    b : float
        Coefficient of x^2
    c : float
        Coefficient of x
    d : float
        Constant term

    Returns
    -------
    tuple[float, ...]
        Real roots of the cubic equation
    """
    if abs(a) < 1e-15:
        raise ValueError("Coefficient 'a' must be non-zero for cubic equation")

    # NumPy polynomial roots expects coefficients in descending order
    coefficients = [a, b, c, d]
    roots_complex = np.roots(coefficients)

    # Extract real roots (imaginary part < 1e-10)
    real_roots = [float(r.real) for r in roots_complex if abs(r.imag) < 1e-10]

    return tuple(sorted(real_roots))


def solve_cubic(
    a: float,
    b: float,
    c: float,
    d: float,
    method: Literal["hybrid", "numpy", "analytical"] = "hybrid",
) -> tuple[float, ...]:
    """Solve cubic equation with multiple methods.

    Solves: a*x^3 + b*x^2 + c*x + d = 0

    Parameters
    ----------
    a : float
        Coefficient of x^3
    b : float
        Coefficient of x^2
    c : float
        Coefficient of x
    d : float
        Constant term
    method : {"hybrid", "numpy", "analytical"}
        Solution method:
        - "hybrid": Try NumPy first, fall back to analytical if needed
        - "numpy": Use NumPy polynomial roots
        - "analytical": Use Cardano's analytical method

    Returns
    -------
    tuple[float, ...]
        Real roots of the cubic equation, sorted in ascending order

    Raises
    ------
    ValueError
        If coefficient 'a' is zero or method is invalid
    """
    if abs(a) < 1e-15:
        raise ValueError("Coefficient 'a' must be non-zero for cubic equation")

    if method not in ("hybrid", "numpy", "analytical"):
        raise ValueError(f"Invalid method: {method}. Must be 'hybrid', 'numpy', or 'analytical'")

    if method == "numpy":
        logger.debug("Solving cubic using NumPy roots")
        return solve_cubic_numpy(a, b, c, d)

    elif method == "analytical":
        logger.debug("Solving cubic using Cardano's analytical method")
        return solve_cubic_analytical(a, b, c, d)

    else:  # hybrid
        logger.debug("Solving cubic using hybrid method (NumPy with analytical fallback)")
        try:
            roots = solve_cubic_numpy(a, b, c, d)
            if len(roots) >= 1:
                logger.debug(f"NumPy solver found {len(roots)} real roots")
                return roots
        except Exception as e:
            logger.debug(f"NumPy solver failed: {e}, falling back to analytical")

        return solve_cubic_analytical(a, b, c, d)
