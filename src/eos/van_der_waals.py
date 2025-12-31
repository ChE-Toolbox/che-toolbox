"""Van der Waals equation of state implementation."""

import logging

from ..compounds.models import Compound
from .cubic_solver import solve_cubic
from .models import PhaseType, ThermodynamicState

logger = logging.getLogger(__name__)


class VanDerWaalsEOS:
    """Van der Waals equation of state solver.

    The Van der Waals EOS accounts for molecular volume (b parameter) and
    intermolecular attractions (a parameter):

        (P + a/V²)(V - b) = RT

    This is simpler than Peng-Robinson but effective for many applications.
    """

    # Gas constant in Pa*m^3/(mol*K)
    R = 8.314462618

    def __init__(self) -> None:
        """Initialize Van der Waals EOS solver."""
        logger.debug("Initializing VanDerWaalsEOS")

    @staticmethod
    def calculate_a(tc: float, pc: float, temperature: float | None = None) -> float:
        """Calculate the 'a' parameter in Van der Waals EOS.

        Parameters
        ----------
        tc : float
            Critical temperature in K
        pc : float
            Critical pressure in Pa
        temperature : Optional[float]
            Temperature in K (not used for VDW, included for API consistency with PR)

        Returns
        -------
        float
            Parameter 'a' in Pa*m^6*mol^-2

        Raises
        ------
        ValueError
            If tc <= 0 or pc <= 0

        Notes
        -----
        For Van der Waals, 'a' is independent of temperature, unlike Peng-Robinson.

        a = 27*R²*Tc²/(64*Pc)
        """
        if tc <= 0:
            raise ValueError(f"Critical temperature must be positive, got {tc}")
        if pc <= 0:
            raise ValueError(f"Critical pressure must be positive, got {pc}")

        a = (27 * VanDerWaalsEOS.R**2 * tc**2) / (64 * pc)

        logger.debug(
            f"Calculated a={a:.6e} Pa*m^6/mol^2 for Tc={tc}K, Pc={pc}Pa"
        )
        return a

    @staticmethod
    def calculate_b(tc: float, pc: float) -> float:
        """Calculate the 'b' parameter in Van der Waals EOS.

        Parameters
        ----------
        tc : float
            Critical temperature in K
        pc : float
            Critical pressure in Pa

        Returns
        -------
        float
            Parameter 'b' in m^3*mol^-1

        Raises
        ------
        ValueError
            If tc <= 0 or pc <= 0

        Notes
        -----
        b = R*Tc/(8*Pc)
        """
        if tc <= 0:
            raise ValueError(f"Critical temperature must be positive, got {tc}")
        if pc <= 0:
            raise ValueError(f"Critical pressure must be positive, got {pc}")

        b = (VanDerWaalsEOS.R * tc) / (8 * pc)

        logger.debug(
            f"Calculated b={b:.6e} m^3/mol for Tc={tc}K, Pc={pc}Pa"
        )
        return b

    def calculate_volume(
        self,
        tc: float,
        pc: float,
        temperature: float,
        pressure: float,
    ) -> float:
        """Calculate molar volume by solving Van der Waals cubic equation.

        Parameters
        ----------
        tc : float
            Critical temperature in K
        pc : float
            Critical pressure in Pa
        temperature : float
            Temperature in K
        pressure : float
            Pressure in Pa

        Returns
        -------
        float
            Molar volume in m^3*mol^-1

        Raises
        ------
        ValueError
            If temperature <= 0, pressure < 0, or cubic has no real roots

        Notes
        -----
        Solves: (P + a/V²)(V - b) = RT

        Rearranged to cubic form:
        V³ - (b + RT/P)V² + (a/P)V - ab/P = 0
        """
        if temperature <= 0:
            raise ValueError(f"Temperature must be positive, got {temperature}")
        if pressure < 0:
            raise ValueError(f"Pressure must be non-negative, got {pressure}")

        # Calculate EOS parameters
        a = self.calculate_a(tc, pc, temperature)
        b = self.calculate_b(tc, pc)

        # Solve cubic equation: V³ - (b + RT/P)V² + (a/P)V - ab/P = 0
        # In form: a*V³ + b*V² + c*V + d = 0
        # Coefficients:
        a_coeff = 1.0
        b_coeff = -(b + self.R * temperature / pressure)
        c_coeff = a / pressure
        d_coeff = -a * b / pressure

        roots = solve_cubic(a_coeff, b_coeff, c_coeff, d_coeff)

        # Filter real, positive roots
        valid_roots = [root for root in roots if isinstance(root, float) and root > 0]

        if not valid_roots:
            raise ValueError(
                f"No positive real roots found for Van der Waals cubic at "
                f"T={temperature}K, P={pressure}Pa"
            )

        # Choose root closest to ideal gas volume
        v_ideal = self.R * temperature / pressure
        v_molar = min(valid_roots, key=lambda v: abs(v - v_ideal))

        logger.debug(
            f"Calculated V={v_molar:.6e} m³/mol for T={temperature}K, P={pressure}Pa"
        )
        return v_molar

    @staticmethod
    def calculate_Z(pressure: float, temperature: float, v_molar: float) -> float:
        """Calculate compressibility factor Z = PV/(nRT).

        Parameters
        ----------
        pressure : float
            Pressure in Pa
        temperature : float
            Temperature in K
        v_molar : float
            Molar volume in m^3*mol^-1

        Returns
        -------
        float
            Compressibility factor (dimensionless)

        Notes
        -----
        Z = 1 for ideal gas. Z < 1 when attractive forces dominate,
        Z > 1 when repulsive forces (molecular volume) dominate.
        """
        if temperature <= 0:
            raise ValueError(f"Temperature must be positive, got {temperature}")
        if v_molar <= 0:
            raise ValueError(f"Molar volume must be positive, got {v_molar}")

        Z = (pressure * v_molar) / (VanDerWaalsEOS.R * temperature)
        return Z

    def calculate_state(
        self,
        compound: Compound,
        temperature: float,
        pressure: float,
        n: float = 1.0,
    ) -> ThermodynamicState:
        """Calculate complete thermodynamic state using Van der Waals EOS.

        Parameters
        ----------
        compound : Compound
            Pure substance with critical properties (tc, pc)
        temperature : float
            Temperature in K
        pressure : float
            Pressure in Pa
        n : float, optional
            Number of moles (default 1.0)

        Returns
        -------
        ThermodynamicState
            Complete thermodynamic state with volume, Z-factor, phase

        Raises
        ------
        ValueError
            If inputs are invalid or cubic solve fails
        """
        if n <= 0:
            raise ValueError(f"Number of moles must be positive, got {n}")

        # Calculate molar volume
        v_molar = self.calculate_volume(compound.tc, compound.pc, temperature, pressure)

        # Calculate compressibility factor
        z = self.calculate_Z(pressure, temperature, v_molar)

        # Determine phase (simplified: vapor if T > Tc, liquid otherwise at saturation)
        if temperature > compound.tc:
            phase = PhaseType.SUPERCRITICAL
        elif pressure > compound.pc:
            phase = PhaseType.LIQUID
        else:
            phase = PhaseType.VAPOR

        # Store additional state properties on the state object
        # Note: ThermodynamicState uses standard field names (temperature, pressure, composition, z_factor)
        # Additional fields are stored as a custom dict to preserve the data
        state = ThermodynamicState(
            temperature=temperature,
            pressure=pressure,
            composition=compound.name,
            phase=phase,
            z_factor=z,
        )
        # Attach additional attributes for convenience (not part of model validation)
        state._n = n  # type: ignore
        state._v_molar = v_molar  # type: ignore

        logger.debug(f"Calculated VDW state: Z={z:.4f}, phase={phase.value}")
        return state
