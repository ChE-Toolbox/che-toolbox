"""Van der Waals mixing rules for multi-component mixtures."""

import logging
import math

logger = logging.getLogger(__name__)


def calculate_a_mix(
    a_values: list[float],
    mole_fractions: list[float],
    kij_matrix: list[list[float]],
) -> float:
    """Calculate the 'a' parameter for a mixture using van der Waals mixing rules.

    Uses geometric mean: a_ij = (1 - kij) * sqrt(ai * aj)

    Parameters
    ----------
    a_values : list[float]
        Pure component 'a' values for each component
    mole_fractions : list[float]
        Mole fraction of each component (must sum to 1.0)
    kij_matrix : list[list[float]]
        Binary interaction parameter matrix (symmetric)

    Returns
    -------
    float
        Mixed 'a' parameter

    Raises
    ------
    ValueError
        If dimensions don't match or validation fails
    """
    n_components = len(a_values)

    if len(mole_fractions) != n_components:
        raise ValueError(
            f"Length mismatch: a_values ({n_components}) != mole_fractions ({len(mole_fractions)})"
        )

    if len(kij_matrix) != n_components:
        raise ValueError(
            f"kij_matrix dimension {len(kij_matrix)} != number of components {n_components}"
        )

    for i, row in enumerate(kij_matrix):
        if len(row) != n_components:
            raise ValueError(
                f"kij_matrix row {i} has length {len(row)}, expected {n_components}"
            )

    # Validate mole fractions
    total = sum(mole_fractions)
    if abs(total - 1.0) > 1e-6:
        raise ValueError(f"Mole fractions sum to {total}, must be 1.0±1e-6")

    # Calculate a_mix = Σ Σ xi*xj*aij
    a_mix = 0.0
    for i in range(n_components):
        for j in range(n_components):
            if a_values[i] > 0 and a_values[j] > 0:
                a_ij = (1 - kij_matrix[i][j]) * math.sqrt(a_values[i] * a_values[j])
                a_mix += mole_fractions[i] * mole_fractions[j] * a_ij

                logger.debug(
                    f"a[{i},{j}]={a_ij:.6e}, xi*xj*aij={mole_fractions[i] * mole_fractions[j] * a_ij:.6e}"
                )

    logger.debug(f"Mixture 'a' parameter: {a_mix:.6e}")
    return a_mix


def calculate_b_mix(b_values: list[float], mole_fractions: list[float]) -> float:
    """Calculate the 'b' parameter for a mixture using van der Waals mixing rules.

    Uses linear mixing: b_mix = Σ xi*bi

    Parameters
    ----------
    b_values : list[float]
        Pure component 'b' values for each component
    mole_fractions : list[float]
        Mole fraction of each component (must sum to 1.0)

    Returns
    -------
    float
        Mixed 'b' parameter

    Raises
    ------
    ValueError
        If dimensions don't match or validation fails
    """
    if len(b_values) != len(mole_fractions):
        raise ValueError(
            f"Length mismatch: b_values ({len(b_values)}) != mole_fractions ({len(mole_fractions)})"
        )

    # Validate mole fractions
    total = sum(mole_fractions)
    if abs(total - 1.0) > 1e-6:
        raise ValueError(f"Mole fractions sum to {total}, must be 1.0±1e-6")

    # Calculate b_mix = Σ xi*bi
    b_mix = sum(x * b for x, b in zip(mole_fractions, b_values))

    logger.debug(f"Mixture 'b' parameter: {b_mix:.6e}")
    return b_mix


def validate_kij_matrix(kij_matrix: list[list[float]], n_components: int) -> None:
    """Validate binary interaction parameter matrix.

    Parameters
    ----------
    kij_matrix : list[list[float]]
        Binary interaction parameter matrix
    n_components : int
        Expected number of components

    Raises
    ------
    ValueError
        If matrix is invalid or symmetry is violated
    """
    if len(kij_matrix) != n_components:
        raise ValueError(
            f"Matrix dimension {len(kij_matrix)} != number of components {n_components}"
        )

    for i, row in enumerate(kij_matrix):
        if len(row) != n_components:
            raise ValueError(
                f"Matrix row {i} has length {len(row)}, expected {n_components}"
            )

        for j, kij in enumerate(row):
            # Check bounds
            if not (-0.5 < kij < 0.5):
                raise ValueError(f"kij[{i},{j}]={kij} outside bounds (-0.5, 0.5)")

            # Check symmetry: kij should equal kji
            if i != j and abs(kij_matrix[i][j] - kij_matrix[j][i]) > 1e-10:
                raise ValueError(
                    f"Matrix not symmetric: kij[{i},{j}]={kij_matrix[i][j]} != "
                    f"kij[{j},{i}]={kij_matrix[j][i]}"
                )

    logger.debug("kij_matrix validation passed")
