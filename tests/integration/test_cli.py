"""Integration tests for CLI commands."""

import json
import subprocess
import sys
from pathlib import Path


class TestCLIZFactor:
    """Test z-factor command."""

    def test_z_factor_text_output(self) -> None:
        """Test z-factor command with text output."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.pr_calc", "z-factor", "methane", "-T", "300", "-P", "50"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "methane" in result.stdout.lower()
        assert "300.00 K" in result.stdout
        assert "50.00 bar" in result.stdout
        assert "z factor" in result.stdout.lower()

    def test_z_factor_json_output(self) -> None:
        """Test z-factor command with JSON output."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.cli.pr_calc",
                "z-factor",
                "methane",
                "-T",
                "300",
                "-P",
                "50",
                "-f",
                "json",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["compound"] == "methane"
        assert output["temperature"]["value"] == 300.0
        assert output["pressure"]["value"] == 50.0
        assert "z_factor" in output
        assert output["phase"] == "supercritical"

    def test_z_factor_invalid_compound(self) -> None:
        """Test z-factor with invalid compound."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.pr_calc", "z-factor", "invalid", "-T", "300", "-P", "50"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "error" in result.stderr.lower() or "not found" in result.stderr.lower()


class TestCLIFugacity:
    """Test fugacity command."""

    def test_fugacity_text_output(self) -> None:
        """Test fugacity command with text output."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.pr_calc", "fugacity", "ethane", "-T", "350", "-P", "30"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "ethane" in result.stdout.lower()
        assert "fugacity" in result.stdout.lower()

    def test_fugacity_json_output(self) -> None:
        """Test fugacity command with JSON output."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.cli.pr_calc",
                "fugacity",
                "propane",
                "-T",
                "350",
                "-P",
                "30",
                "-f",
                "json",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["compound"] == "propane"
        assert "fugacity_coefficient" in output
        assert "fugacity" in output


class TestCLIVaporPressure:
    """Test vapor-pressure command."""

    def test_vapor_pressure_text_output(self) -> None:
        """Test vapor-pressure command with text output."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.pr_calc", "vapor-pressure", "water", "-T", "373.15"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "water" in result.stdout.lower()
        assert "vapor pressure" in result.stdout.lower()

    def test_vapor_pressure_json_output(self) -> None:
        """Test vapor-pressure command with JSON output."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.cli.pr_calc",
                "vapor-pressure",
                "methane",
                "-T",
                "150",
                "-f",
                "json",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["compound"] == "methane"
        assert "vapor_pressure" in output
        assert "critical_temperature" in output


class TestCLIState:
    """Test state command."""

    def test_state_text_output(self) -> None:
        """Test state command with text output."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.pr_calc", "state", "methane", "-T", "200", "-P", "50"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "methane" in result.stdout.lower()
        assert "properties" in result.stdout.lower()
        assert "z factor" in result.stdout.lower()

    def test_state_json_output(self) -> None:
        """Test state command with JSON output."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.cli.pr_calc",
                "state",
                "water",
                "-T",
                "500",
                "-P",
                "100",
                "-f",
                "json",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["compound"] == "water"
        assert "z_factor" in output
        assert "fugacity_coefficient" in output
        assert "reduced_temperature" in output
        assert "reduced_pressure" in output


class TestCLIListCompounds:
    """Test list-compounds command."""

    def test_list_compounds_text_output(self) -> None:
        """Test list-compounds command with text output."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.pr_calc", "list-compounds"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "methane" in result.stdout.lower()
        assert "ethane" in result.stdout.lower()
        assert "water" in result.stdout.lower()

    def test_list_compounds_json_output(self) -> None:
        """Test list-compounds command with JSON output."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.pr_calc", "list-compounds", "-f", "json"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert "compounds" in output
        assert len(output["compounds"]) >= 5  # At least 5 compounds


class TestCLIValidate:
    """Test validate command."""

    def test_validate_text_output(self) -> None:
        """Test validate command with text output."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.pr_calc", "validate", "methane"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode in [0, 4]  # 0=all pass, 4=some fail
        assert "methane" in result.stdout.lower() or "validation" in result.stdout.lower()

    def test_validate_json_output(self) -> None:
        """Test validate command with JSON output."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.cli.pr_calc",
                "validate",
                "methane",
                "-f",
                "json",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode in [0, 4]
        output = json.loads(result.stdout)
        assert "validation_results" in output
