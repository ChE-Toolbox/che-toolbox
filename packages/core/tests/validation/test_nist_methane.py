"""NIST validation tests for Methane (CH4) critical properties.

Reference: https://webbook.nist.gov/cgi/cbook.cgi?ID=C74828
Data Source: NIST ThermoData Engine (TDE)
"""

import pytest

from chemeng_core.compounds import get_compound


@pytest.mark.validation
def test_methane_critical_temperature() -> None:
    """Validate methane critical temperature against NIST WebBook.

    NIST Value: 190.564 K
    Tolerance: ±0.01%
    """
    methane = get_compound("methane")
    assert methane.critical_properties.temperature.magnitude == pytest.approx(
        190.564, rel=1e-4
    )


@pytest.mark.validation
def test_methane_critical_pressure() -> None:
    """Validate methane critical pressure against NIST WebBook.

    NIST Value: 4.5992 MPa = 4599200 Pa
    Tolerance: ±0.01%
    """
    methane = get_compound("methane")
    assert methane.critical_properties.pressure.magnitude == pytest.approx(
        4599200, rel=1e-4
    )


@pytest.mark.validation
def test_methane_critical_density() -> None:
    """Validate methane critical density against NIST WebBook.

    NIST Value: ~162.7 kg/m³
    Tolerance: ±0.1%
    """
    methane = get_compound("methane")
    assert methane.critical_properties.density.magnitude == pytest.approx(162.7, rel=1e-3)


@pytest.mark.validation
def test_methane_acentric_factor() -> None:
    """Validate methane acentric factor against NIST WebBook.

    NIST Value: 0.01142
    Tolerance: ±1%
    """
    methane = get_compound("methane")
    assert methane.critical_properties.acentric_factor == pytest.approx(0.01142, rel=0.01)


@pytest.mark.validation
def test_methane_normal_boiling_point() -> None:
    """Validate methane normal boiling point against NIST WebBook.

    NIST Value: 111.67 K
    Tolerance: ±0.1%
    """
    methane = get_compound("methane")
    assert methane.phase_properties.normal_boiling_point.magnitude == pytest.approx(
        111.67, rel=1e-3
    )
