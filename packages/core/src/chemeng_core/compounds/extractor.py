"""CoolProp data extraction utilities for adding new compounds.

This module provides utilities to extract thermophysical properties from CoolProp
and convert them to the standard CompoundDTO format for database storage.
"""

from __future__ import annotations

from datetime import date

try:
    import CoolProp.CoolProp as CP
except ImportError as e:
    raise ImportError(
        "CoolProp is required for compound extraction. Install with: pip install CoolProp"
    ) from e

from chemeng_core.compounds.models import (
    CompoundDTO,
    CriticalPropertiesDTO,
    PhasePropertiesDTO,
    QuantityDTO,
    SourceAttributionDTO,
)


class CoolPropDataExtractor:
    """Extract compound data from CoolProp library.

    This class provides methods to fetch thermophysical properties from CoolProp's
    database and convert them to the standard CompoundDTO format.

    Attributes:
        coolprop_name: CoolProp fluid identifier (e.g., "Water", "Methane")
    """

    def __init__(self, coolprop_name: str) -> None:
        """Initialize extractor for a specific CoolProp fluid.

        Args:
            coolprop_name: CoolProp fluid name (case-sensitive)

        Raises:
            ValueError: If fluid is not available in CoolProp
        """
        self.coolprop_name = coolprop_name

        # Verify fluid exists in CoolProp
        try:
            CP.PropsSI("M", self.coolprop_name)
        except Exception as e:
            raise ValueError(
                f"Fluid '{coolprop_name}' not found in CoolProp. "
                f"Available fluids: {', '.join(CP.get_global_param_string('fluids_list').split(',')[:10])}..."
            ) from e

    def extract_compound_data(
        self,
        cas_number: str,
        name: str,
        formula: str,
        iupac_name: str,
        aliases: list[str] | None = None,
        nist_url: str | None = None,
    ) -> CompoundDTO:
        """Extract complete compound data from CoolProp.

        Args:
            cas_number: CAS Registry Number (e.g., "7732-18-5")
            name: Common name (e.g., "Water")
            formula: Chemical formula (e.g., "H2O")
            iupac_name: IUPAC systematic name
            aliases: Optional list of alternative names
            nist_url: Optional NIST WebBook reference URL

        Returns:
            CompoundDTO with all extracted properties

        Examples:
            >>> extractor = CoolPropDataExtractor("Water")
            >>> water = extractor.extract_compound_data(
            ...     cas_number="7732-18-5",
            ...     name="Water",
            ...     formula="H2O",
            ...     iupac_name="oxidane",
            ...     aliases=["water", "H2O"],
            ...     nist_url="https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185"
            ... )
            >>> print(water.name)
            Water
        """
        return CompoundDTO(
            cas_number=cas_number,
            name=name,
            formula=formula,
            iupac_name=iupac_name,
            coolprop_name=self.coolprop_name,
            aliases=aliases or [],
            molecular_weight=self.fetch_molecular_weight(),
            critical_properties=self.fetch_critical_properties(),
            phase_properties=self.fetch_phase_properties(),
            source=SourceAttributionDTO(
                name="CoolProp / NIST WebBook",
                url=nist_url or f"https://webbook.nist.gov/cgi/cbook.cgi?ID={cas_number}",
                retrieved_date=date.today(),
                version="CoolProp 7.x",
                notes=f"Properties extracted from CoolProp for fluid: {self.coolprop_name}",
            ),
        )

    def fetch_critical_properties(self) -> CriticalPropertiesDTO:
        """Fetch critical point properties from CoolProp.

        Returns:
            CriticalPropertiesDTO with T_c, P_c, rho_c, and acentric factor

        Raises:
            RuntimeError: If CoolProp query fails
        """
        try:
            t_crit = CP.PropsSI("Tcrit", self.coolprop_name)  # K
            p_crit = CP.PropsSI("pcrit", self.coolprop_name)  # Pa
            rho_crit = CP.PropsSI("rhocrit", self.coolprop_name)  # kg/m³
            acentric = CP.PropsSI("acentric", self.coolprop_name)  # dimensionless
        except Exception as e:
            raise RuntimeError(
                f"Failed to extract critical properties for {self.coolprop_name}: {e}"
            ) from e

        return CriticalPropertiesDTO(
            temperature=QuantityDTO(magnitude=t_crit, unit="kelvin"),
            pressure=QuantityDTO(magnitude=p_crit, unit="pascal"),
            density=QuantityDTO(magnitude=rho_crit, unit="kilogram / meter ** 3"),
            acentric_factor=acentric,
        )

    def fetch_phase_properties(self) -> PhasePropertiesDTO:
        """Fetch phase transition properties from CoolProp.

        Returns:
            PhasePropertiesDTO with normal boiling point and triple point data

        Raises:
            RuntimeError: If CoolProp query fails
        """
        try:
            # Normal boiling point at 1 atm (101325 Pa)
            t_boil = CP.PropsSI("T", "P", 101325, "Q", 0, self.coolprop_name)  # K

            # Triple point properties
            t_triple = CP.PropsSI("Ttriple", self.coolprop_name)  # K
            p_triple = CP.PropsSI("ptriple", self.coolprop_name)  # Pa
        except Exception as e:
            raise RuntimeError(
                f"Failed to extract phase properties for {self.coolprop_name}: {e}"
            ) from e

        return PhasePropertiesDTO(
            normal_boiling_point=QuantityDTO(magnitude=t_boil, unit="kelvin"),
            triple_point_temperature=QuantityDTO(magnitude=t_triple, unit="kelvin"),
            triple_point_pressure=QuantityDTO(magnitude=p_triple, unit="pascal"),
        )

    def fetch_molecular_weight(self) -> QuantityDTO:
        """Fetch molecular weight from CoolProp.

        Returns:
            QuantityDTO with molecular weight in g/mol

        Raises:
            RuntimeError: If CoolProp query fails
        """
        try:
            mw = CP.PropsSI("M", self.coolprop_name)  # kg/mol
            mw_gmol = mw * 1000  # Convert to g/mol
        except Exception as e:
            raise RuntimeError(
                f"Failed to extract molecular weight for {self.coolprop_name}: {e}"
            ) from e

        return QuantityDTO(magnitude=mw_gmol, unit="gram / mole")
