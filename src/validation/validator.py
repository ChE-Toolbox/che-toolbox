"""NIST validation framework."""

import logging

from ..compounds.database import CompoundDatabase
from ..eos.peng_robinson import PengRobinsonEOS
from .models import ValidationResult, ValidationTestCase
from .nist_data import NISTDataLoader

logger = logging.getLogger(__name__)


class NISTValidation:
    """Validate Peng-Robinson EOS implementation against NIST reference data."""

    def __init__(
        self,
        eos: PengRobinsonEOS | None = None,
        db: CompoundDatabase | None = None,
        nist_loader: NISTDataLoader | None = None,
    ) -> None:
        """Initialize NIST validator.

        Parameters
        ----------
        eos : PengRobinsonEOS, optional
            EOS solver instance (creates new if None)
        db : CompoundDatabase, optional
            Compound database (creates new if None, loads data/compounds.json)
        nist_loader : NISTDataLoader, optional
            NIST data loader (creates new if None, uses data/nist_reference)
        """
        self.eos = eos or PengRobinsonEOS()
        self.db = db or CompoundDatabase("data/compounds.json")
        self.nist_loader = nist_loader or NISTDataLoader("data/nist_reference")

        logger.debug("Initialized NIST validator")

    def validate_z_factor(
        self,
        temperature: float,
        pressure: float,
        compound_name: str,
        expected_z: float,
        tolerance: float = 0.05,
    ) -> tuple[bool, float, str | None]:
        """Validate Z factor calculation.

        Parameters
        ----------
        temperature : float
            Temperature in K
        pressure : float
            Pressure in Pa
        compound_name : str
            Compound name
        expected_z : float
            Expected Z factor from NIST
        tolerance : float
            Tolerance for deviation (default 0.05 = 5%)

        Returns
        -------
        tuple[bool, float, Optional[str]]
            (passed, deviation, error_message)
        """
        try:
            compound = self.db.get(compound_name)
            if not compound:
                return False, float("nan"), f"Compound not found: {compound_name}"

            z_factors = self.eos.calculate_z_factor(temperature, pressure, compound)
            # Use largest Z (vapor phase)
            calculated_z = z_factors[-1]

            # Calculate relative deviation
            if expected_z == 0:
                deviation = abs(calculated_z - expected_z)
            else:
                deviation = abs(calculated_z - expected_z) / abs(expected_z)

            passed = deviation <= tolerance
            return passed, deviation, None

        except Exception as e:
            logger.warning(f"Error validating Z factor: {e}")
            return False, float("nan"), str(e)

    def validate_fugacity(
        self,
        temperature: float,
        pressure: float,
        compound_name: str,
        expected_fugacity: float,
        tolerance: float = 0.10,
    ) -> tuple[bool, float, str | None]:
        """Validate fugacity calculation.

        Parameters
        ----------
        temperature : float
            Temperature in K
        pressure : float
            Pressure in Pa
        compound_name : str
            Compound name
        expected_fugacity : float
            Expected fugacity in Pa
        tolerance : float
            Tolerance for deviation (default 0.10 = 10%)

        Returns
        -------
        tuple[bool, float, Optional[str]]
            (passed, deviation, error_message)
        """
        try:
            compound = self.db.get(compound_name)
            if not compound:
                return False, float("nan"), f"Compound not found: {compound_name}"

            phi = self.eos.calculate_fugacity_coefficient(temperature, pressure, compound)
            calculated_fugacity = phi * pressure

            # Calculate relative deviation
            if expected_fugacity == 0:
                deviation = abs(calculated_fugacity - expected_fugacity)
            else:
                deviation = abs(calculated_fugacity - expected_fugacity) / abs(expected_fugacity)

            passed = deviation <= tolerance
            return passed, deviation, None

        except Exception as e:
            logger.warning(f"Error validating fugacity: {e}")
            return False, float("nan"), str(e)

    def validate_vapor_pressure(
        self,
        temperature: float,
        compound_name: str,
        expected_vapor_pressure: float,
        tolerance: float = 0.05,
    ) -> tuple[bool, float, str | None]:
        """Validate vapor pressure calculation.

        Parameters
        ----------
        temperature : float
            Temperature in K
        compound_name : str
            Compound name
        expected_vapor_pressure : float
            Expected vapor pressure in Pa
        tolerance : float
            Tolerance for deviation (default 0.05 = 5%)

        Returns
        -------
        tuple[bool, float, Optional[str]]
            (passed, deviation, error_message)
        """
        try:
            compound = self.db.get(compound_name)
            if not compound:
                return False, float("nan"), f"Compound not found: {compound_name}"

            # Check if temperature is subcritical
            if temperature >= compound.tc:
                return False, float("nan"), "Temperature is at or above critical temperature"

            calculated_psat = self.eos.calculate_vapor_pressure(temperature, compound)

            # Calculate relative deviation
            if expected_vapor_pressure == 0:
                deviation = abs(calculated_psat - expected_vapor_pressure)
            else:
                deviation = abs(calculated_psat - expected_vapor_pressure) / abs(expected_vapor_pressure)

            passed = deviation <= tolerance
            return passed, deviation, None

        except Exception as e:
            logger.warning(f"Error validating vapor pressure: {e}")
            return False, float("nan"), str(e)

    def validate_test_case(self, test_case: ValidationTestCase) -> ValidationResult:
        """Validate a single test case.

        Parameters
        ----------
        test_case : ValidationTestCase
            Test case to validate

        Returns
        -------
        ValidationResult
            Validation result with calculated values and pass/fail status
        """
        logger.debug(f"Validating {test_case.compound_name} at T={test_case.temperature}K, P={test_case.pressure}Pa")

        result = ValidationResult(test_case=test_case)

        try:
            compound = self.db.get(test_case.compound_name)
            if not compound:
                result.error_message = f"Compound not found: {test_case.compound_name}"
                return result

            # Calculate Z factor if expected
            if test_case.expected_z_factor is not None:
                z_factors = self.eos.calculate_z_factor(test_case.temperature, test_case.pressure, compound)
                result.calculated_z_factor = z_factors[-1]

                deviation = abs(result.calculated_z_factor - test_case.expected_z_factor) / abs(
                    test_case.expected_z_factor
                )
                result.z_factor_deviation = deviation
                result.z_factor_passed = deviation <= test_case.tolerance_z

            # Calculate fugacity if expected
            if test_case.expected_fugacity is not None:
                phi = self.eos.calculate_fugacity_coefficient(
                    test_case.temperature, test_case.pressure, compound
                )
                result.calculated_fugacity = phi * test_case.pressure

                deviation = abs(result.calculated_fugacity - test_case.expected_fugacity) / abs(
                    test_case.expected_fugacity
                )
                result.fugacity_deviation = deviation
                result.fugacity_passed = deviation <= test_case.tolerance_fugacity

        except Exception as e:
            logger.error(f"Error validating test case: {e}")
            result.error_message = str(e)

        return result
