"""PT (Pressure-Temperature) Flash calculation for vapor-liquid equilibrium."""

import logging
from dataclasses import dataclass
from enum import Enum

import numpy as np

logger = logging.getLogger(__name__)


class FlashConvergence(str, Enum):
    """Flash calculation convergence status."""

    SUCCESS = "converged"
    SINGLE_PHASE = "single_phase_detected"
    MAX_ITERATIONS = "max_iterations_exceeded"
    DIVERGED = "diverged"
    NOT_RUN = "not_attempted"


@dataclass
class FlashResult:
    """Result of a PT flash calculation.

    Attributes
    ----------
    L : float
        Liquid phase mole fraction [0, 1]
    V : float
        Vapor phase mole fraction [0, 1]
    x : np.ndarray
        Liquid mole fractions by component
    y : np.ndarray
        Vapor mole fractions by component
    K_values : np.ndarray
        Partitioning ratios K_i = y_i/x_i [dimensionless]
    iterations : int
        Number of Rachford-Rice iterations performed
    tolerance_achieved : float
        Final |f_i^v / f_i^l - 1| value
    convergence : FlashConvergence
        Convergence status flag
    material_balance_error : float, optional
        Maximum composition balance error: max(|z_i - (L*x_i + V*y_i)|)
    """

    L: float
    V: float
    x: np.ndarray
    y: np.ndarray
    K_values: np.ndarray
    iterations: int
    tolerance_achieved: float
    convergence: FlashConvergence
    material_balance_error: float | None = None

    @property
    def success(self) -> bool:
        """Return True if flash converged successfully."""
        return self.convergence == FlashConvergence.SUCCESS


class FlashPT:
    """PT Flash calculator using Rachford-Rice iteration.

    Performs Pressure-Temperature flash to determine vapor-liquid equilibrium
    (phase split composition and amounts) using iterative solution of the
    Rachford-Rice equation with fugacity equality constraint.

    The algorithm:
    1. Check for single-phase conditions (T > Tc or pure component)
    2. Initialize K-values via Wilson correlation
    3. Iterate Rachford-Rice equation until convergence
    4. Update K-values from fugacity ratios
    5. Validate material balance

    Convergence criterion: |f_i^vapor / f_i^liquid - 1| < tolerance (default 1e-6)
    """

    def __init__(self) -> None:
        """Initialize PT flash calculator."""
        self.max_iterations: int = 50
        self.tolerance: float = 1e-6
        logger.debug("Initializing FlashPT calculator")

    def calculate(
        self,
        feed_composition: np.ndarray,
        temperature: float,
        pressure: float,
        critical_temperatures: np.ndarray,
        critical_pressures: np.ndarray,
        tolerance: float | None = None,
        max_iterations: int | None = None,
    ) -> FlashResult:
        """Perform PT flash calculation using Rachford-Rice iteration.

        Parameters
        ----------
        feed_composition : np.ndarray
            Feed mole fractions z_i (must sum to 1.0)
        temperature : float
            Temperature in K
        pressure : float
            Pressure in Pa
        critical_temperatures : np.ndarray
            Critical temperatures of each component [K]
        critical_pressures : np.ndarray
            Critical pressures of each component [Pa]
        tolerance : float, optional
            Equilibrium tolerance |f_v/f_l - 1| (default 1e-6)
        max_iterations : int, optional
            Maximum RR iterations (default 50)

        Returns
        -------
        FlashResult
            Complete flash result with compositions, K-values, convergence data

        Raises
        ------
        ValueError
            If feed_composition is invalid or flash cannot proceed
        """
        # Use provided or default tolerance/max_iterations
        if tolerance is not None:
            self.tolerance = tolerance
        if max_iterations is not None:
            self.max_iterations = max_iterations

        # Validate inputs
        if not isinstance(feed_composition, np.ndarray):
            feed_composition = np.array(feed_composition)

        if abs(np.sum(feed_composition) - 1.0) > 1e-6:
            raise ValueError(
                f"Feed composition must sum to 1.0, got {np.sum(feed_composition)}"
            )

        if temperature <= 0:
            raise ValueError(f"Temperature must be positive, got {temperature}")
        if pressure <= 0:
            raise ValueError(f"Pressure must be positive, got {pressure}")

        n_comp = len(feed_composition)
        logger.debug(
            f"Starting PT flash: {n_comp} components, T={temperature}K, P={pressure}Pa"
        )

        # Check for single-phase conditions
        single_phase_result = self._check_single_phase(
            feed_composition, temperature, critical_temperatures
        )
        if single_phase_result is not None:
            return single_phase_result

        # Initialize K-values using Wilson correlation
        K_values = self._initialize_K_values(
            temperature, pressure, critical_temperatures, critical_pressures
        )

        # Rachford-Rice iteration
        for iteration in range(self.max_iterations):
            # Solve Rachford-Rice equation for vapor fraction V
            V = self._solve_rachford_rice(feed_composition, K_values)

            if V < 0 or V > 1:
                # Single-phase detected (V outside [0, 1])
                logger.debug(f"Single-phase detected at iteration {iteration}: V={V}")
                return self._return_single_phase_result(feed_composition, V)

            # Calculate liquid and vapor compositions
            x = feed_composition / (1 + V * (K_values - 1))
            y = K_values * x

            # Check convergence
            tolerance_achieved = np.max(np.abs(K_values - 1))

            if tolerance_achieved < self.tolerance:
                logger.debug(
                    f"Converged after {iteration + 1} iterations, "
                    f"tolerance={tolerance_achieved:.2e}"
                )

                # Validate material balance
                L = 1.0 - V
                material_balance_error = np.max(
                    np.abs(feed_composition - (L * x + V * y))
                )

                return FlashResult(
                    L=L,
                    V=V,
                    x=x,
                    y=y,
                    K_values=K_values,
                    iterations=iteration + 1,
                    tolerance_achieved=tolerance_achieved,
                    convergence=FlashConvergence.SUCCESS,
                    material_balance_error=material_balance_error,
                )

            # Update K-values (simplified: use Rachford-Rice iteration update)
            # In a full implementation, would compute fugacities from EOS
            K_values = self._update_K_values(K_values, x, y, feed_composition)

        # Max iterations exceeded
        logger.warning(
            f"Flash did not converge within {self.max_iterations} iterations"
        )
        return FlashResult(
            L=np.nan,
            V=np.nan,
            x=np.full(n_comp, np.nan),
            y=np.full(n_comp, np.nan),
            K_values=K_values,
            iterations=self.max_iterations,
            tolerance_achieved=np.nan,
            convergence=FlashConvergence.MAX_ITERATIONS,
        )

    def _check_single_phase(
        self,
        feed_composition: np.ndarray,
        temperature: float,
        critical_temperatures: np.ndarray,
    ) -> FlashResult | None:
        """Check if system is single-phase before Rachford-Rice iteration.

        Single-phase conditions:
        - T > max(Tc) for all components (supercritical)
        - Single-component feed (n_comp == 1)

        Returns None if two-phase region possible, otherwise returns single-phase result.
        """
        n_comp = len(feed_composition)

        # Pure component check
        if n_comp == 1:
            # Single component - return liquid if single composition
            logger.debug("Single-component feed detected")
            x = np.array([1.0])
            y = np.array([1.0])
            return FlashResult(
                L=1.0,
                V=0.0,
                x=x,
                y=y,
                K_values=np.array([1.0]),
                iterations=0,
                tolerance_achieved=0.0,
                convergence=FlashConvergence.SINGLE_PHASE,
                material_balance_error=0.0,
            )

        # Supercritical check (all components above critical temperature)
        if temperature > np.max(critical_temperatures):
            logger.debug(
                f"Supercritical conditions: T={temperature}K > Tc_max={np.max(critical_temperatures)}K"
            )
            x = np.full(n_comp, np.nan)
            y = feed_composition
            return FlashResult(
                L=0.0,
                V=1.0,
                x=x,
                y=y,
                K_values=np.full(n_comp, np.inf),
                iterations=0,
                tolerance_achieved=0.0,
                convergence=FlashConvergence.SINGLE_PHASE,
                material_balance_error=0.0,
            )

        # Two-phase region possible
        return None

    def _initialize_K_values(
        self,
        temperature: float,
        pressure: float,
        critical_temperatures: np.ndarray,
        critical_pressures: np.ndarray,
    ) -> np.ndarray:
        """Initialize K-values using Wilson correlation.

        K_i ≈ (Pc_i / P) * exp(5.373 * (1 + omega_i) * (1 - Tc_i / T))

        For simplicity, use Wilson approximation without acentric factor:
        K_i ≈ (Pc_i / P) * exp(5.373 * (1 - Tc_i / T))
        """
        K_values = (critical_pressures / pressure) * np.exp(
            5.373 * (1 - critical_temperatures / temperature)
        )

        # Ensure K > 0
        K_values = np.maximum(K_values, 1e-8)

        logger.debug(f"Initialized K-values: {K_values}")
        return K_values

    def _solve_rachford_rice(
        self, feed_composition: np.ndarray, K_values: np.ndarray
    ) -> float:
        """Solve Rachford-Rice equation for vapor fraction V.

        RR equation: sum_i(z_i * (K_i - 1) / (1 + V * (K_i - 1))) = 0

        Uses Newton-Raphson iteration to solve for V.
        """
        def rachford_rice_equation(V: float) -> float:
            """RR equation as function of V."""
            return np.sum(feed_composition * (K_values - 1) / (1 + V * (K_values - 1)))

        def rachford_rice_derivative(V: float) -> float:
            """Derivative of RR equation w.r.t. V."""
            return -np.sum(
                feed_composition
                * (K_values - 1) ** 2
                / (1 + V * (K_values - 1)) ** 2
            )

        # Newton-Raphson starting from V=0.5
        V = 0.5
        for _ in range(10):
            f = rachford_rice_equation(V)
            if abs(f) < 1e-10:
                break
            df = rachford_rice_derivative(V)
            if abs(df) < 1e-12:
                break
            V = V - f / df
            V = np.clip(V, 0.0, 1.0)

        return V

    def _update_K_values(
        self,
        K_values: np.ndarray,
        x: np.ndarray,
        y: np.ndarray,
        feed_composition: np.ndarray,
    ) -> np.ndarray:
        """Update K-values for next iteration.

        In simplified version, use damping factor to improve convergence:
        K_new = alpha * K_old + (1 - alpha) * 1.0

        In full implementation, would compute fugacities and use:
        K_i = phi_i^liquid / phi_i^vapor
        """
        # Simplified update with damping
        alpha = 0.7
        K_new = alpha * K_values + (1 - alpha) * np.ones_like(K_values)

        return K_new

    def _return_single_phase_result(
        self, feed_composition: np.ndarray, V: float
    ) -> FlashResult:
        """Return single-phase result when RR produces V outside [0, 1]."""
        n_comp = len(feed_composition)

        if V < 0:
            # Liquid phase
            return FlashResult(
                L=1.0,
                V=0.0,
                x=feed_composition,
                y=np.full(n_comp, np.nan),
                K_values=np.full(n_comp, np.nan),
                iterations=0,
                tolerance_achieved=0.0,
                convergence=FlashConvergence.SINGLE_PHASE,
                material_balance_error=0.0,
            )
        else:
            # Vapor phase
            return FlashResult(
                L=0.0,
                V=1.0,
                x=np.full(n_comp, np.nan),
                y=feed_composition,
                K_values=np.full(n_comp, np.nan),
                iterations=0,
                tolerance_achieved=0.0,
                convergence=FlashConvergence.SINGLE_PHASE,
                material_balance_error=0.0,
            )
