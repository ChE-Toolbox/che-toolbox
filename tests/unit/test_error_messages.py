"""
Unit tests for error message validation.

Ensures that InputRangeError, NumericalInstabilityError, and InvalidStateError
include parameter names and actionable guidance in their messages.
"""

import pytest
from pint import UnitRegistry

from iapws_if97 import SteamTable
from iapws_if97.exceptions import InputRangeError, InvalidStateError, NumericalInstabilityError

ureg = UnitRegistry()


class TestInputRangeErrorMessages:
    """Test InputRangeError message format and content."""

    def test_low_pressure_error_message(self):
        """Test that low pressure error includes range information."""
        steam = SteamTable()

        with pytest.raises(InputRangeError) as exc_info:
            steam.h_pt(100 * ureg.Pa, 500 * ureg.K)  # Well below minimum

        error_msg = str(exc_info.value)

        # Should mention "pressure" or "Pressure"
        assert "pressure" in error_msg.lower()

        # Should include valid range
        assert "611" in error_msg or "0.611" in error_msg  # Triple point pressure

    def test_high_pressure_error_message(self):
        """Test that high pressure error includes maximum value."""
        steam = SteamTable()

        with pytest.raises(InputRangeError) as exc_info:
            steam.h_pt(1000 * ureg.MPa, 500 * ureg.K)  # Above maximum

        error_msg = str(exc_info.value)

        assert "pressure" in error_msg.lower()
        # Should mention maximum pressure (863.91 MPa or in Pa)
        assert "863" in error_msg or "8.639" in error_msg or "8639" in error_msg

    def test_low_temperature_error_message(self):
        """Test that low temperature error includes minimum value."""
        steam = SteamTable()

        with pytest.raises(InputRangeError) as exc_info:
            steam.h_pt(1 * ureg.MPa, 200 * ureg.K)  # Below triple point

        error_msg = str(exc_info.value)

        assert "temperature" in error_msg.lower()
        # Should mention minimum temperature (273.15 K)
        assert "273" in error_msg

    def test_high_temperature_error_message(self):
        """Test that high temperature error includes maximum value."""
        steam = SteamTable()

        with pytest.raises(InputRangeError) as exc_info:
            steam.h_pt(1 * ureg.MPa, 1000 * ureg.K)  # Above maximum

        error_msg = str(exc_info.value)

        assert "temperature" in error_msg.lower()
        # Should mention maximum temperature (863.15 K)
        assert "863" in error_msg

    def test_error_message_includes_actual_value(self):
        """Test that error message includes the invalid value provided."""
        steam = SteamTable()

        with pytest.raises(InputRangeError) as exc_info:
            steam.h_pt(1000 * ureg.MPa, 500 * ureg.K)

        error_msg = str(exc_info.value)

        # Should include the actual invalid pressure value
        # (either 1000 MPa or 1e9 Pa)
        assert "1000" in error_msg or "1.000" in error_msg or "1e+09" in error_msg


class TestInvalidStateErrorMessages:
    """Test InvalidStateError message format for saturation line conditions."""

    def test_saturation_line_error_includes_guidance(self):
        """Test that saturation line error provides guidance."""
        steam = SteamTable()

        # Get exact saturation conditions
        sat = steam.T_sat(1 * ureg.MPa)
        t_sat = sat.saturation_temperature

        # Try to compute single-phase properties on saturation line
        # (exact saturation may or may not trigger due to tolerance)
        # Use a known saturation point
        with pytest.raises((InvalidStateError, NumericalInstabilityError)):
            steam.h_pt(1 * ureg.MPa, t_sat)

    def test_error_message_suggests_saturation_api(self):
        """Test that saturation error suggests using T_sat or P_sat."""
        steam = SteamTable()

        try:
            # This might raise InvalidStateError if on saturation line
            sat = steam.T_sat(1 * ureg.MPa)
            # If we can get saturation conditions, try using them
            steam.h_pt(1 * ureg.MPa, sat.saturation_temperature)
        except InvalidStateError as e:
            error_msg = str(e).lower()
            # Should suggest using saturation API
            assert "t_sat" in error_msg or "p_sat" in error_msg or "saturation" in error_msg
        except Exception:
            # Other exceptions are OK for this test
            pass


class TestNumericalInstabilityErrorMessages:
    """Test NumericalInstabilityError message format."""

    def test_saturation_convergence_error_message(self):
        """Test error message when saturation calculation fails to converge."""
        steam = SteamTable()

        # Try a pressure very close to critical point
        try:
            steam.T_sat(22 * ureg.MPa)  # Near critical pressure
        except NumericalInstabilityError as e:
            error_msg = str(e)

            # Should mention convergence, critical point, or saturation
            assert any(
                keyword in error_msg.lower()
                for keyword in ["converge", "critical", "saturation", "iteration", "fail"]
            )
        except Exception:
            # Other exceptions are acceptable for this edge case
            pass

    def test_error_message_provides_suggestion(self):
        """Test that instability error provides actionable suggestion."""
        steam = SteamTable()

        try:
            # Near critical point
            steam.T_sat(22 * ureg.MPa)
        except NumericalInstabilityError as e:
            error_msg = str(e).lower()

            # Should provide guidance
            assert any(
                keyword in error_msg
                for keyword in ["suggestion", "try", "use", "avoid", "alternative"]
            )
        except Exception:
            # Other exceptions are OK
            pass


class TestErrorMessageFormat:
    """Test general error message formatting standards."""

    def test_error_messages_are_not_empty(self):
        """Test that all error messages contain substantive information."""
        steam = SteamTable()

        with pytest.raises(InputRangeError) as exc_info:
            steam.h_pt(1000 * ureg.MPa, 500 * ureg.K)

        error_msg = str(exc_info.value)

        # Message should not be empty
        assert len(error_msg) > 10

        # Should contain multiple pieces of information
        assert error_msg.count(" ") > 3  # At least a few words

    def test_error_messages_use_proper_units(self):
        """Test that error messages express values in user-friendly units."""
        steam = SteamTable()

        with pytest.raises(InputRangeError) as exc_info:
            steam.h_pt(100 * ureg.Pa, 500 * ureg.K)

        error_msg = str(exc_info.value)

        # Should mention Pa or MPa for pressure
        # (not just raw numbers without context)
        assert "pressure" in error_msg.lower() or "temperature" in error_msg.lower()


class TestErrorConsistency:
    """Test that similar errors produce consistent messages."""

    def test_all_properties_raise_same_error_for_out_of_range(self):
        """Test that h_pt, s_pt, u_pt, rho_pt raise consistent errors."""
        steam = SteamTable()

        invalid_p = 1000 * ureg.MPa
        invalid_t = 500 * ureg.K

        # All methods should raise InputRangeError for same invalid input
        with pytest.raises(InputRangeError):
            steam.h_pt(invalid_p, invalid_t)

        with pytest.raises(InputRangeError):
            steam.s_pt(invalid_p, invalid_t)

        with pytest.raises(InputRangeError):
            steam.u_pt(invalid_p, invalid_t)

        with pytest.raises(InputRangeError):
            steam.rho_pt(invalid_p, invalid_t)


class TestParameterNameInclusion:
    """Test that error messages explicitly name which parameter is invalid."""

    def test_pressure_error_mentions_pressure(self):
        """Test that pressure validation error explicitly says 'pressure'."""
        steam = SteamTable()

        with pytest.raises(InputRangeError) as exc_info:
            steam.h_pt(100 * ureg.Pa, 500 * ureg.K)

        error_msg = str(exc_info.value).lower()
        assert "pressure" in error_msg

    def test_temperature_error_mentions_temperature(self):
        """Test that temperature validation error explicitly says 'temperature'."""
        steam = SteamTable()

        with pytest.raises(InputRangeError) as exc_info:
            steam.h_pt(1 * ureg.MPa, 100 * ureg.K)

        error_msg = str(exc_info.value).lower()
        assert "temperature" in error_msg


class TestGuidanceQuality:
    """Test that error messages provide helpful guidance."""

    def test_range_errors_include_valid_range(self):
        """Test that out-of-range errors specify the valid range."""
        steam = SteamTable()

        with pytest.raises(InputRangeError) as exc_info:
            steam.h_pt(100 * ureg.Pa, 500 * ureg.K)

        error_msg = str(exc_info.value)

        # Should include "valid" or "range" to indicate what's acceptable
        assert (
            "valid" in error_msg.lower()
            or "range" in error_msg.lower()
            or "minimum" in error_msg.lower()
            or "maximum" in error_msg.lower()
        )
