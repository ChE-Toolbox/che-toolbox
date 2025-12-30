"""NIST validation tests for Carbon Dioxide (CO2) critical properties.

Reference: https://webbook.nist.gov/cgi/cbook.cgi?ID=C124389
"""

import pytest

from chemeng_core.compounds import get_compound


@pytest.mark.validation
def test_co2_critical_temperature() -> None:
    """Validate CO2 critical temperature against NIST WebBook.

    NIST Value: 304.128 K
    Tolerance: ±0.01%
    """
    co2 = get_compound("CO2")
    assert co2.critical_properties.temperature.magnitude == pytest.approx(
        304.128, rel=1e-4
    )


@pytest.mark.validation
def test_co2_critical_pressure() -> None:
    """Validate CO2 critical pressure against NIST WebBook.

    NIST Value: 7.3773 MPa = 7377300 Pa
    Tolerance: ±0.01%
    """
    co2 = get_compound("CO2")
    assert co2.critical_properties.pressure.magnitude == pytest.approx(7377300, rel=1e-4)


@pytest.mark.validation
def test_co2_acentric_factor() -> None:
    """Validate CO2 acentric factor against NIST WebBook.

    NIST Value: 0.22394
    Tolerance: ±1%
    """
    co2 = get_compound("CO2")
    assert co2.critical_properties.acentric_factor == pytest.approx(0.22394, rel=0.01)
