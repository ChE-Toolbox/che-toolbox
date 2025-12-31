"""Ideal Gas Law implementation - reference baseline for EOS comparisons."""

import logging
from typing import Optional

from ..compounds.models import Compound
from .models import PhaseType, ThermodynamicState

logger = logging.getLogger(__name__)


class IdealGasEOS:
    """Ideal Gas Law solver: PV = nRT.

    This simple model assumes no intermolecular forces and zero molecular volume.
    Used as a reference baseline to understand non-ideal behavior in real gases.

    The compressibility factor Z is always exactly 1.0 by definition.
    """

    # Gas constant in Pa*m^3/(mol*K)
    R = 8.314462618

    def __init__(self) -> None:
        """Initialize Ideal Gas EOS solver."""
        logger.debug("Initializing IdealGasEOS")

    @staticmethod
    def calculate_volume(n: float, temperature: float, pressure: float) -> float:
        """Calculate volume using ideal gas law: V = nRT/P.

        Parameters
        ----------
        n : float
            Number of moles (mol)
        temperature : float
            Temperature in K
        pressure : float
            Pressure in Pa

        Returns
        -------
        float
            Volume in m^3

        Raises
        ------
        ValueError
            If temperature <= 0 or pressure <= 0
        """
        if temperature <= 0:
            raise ValueError(f"Temperature must be positive, got {temperature}")
        if pressure <= 0:
            raise ValueError(f"Pressure must be positive, got {pressure}")
        if n <= 0:
            raise ValueError(f"Number of moles must be positive, got {n}")

        V = (n * IdealGasEOS.R * temperature) / pressure

        logger.debug(
            f"Calculated ideal gas volume V={V:.6e} m³ for "
            f"n={n} mol, T={temperature}K, P={pressure}Pa"
        )
        return V

    @staticmethod
    def calculate_volume_molar(temperature: float, pressure: float) -> float:
        """Calculate molar volume using ideal gas law: V_m = RT/P.

        Parameters
        ----------
        temperature : float
            Temperature in K
        pressure : float
            Pressure in Pa

        Returns
        -------
        float
            Molar volume in m^3*mol^-1
        """
        if temperature <= 0:
            raise ValueError(f"Temperature must be positive, got {temperature}")
        if pressure <= 0:
            raise ValueError(f"Pressure must be positive, got {pressure}")

        v_molar = (IdealGasEOS.R * temperature) / pressure
        return v_molar

    @staticmethod
    def calculate_Z(
        pressure: float, temperature: float, v_molar: float
    ) -> float:
        """Calculate compressibility factor: Z = PV/(nRT).

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
            Compressibility factor (always exactly 1.0 for ideal gas)

        Notes
        -----
        For ideal gas, Z is identically 1.0 by definition.
        Any deviation indicates non-ideal behavior.
        """
        # By definition for ideal gas
        return 1.0

    def calculate_state(
        self,
        compound: Optional[Compound] = None,
        temperature: float = 298.15,
        pressure: float = 101325,
        n: float = 1.0,
    ) -> ThermodynamicState:
        """Calculate complete thermodynamic state using ideal gas law.

        Parameters
        ----------
        compound : Optional[Compound]
            Pure substance (unused, included for API consistency)
        temperature : float
            Temperature in K (default 298.15 K = 25°C)
        pressure : float
            Pressure in Pa (default 101325 Pa = 1 atm)
        n : float, optional
            Number of moles (default 1.0)

        Returns
        -------
        ThermodynamicState
            Complete thermodynamic state with Z=1.0, phase=VAPOR

        Raises
        ------
        ValueError
            If inputs are invalid
        """
        if temperature <= 0:
            raise ValueError(f"Temperature must be positive, got {temperature}")
        if pressure <= 0:
            raise ValueError(f"Pressure must be positive, got {pressure}")
        if n <= 0:
            raise ValueError(f"Number of moles must be positive, got {n}")

        # Calculate molar volume
        v_molar = self.calculate_volume_molar(temperature, pressure)

        # Compressibility factor is always 1.0
        z = 1.0

        # Ideal gas is always in vapor phase
        phase = PhaseType.VAPOR

        compound_name = compound.name if compound else "ideal_gas"
        state = ThermodynamicState(
            temperature=temperature,
            pressure=pressure,
            composition=compound_name,
            phase=phase,
            z_factor=z,
        )
        # Attach additional attributes for convenience (not part of model validation)
        state._n = n  # type: ignore
        state._v_molar = v_molar  # type: ignore

        logger.debug(
            f"Calculated ideal gas state: Z={z:.4f}, V_m={v_molar:.6e} m³/mol"
        )
        return state
