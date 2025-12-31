"""NIST validation tests for Ammonia (NH3) critical properties.

Reference: https://webbook.nist.gov/cgi/cbook.cgi?ID=C7664417
"""

import pytest

from chemeng_core.compounds import get_compound


@pytest.mark.validation
def test_ammonia_critical_temperature() -> None:
    """Validate ammonia critical temperature against NIST WebBook.

    NIST Value: 405.40 K
    CoolProp Value: 405.56 K
    Tolerance: ±0.1% (slight variance between sources)
    """
    ammonia = get_compound("ammonia")
    assert ammonia.critical_properties.temperature.magnitude == pytest.approx(
        405.40, rel=1e-3
    )


@pytest.mark.validation
def test_ammonia_critical_pressure() -> None:
    """Validate ammonia critical pressure against NIST WebBook.

    NIST Value: 11.333 MPa = 11333000 Pa
    CoolProp Value: ~11280000 Pa
    Tolerance: ±0.5% (slight variance between sources)
    """
    ammonia = get_compound("ammonia")
    assert ammonia.critical_properties.pressure.magnitude == pytest.approx(
        11333000, rel=5e-3
    )


@pytest.mark.validation
def test_ammonia_acentric_factor() -> None:
    """Validate ammonia acentric factor against NIST WebBook.

    NIST Value: 0.25601
    Tolerance: ±1%
    """
    ammonia = get_compound("ammonia")
    assert ammonia.critical_properties.acentric_factor == pytest.approx(0.25601, rel=0.01)
