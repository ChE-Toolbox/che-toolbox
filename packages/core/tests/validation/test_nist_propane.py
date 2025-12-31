"""NIST validation tests for Propane (C3H8) critical properties.

Reference: https://webbook.nist.gov/cgi/cbook.cgi?ID=C74986
"""

import pytest

from chemeng_core.compounds import get_compound


@pytest.mark.validation
def test_propane_critical_temperature() -> None:
    """Validate propane critical temperature against NIST WebBook.

    NIST Value: 369.89 K
    Tolerance: ±0.01%
    """
    propane = get_compound("propane")
    assert propane.critical_properties.temperature.magnitude == pytest.approx(369.89, rel=1e-4)


@pytest.mark.validation
def test_propane_critical_pressure() -> None:
    """Validate propane critical pressure against NIST WebBook.

    NIST Value: 4.2512 MPa = 4251200 Pa
    Tolerance: ±0.01%
    """
    propane = get_compound("propane")
    assert propane.critical_properties.pressure.magnitude == pytest.approx(4251200, rel=1e-4)


@pytest.mark.validation
def test_propane_acentric_factor() -> None:
    """Validate propane acentric factor against NIST WebBook.

    NIST Value: 0.1521
    Tolerance: ±1%
    """
    propane = get_compound("propane")
    assert propane.critical_properties.acentric_factor == pytest.approx(0.1521, rel=0.01)
