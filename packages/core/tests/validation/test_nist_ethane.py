"""NIST validation tests for Ethane (C2H6) critical properties.

Reference: https://webbook.nist.gov/cgi/cbook.cgi?ID=C74840
"""

import pytest

from chemeng_core.compounds import get_compound


@pytest.mark.validation
def test_ethane_critical_temperature() -> None:
    """Validate ethane critical temperature against NIST WebBook.

    NIST Value: 305.32 K
    Tolerance: ±0.01%
    """
    ethane = get_compound("ethane")
    assert ethane.critical_properties.temperature.magnitude == pytest.approx(305.32, rel=1e-4)


@pytest.mark.validation
def test_ethane_critical_pressure() -> None:
    """Validate ethane critical pressure against NIST WebBook.

    NIST Value: 4.8722 MPa = 4872200 Pa
    Tolerance: ±0.01%
    """
    ethane = get_compound("ethane")
    assert ethane.critical_properties.pressure.magnitude == pytest.approx(4872200, rel=1e-4)


@pytest.mark.validation
def test_ethane_acentric_factor() -> None:
    """Validate ethane acentric factor against NIST WebBook.

    NIST Value: 0.0995
    Tolerance: ±1%
    """
    ethane = get_compound("ethane")
    assert ethane.critical_properties.acentric_factor == pytest.approx(0.0995, rel=0.01)
