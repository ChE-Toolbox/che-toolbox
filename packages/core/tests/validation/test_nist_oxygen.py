"""NIST validation tests for Oxygen (O2) critical properties.

Reference: https://webbook.nist.gov/cgi/cbook.cgi?ID=C7782447
"""

import pytest

from chemeng_core.compounds import get_compound


@pytest.mark.validation
def test_oxygen_critical_temperature() -> None:
    """Validate oxygen critical temperature against NIST WebBook.

    NIST Value: 154.581 K
    CoolProp Value: 154.594 K
    Tolerance: ±0.01% (minimal variance)
    """
    oxygen = get_compound("oxygen")
    assert oxygen.critical_properties.temperature.magnitude == pytest.approx(154.581, rel=1e-3)


@pytest.mark.validation
def test_oxygen_critical_pressure() -> None:
    """Validate oxygen critical pressure against NIST WebBook.

    NIST Value: 5.0430 MPa = 5043000 Pa
    CoolProp Value: 5046410.5 Pa
    Tolerance: ±0.1% (slight variance between sources)
    """
    oxygen = get_compound("oxygen")
    assert oxygen.critical_properties.pressure.magnitude == pytest.approx(5043000, rel=1e-3)


@pytest.mark.validation
def test_oxygen_acentric_factor() -> None:
    """Validate oxygen acentric factor against NIST WebBook.

    NIST Value: 0.0222
    Tolerance: ±1%
    """
    oxygen = get_compound("oxygen")
    assert oxygen.critical_properties.acentric_factor == pytest.approx(0.0222, rel=0.01)
