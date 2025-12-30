"""NIST validation tests for Water (H2O) critical properties.

These tests validate that compound data matches authoritative NIST WebBook values
within acceptable tolerance ranges. Per Constitution Principle III, these tests
ensure all data is validated against literature sources.

Reference: https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185
Data Source: IAPWS-IF97 (International Association for the Properties of Water and Steam)
"""

import pytest

from chemeng_core.compounds import get_compound


@pytest.mark.validation
def test_water_critical_temperature() -> None:
    """Validate water critical temperature against NIST WebBook.

    NIST Value: 647.096 K
    Tolerance: ±0.01% (±0.06 K)
    Source: IAPWS-IF97
    """
    water = get_compound("water")
    assert water.critical_properties.temperature.unit in ("kelvin", "K")
    assert water.critical_properties.temperature.magnitude == pytest.approx(
        647.096, rel=1e-4
    )


@pytest.mark.validation
def test_water_critical_pressure() -> None:
    """Validate water critical pressure against NIST WebBook.

    NIST Value: 22.064 MPa = 22064000 Pa
    Tolerance: ±0.01% (±2206 Pa)
    Source: IAPWS-IF97
    """
    water = get_compound("water")
    assert water.critical_properties.pressure.unit in ("pascal", "Pa")
    assert water.critical_properties.pressure.magnitude == pytest.approx(
        22064000, rel=1e-4
    )


@pytest.mark.validation
def test_water_critical_density() -> None:
    """Validate water critical density against NIST WebBook.

    NIST Value: 322.0 kg/m³
    Tolerance: ±0.1% (±0.32 kg/m³)
    Source: IAPWS-IF97
    """
    water = get_compound("water")
    assert "kilogram" in water.critical_properties.density.unit
    assert "meter" in water.critical_properties.density.unit
    assert water.critical_properties.density.magnitude == pytest.approx(322.0, rel=1e-3)


@pytest.mark.validation
def test_water_acentric_factor() -> None:
    """Validate water acentric factor against NIST WebBook.

    NIST Value: 0.3443
    Tolerance: ±1% (±0.003443)
    Source: DIPPR correlation
    """
    water = get_compound("water")
    assert water.critical_properties.acentric_factor == pytest.approx(0.3443, rel=0.01)


@pytest.mark.validation
def test_water_normal_boiling_point() -> None:
    """Validate water normal boiling point against NIST WebBook.

    NIST Value: 373.124 K (99.974°C at 1 atm)
    Tolerance: ±0.1% (±0.37 K)
    Source: IAPWS-IF97
    """
    water = get_compound("water")
    assert water.phase_properties.normal_boiling_point.unit in ("kelvin", "K")
    assert water.phase_properties.normal_boiling_point.magnitude == pytest.approx(
        373.124, rel=1e-3
    )


@pytest.mark.validation
def test_water_molecular_weight() -> None:
    """Validate water molecular weight.

    Standard Value: 18.01528 g/mol
    Tolerance: ±0.001% (exact from atomic masses)
    """
    water = get_compound("water")
    assert "gram" in water.molecular_weight.unit
    assert "mol" in water.molecular_weight.unit
    assert water.molecular_weight.magnitude == pytest.approx(18.01528, rel=1e-5)
