"""Peng-Robinson equation of state implementation."""

import logging
import math
from typing import Optional

from ..compounds.models import Compound
from .cubic_solver import solve_cubic
from .models import Mixture, PhaseType, ThermodynamicState

logger = logging.getLogger(__name__)


class PengRobinsonEOS:
    """Peng-Robinson equation of state solver."""

    # Gas constant in Pa*m^3/(mol*K)
    R = 8.314462618

    def __init__(self) -> None:
        """Initialize Peng-Robinson EOS solver."""
        logger.debug("Initializing PengRobinsonEOS")

    @staticmethod
    def calculate_a(tc: float, pc: float, omega: float, temperature: float) -> float:
        """Calculate the 'a' parameter in Peng-Robinson EOS.

        Parameters
        ----------
        tc : float
            Critical temperature in K
        pc : float
            Critical pressure in Pa
        omega : float
            Acentric factor
        temperature : float
            Temperature in K

        Returns
        -------
        float
            Parameter 'a' in Pa*m^6*mol^-2
        """
        if temperature <= 0:
            raise ValueError(f"Temperature must be positive, got {temperature}")
        if tc <= 0:
            raise ValueError(f"Critical temperature must be positive, got {tc}")
        if pc <= 0:
            raise ValueError(f"Critical pressure must be positive, got {pc}")

        tr = temperature / tc
        alpha_func = (1 + (0.37464 + 1.54226 * omega - 0.26992 * omega**2) * (1 - math.sqrt(tr))) ** 2

        a0 = 0.45724 * (PengRobinsonEOS.R**2 * tc**2) / pc
        a = a0 * alpha_func

        logger.debug(
            f"Calculated a={a:.6e} Pa*m^6/mol^2 for T={temperature}K, Tc={tc}K, omega={omega}"
        )
        return a

    @staticmethod
    def calculate_b(tc: float, pc: float) -> float:
        """Calculate the 'b' parameter in Peng-Robinson EOS.

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
        """
        if tc <= 0:
            raise ValueError(f"Critical temperature must be positive, got {tc}")
        if pc <= 0:
            raise ValueError(f"Critical pressure must be positive, got {pc}")

        b = 0.07780 * (PengRobinsonEOS.R * tc) / pc

        logger.debug(f"Calculated b={b:.6e} m^3/mol for Tc={tc}K, Pc={pc}Pa")
        return b

    def calculate_z_factor(
        self, temperature: float, pressure: float, compound: Compound
    ) -> tuple[float, ...]:
        """Calculate compressibility factor(s) for a pure component.

        The Peng-Robinson EOS gives a cubic equation in Z:
        Z^3 - (1 - B)Z^2 + (A - 3B^2 - 2B)Z - (AB - B^2 - B^3) = 0

        Parameters
        ----------
        temperature : float
            Temperature in K
        pressure : float
            Pressure in Pa
        compound : Compound
            Compound object with critical properties

        Returns
        -------
        tuple[float, ...]
            Sorted Z factors (smallest=liquid phase, largest=vapor phase)

        Raises
        ------
        ValueError
            If temperature or pressure is invalid
        """
        if temperature <= 0:
            raise ValueError(f"Temperature must be positive, got {temperature}")
        if pressure <= 0:
            raise ValueError(f"Pressure must be positive, got {pressure}")

        logger.debug(f"Calculating Z factor for {compound.name} at T={temperature}K, P={pressure}Pa")

        # Calculate EOS parameters
        a = self.calculate_a(compound.tc, compound.pc, compound.acentric_factor, temperature)
        b = self.calculate_b(compound.tc, compound.pc)

        # Dimensionless parameters
        A = (a * pressure) / (PengRobinsonEOS.R**2 * temperature**2)
        B = (b * pressure) / (PengRobinsonEOS.R * temperature)

        logger.debug(f"A={A:.6f}, B={B:.6f}")

        # Cubic coefficients for: Z^3 - (1-B)Z^2 + (A-3B^2-2B)Z - (AB-B^2-B^3) = 0
        coeff_z3 = 1.0
        coeff_z2 = -(1 - B)
        coeff_z1 = A - 3 * B**2 - 2 * B
        coeff_z0 = -(A * B - B**2 - B**3)

        logger.debug(
            f"Cubic coefficients: Z^3 + {coeff_z2:.6f}Z^2 + {coeff_z1:.6f}Z + {coeff_z0:.6f} = 0"
        )

        # Solve cubic equation
        z_factors = solve_cubic(coeff_z3, coeff_z2, coeff_z1, coeff_z0, method="hybrid")

        # Filter for physically meaningful Z factors (Z > 0)
        valid_z = tuple(z for z in z_factors if z > 0)

        logger.debug(f"Found {len(valid_z)} valid Z factors: {valid_z}")

        if not valid_z:
            raise ValueError(f"No valid Z factors found for {compound.name} at T={temperature}, P={pressure}")

        return valid_z

    def calculate_fugacity_coefficient(
        self,
        temperature: float,
        pressure: float,
        compound: Compound,
        phase: Optional[PhaseType] = None,
    ) -> float:
        """Calculate fugacity coefficient for a pure component.

        Parameters
        ----------
        temperature : float
            Temperature in K
        pressure : float
            Pressure in Pa
        compound : Compound
            Compound object
        phase : PhaseType, optional
            Specific phase to use (LIQUID or VAPOR). If None, returns vapor phase.

        Returns
        -------
        float
            Fugacity coefficient

        Raises
        ------
        ValueError
            If phase cannot be determined or calculated
        """
        logger.debug(f"Calculating fugacity coefficient for {compound.name} at T={temperature}K, P={pressure}Pa")

        # Get Z factors
        z_factors = self.calculate_z_factor(temperature, pressure, compound)

        # Select appropriate Z factor
        if phase == PhaseType.LIQUID or phase == "liquid":
            z = z_factors[0]  # smallest Z
            logger.debug(f"Using liquid Z factor: {z}")
        else:
            z = z_factors[-1]  # largest Z
            logger.debug(f"Using vapor Z factor: {z}")

        # Calculate parameters
        a = self.calculate_a(compound.tc, compound.pc, compound.acentric_factor, temperature)
        b = self.calculate_b(compound.tc, compound.pc)

        A = (a * pressure) / (PengRobinsonEOS.R**2 * temperature**2)
        B = (b * pressure) / (PengRobinsonEOS.R * temperature)

        # Fugacity coefficient calculation for PR-EOS
        # ln(φ) = Z - 1 - ln(Z - B) + (A / (2*sqrt(2)*B)) * ln((Z + (1 - sqrt(2))*B) / (Z + (1 + sqrt(2))*B))
        sqrt_2 = math.sqrt(2)

        if z <= B:
            raise ValueError(f"Invalid Z factor {z} relative to B={B}")

        ln_phi = (
            z - 1
            - math.log(z - B)
            + (A / (2 * sqrt_2 * B))
            * math.log(
                (z + (1 - sqrt_2) * B) / (z + (1 + sqrt_2) * B)
            )
        )

        phi = math.exp(ln_phi)
        logger.debug(f"Fugacity coefficient: {phi:.6f}")

        return phi

    def identify_phase(
        self,
        temperature: float,
        pressure: float,
        compound: Compound,
        z_factors: Optional[tuple[float, ...]] = None,
    ) -> PhaseType:
        """Identify the thermodynamic phase.

        Parameters
        ----------
        temperature : float
            Temperature in K
        pressure : float
            Pressure in Pa
        compound : Compound
            Compound object
        z_factors : tuple[float, ...], optional
            Pre-calculated Z factors. If None, will be calculated.

        Returns
        -------
        PhaseType
            Identified phase (VAPOR, LIQUID, SUPERCRITICAL, or TWO_PHASE)
        """
        logger.debug(f"Identifying phase for {compound.name} at T={temperature}K, P={pressure}Pa")

        # Check if supercritical
        if temperature > compound.tc or pressure > compound.pc:
            logger.debug(f"Supercritical: T>{compound.tc} or P>{compound.pc}")
            return PhaseType.SUPERCRITICAL

        # Get Z factors if not provided
        if z_factors is None:
            try:
                z_factors = self.calculate_z_factor(temperature, pressure, compound)
            except ValueError:
                logger.warning(f"Could not calculate Z factors for phase identification")
                return PhaseType.UNKNOWN

        # Three real roots indicate two-phase region
        if len(z_factors) >= 3:
            logger.debug(f"Two-phase region: {len(z_factors)} real Z factors")
            return PhaseType.TWO_PHASE

        # One real root indicates single phase
        if len(z_factors) == 1:
            # Below critical point with one phase - use pressure heuristic
            if pressure > compound.pc / 2:
                logger.debug("Single phase, likely liquid")
                return PhaseType.LIQUID
            else:
                logger.debug("Single phase, likely vapor")
                return PhaseType.VAPOR

        # Two real roots - use largest Z for vapor, smallest for liquid
        logger.debug(f"Two real Z factors: {z_factors}")
        return PhaseType.TWO_PHASE

    def calculate_state(
        self, temperature: float, pressure: float, compound: Compound
    ) -> ThermodynamicState:
        """Calculate complete thermodynamic state for a pure component.

        Parameters
        ----------
        temperature : float
            Temperature in K
        pressure : float
            Pressure in Pa
        compound : Compound
            Compound object

        Returns
        -------
        ThermodynamicState
            Complete state including Z, fugacity coefficient, and identified phase
        """
        logger.debug(f"Calculating complete state for {compound.name}")

        # Calculate Z factors
        z_factors = self.calculate_z_factor(temperature, pressure, compound)

        # Identify phase
        phase = self.identify_phase(temperature, pressure, compound, z_factors)

        # Calculate fugacity coefficient (for vapor phase)
        phi = self.calculate_fugacity_coefficient(temperature, pressure, compound, phase=PhaseType.VAPOR)

        # Calculate fugacity
        fugacity = phi * pressure

        # Use largest Z for state reporting (vapor phase)
        z = z_factors[-1]

        logger.info(
            f"State: {compound.name} at T={temperature}K, P={pressure}Pa: "
            f"Z={z:.4f}, φ={phi:.4f}, f={fugacity:.2e}Pa, phase={phase}"
        )

        return ThermodynamicState(
            temperature=temperature,
            pressure=pressure,
            composition=compound.name,
            phase=phase,
            z_factor=z,
            fugacity_coefficient=phi,
            fugacity=fugacity,
        )
