"""Schema validation test suite for SC-005 success criterion.

This module tests that malformed compound data is properly rejected
by the Pydantic validation schema.

Success Criterion SC-005: Schema rejects invalid data (missing fields,
wrong types, out-of-range values).
"""

import pytest
from pydantic import ValidationError as PydanticValidationError

from chemeng_core.compounds.models import (
    CompoundDatabaseDTO,
    CompoundDTO,
    CriticalPropertiesDTO,
    DatabaseMetadataDTO,
    PhasePropertiesDTO,
    QuantityDTO,
    SourceAttributionDTO,
)


class TestQuantityValidation:
    """Test QuantityDTO validation rules."""

    def test_valid_quantity(self):
        """Test that valid quantities are accepted."""
        q = QuantityDTO(magnitude=100.0, unit="kelvin")
        assert q.magnitude == 100.0
        assert q.unit == "kelvin"

    def test_missing_magnitude_rejected(self):
        """Test that missing magnitude is rejected."""
        with pytest.raises(PydanticValidationError):
            QuantityDTO(unit="kelvin")

    def test_missing_unit_rejected(self):
        """Test that missing unit is rejected."""
        with pytest.raises(PydanticValidationError):
            QuantityDTO(magnitude=100.0)

    def test_non_numeric_magnitude_rejected(self):
        """Test that non-numeric magnitude is rejected."""
        with pytest.raises(PydanticValidationError):
            QuantityDTO(magnitude="not a number", unit="kelvin")


class TestCriticalPropertiesValidation:
    """Test CriticalPropertiesDTO validation rules."""

    @pytest.fixture
    def valid_critical_props(self):
        """Fixture for valid critical properties."""
        return {
            "temperature": QuantityDTO(magnitude=647.096, unit="kelvin"),
            "pressure": QuantityDTO(magnitude=22064000, unit="pascal"),
            "density": QuantityDTO(magnitude=322.0, unit="kg/m**3"),
            "acentric_factor": 0.3443,
        }

    def test_valid_critical_properties(self, valid_critical_props):
        """Test that valid critical properties are accepted."""
        props = CriticalPropertiesDTO(**valid_critical_props)
        assert props.temperature.magnitude == 647.096

    def test_missing_temperature_rejected(self, valid_critical_props):
        """Test that missing temperature is rejected."""
        del valid_critical_props["temperature"]
        with pytest.raises(PydanticValidationError):
            CriticalPropertiesDTO(**valid_critical_props)

    def test_missing_acentric_factor_rejected(self, valid_critical_props):
        """Test that missing acentric factor is rejected."""
        del valid_critical_props["acentric_factor"]
        with pytest.raises(PydanticValidationError):
            CriticalPropertiesDTO(**valid_critical_props)


class TestPhasePropertiesValidation:
    """Test PhasePropertiesDTO validation rules."""

    def test_valid_phase_properties(self):
        """Test that valid phase properties are accepted."""
        props = PhasePropertiesDTO(
            normal_boiling_point=QuantityDTO(magnitude=373.124, unit="kelvin"),
            triple_point_temperature=QuantityDTO(magnitude=273.16, unit="kelvin"),
            triple_point_pressure=QuantityDTO(magnitude=611.7, unit="pascal"),
        )
        assert props.normal_boiling_point.magnitude == 373.124

    def test_missing_boiling_point_rejected(self):
        """Test that missing normal boiling point is rejected."""
        with pytest.raises(PydanticValidationError):
            PhasePropertiesDTO(
                triple_point_temperature=QuantityDTO(magnitude=273.16, unit="kelvin")
            )

    def test_optional_triple_point_accepted(self):
        """Test that triple point properties are optional."""
        props = PhasePropertiesDTO(
            normal_boiling_point=QuantityDTO(magnitude=373.124, unit="kelvin")
        )
        assert props.triple_point_temperature is None
        assert props.triple_point_pressure is None


class TestCompoundValidation:
    """Test CompoundDTO validation rules."""

    @pytest.fixture
    def valid_compound_data(self):
        """Fixture for valid compound data."""
        return {
            "cas_number": "7732-18-5",
            "name": "Water",
            "formula": "H2O",
            "iupac_name": "oxidane",
            "coolprop_name": "Water",
            "aliases": ["water", "H2O"],
            "molecular_weight": QuantityDTO(magnitude=18.01527, unit="g/mol"),
            "critical_properties": CriticalPropertiesDTO(
                temperature=QuantityDTO(magnitude=647.096, unit="kelvin"),
                pressure=QuantityDTO(magnitude=22064000, unit="pascal"),
                density=QuantityDTO(magnitude=322.0, unit="kg/m**3"),
                acentric_factor=0.3443,
            ),
            "phase_properties": PhasePropertiesDTO(
                normal_boiling_point=QuantityDTO(magnitude=373.124, unit="kelvin")
            ),
            "source": SourceAttributionDTO(
                name="CoolProp",
                url="https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185",
                retrieved_date="2025-12-29",
            ),
        }

    def test_valid_compound(self, valid_compound_data):
        """Test that valid compound is accepted."""
        compound = CompoundDTO(**valid_compound_data)
        assert compound.name == "Water"
        assert compound.cas_number == "7732-18-5"

    def test_missing_cas_number_rejected(self, valid_compound_data):
        """Test that missing CAS number is rejected."""
        del valid_compound_data["cas_number"]
        with pytest.raises(PydanticValidationError):
            CompoundDTO(**valid_compound_data)

    def test_missing_critical_properties_rejected(self, valid_compound_data):
        """Test that missing critical properties is rejected."""
        del valid_compound_data["critical_properties"]
        with pytest.raises(PydanticValidationError):
            CompoundDTO(**valid_compound_data)

    def test_aliases_default_to_empty_list(self, valid_compound_data):
        """Test that aliases defaults to empty list if not provided."""
        del valid_compound_data["aliases"]
        compound = CompoundDTO(**valid_compound_data)
        assert compound.aliases == []


class TestDatabaseMetadataValidation:
    """Test DatabaseMetadataDTO validation rules."""

    def test_valid_metadata(self):
        """Test that valid metadata is accepted."""
        metadata = DatabaseMetadataDTO(
            version="1.0.0",
            source="CoolProp",
            retrieved_date="2025-12-29",
            attribution="Test attribution",
            compound_count=10,
        )
        assert metadata.version == "1.0.0"
        assert metadata.compound_count == 10

    def test_negative_compound_count_rejected(self):
        """Test that negative compound count is rejected."""
        with pytest.raises(PydanticValidationError):
            DatabaseMetadataDTO(
                version="1.0.0",
                source="CoolProp",
                retrieved_date="2025-12-29",
                attribution="Test",
                compound_count=-1,
            )

    def test_zero_compound_count_rejected(self):
        """Test that zero compound count is rejected."""
        with pytest.raises(PydanticValidationError):
            DatabaseMetadataDTO(
                version="1.0.0",
                source="CoolProp",
                retrieved_date="2025-12-29",
                attribution="Test",
                compound_count=0,
            )


class TestDatabaseValidation:
    """Test CompoundDatabaseDTO validation rules."""

    @pytest.fixture
    def minimal_valid_database(self):
        """Fixture for minimal valid database."""
        metadata = DatabaseMetadataDTO(
            version="1.0.0",
            source="Test",
            retrieved_date="2025-12-29",
            attribution="Test attribution",
            compound_count=1,
        )

        compound = CompoundDTO(
            cas_number="7732-18-5",
            name="Water",
            formula="H2O",
            iupac_name="oxidane",
            coolprop_name="Water",
            molecular_weight=QuantityDTO(magnitude=18.01527, unit="g/mol"),
            critical_properties=CriticalPropertiesDTO(
                temperature=QuantityDTO(magnitude=647.096, unit="kelvin"),
                pressure=QuantityDTO(magnitude=22064000, unit="pascal"),
                density=QuantityDTO(magnitude=322.0, unit="kg/m**3"),
                acentric_factor=0.3443,
            ),
            phase_properties=PhasePropertiesDTO(
                normal_boiling_point=QuantityDTO(magnitude=373.124, unit="kelvin")
            ),
            source=SourceAttributionDTO(
                name="Test",
                url="https://example.com",
                retrieved_date="2025-12-29",
            ),
        )

        return {"metadata": metadata, "compounds": [compound]}

    def test_valid_database(self, minimal_valid_database):
        """Test that valid database is accepted."""
        db = CompoundDatabaseDTO(**minimal_valid_database)
        assert len(db.compounds) == 1
        assert db.metadata.compound_count == 1

    def test_missing_metadata_rejected(self, minimal_valid_database):
        """Test that missing metadata is rejected."""
        del minimal_valid_database["metadata"]
        with pytest.raises(PydanticValidationError):
            CompoundDatabaseDTO(**minimal_valid_database)

    def test_missing_compounds_rejected(self, minimal_valid_database):
        """Test that missing compounds array is rejected."""
        del minimal_valid_database["compounds"]
        with pytest.raises(PydanticValidationError):
            CompoundDatabaseDTO(**minimal_valid_database)

    def test_empty_compounds_list_accepted(self, minimal_valid_database):
        """Test that empty compounds list is accepted by Pydantic (loader validates count)."""
        minimal_valid_database["compounds"] = []
        # Pydantic allows empty list, but loader should reject count mismatch
        db = CompoundDatabaseDTO(**minimal_valid_database)
        assert len(db.compounds) == 0
