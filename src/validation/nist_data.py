"""NIST reference data loader and manager."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class NISTDataLoader:
    """Load and parse NIST reference data JSON files."""

    def __init__(self, data_dir: str | Path = "data/nist_reference") -> None:
        """Initialize NIST data loader.

        Parameters
        ----------
        data_dir : str | Path
            Directory containing NIST reference JSON files
        """
        self.data_dir = Path(data_dir)
        if not self.data_dir.exists():
            logger.warning(f"NIST data directory not found: {self.data_dir}")

    def load_compound_data(self, compound_name: str) -> list[dict[str, Any]]:
        """Load NIST reference data for a compound.

        Parameters
        ----------
        compound_name : str
            Compound name (e.g., 'methane', 'water')

        Returns
        -------
        list[dict]
            List of test cases with temperature, pressure, z_factor, fugacity

        Raises
        ------
        FileNotFoundError
            If compound data file not found
        json.JSONDecodeError
            If JSON parsing fails
        """
        filename = f"{compound_name.lower()}.json"
        filepath = self.data_dir / filename

        logger.debug(f"Loading NIST data from {filepath}")

        if not filepath.exists():
            raise FileNotFoundError(f"NIST data file not found: {filepath}")

        try:
            with open(filepath) as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise ValueError(f"Expected list of test cases, got {type(data)}")

            logger.info(f"Loaded {len(data)} test cases for {compound_name}")
            return data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse {filepath}: {e}")
            raise

    def list_available_compounds(self) -> list[str]:
        """List available compounds with NIST data.

        Returns
        -------
        list[str]
            List of compound names (without .json extension)
        """
        if not self.data_dir.exists():
            return []

        compounds = [f.stem for f in self.data_dir.glob("*.json") if f.is_file()]
        logger.debug(f"Found {len(compounds)} compounds with NIST data: {compounds}")
        return sorted(compounds)

    def get_temperature_range(self, compound_name: str) -> tuple[float, float] | None:
        """Get temperature range for compound data.

        Parameters
        ----------
        compound_name : str
            Compound name

        Returns
        -------
        tuple[float, float] | None
            (min_temperature, max_temperature) or None if not found
        """
        try:
            data = self.load_compound_data(compound_name)
            if not data:
                return None

            temperatures = [
                float(d["temperature"])
                for d in data
                if "temperature" in d and d["temperature"] is not None
            ]
            if not temperatures:
                return None

            return (min(temperatures), max(temperatures))
        except Exception as e:
            logger.debug(f"Could not determine temperature range: {e}")
            return None

    def get_pressure_range(self, compound_name: str) -> tuple[float, float] | None:
        """Get pressure range for compound data.

        Parameters
        ----------
        compound_name : str
            Compound name

        Returns
        -------
        tuple[float, float] | None
            (min_pressure, max_pressure) or None if not found
        """
        try:
            data = self.load_compound_data(compound_name)
            if not data:
                return None

            pressures = [
                float(d["pressure"]) for d in data if "pressure" in d and d["pressure"] is not None
            ]
            if not pressures:
                return None

            return (min(pressures), max(pressures))
        except Exception as e:
            logger.debug(f"Could not determine pressure range: {e}")
            return None
