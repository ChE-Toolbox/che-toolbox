"""Integration tests for pipe CLI commands."""

import json
import subprocess
import sys
from pathlib import Path


class TestPipeCLI:
    """Test pipe flow CLI commands."""

    def test_reynolds_text_output(self) -> None:
        """Test reynolds command with text output."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "pipe",
                "reynolds",
                "--density",
                "1000",
                "--velocity",
                "2",
                "--diameter",
                "0.05",
                "--viscosity",
                "0.001",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0
        assert "Reynolds" in result.stdout or "Re" in result.stdout
        # Should show flow regime
        assert (
            "laminar" in result.stdout.lower()
            or "turbulent" in result.stdout.lower()
            or "transitional" in result.stdout.lower()
        )

    def test_reynolds_json_output(self) -> None:
        """Test reynolds command with JSON output."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "pipe",
                "reynolds",
                "--density",
                "1000",
                "--velocity",
                "2",
                "--diameter",
                "0.05",
                "--viscosity",
                "0.001",
                "--output-format",
                "json",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert "reynolds_number" in output
        assert "flow_regime" in output
        assert output["reynolds_number"] == 100000  # (1000 * 2 * 0.05) / 0.001

    def test_reynolds_minimal_verbosity(self) -> None:
        """Test reynolds command with minimal verbosity."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "pipe",
                "reynolds",
                "--density",
                "1000",
                "--velocity",
                "2",
                "--diameter",
                "0.05",
                "--viscosity",
                "0.001",
                "--verbosity",
                "minimal",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0
        # Minimal should be a single line with result
        assert len(result.stdout.strip().split("\n")) <= 2

    def test_reynolds_detailed_verbosity(self) -> None:
        """Test reynolds command with detailed verbosity."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "pipe",
                "reynolds",
                "--density",
                "1000",
                "--velocity",
                "2",
                "--diameter",
                "0.05",
                "--viscosity",
                "0.001",
                "--verbosity",
                "detailed",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0
        # Detailed should include more information
        assert len(result.stdout.strip().split("\n")) >= 3

    def test_friction_calculation(self) -> None:
        """Test friction factor command."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "pipe",
                "friction",
                "--reynolds",
                "100000",
                "--roughness",
                "0.000045",
                "--diameter",
                "0.05",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0
        assert "friction" in result.stdout.lower() or "f" in result.stdout

    def test_friction_json_output(self) -> None:
        """Test friction factor command with JSON output."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "pipe",
                "friction",
                "--reynolds",
                "100000",
                "--roughness",
                "0.000045",
                "--diameter",
                "0.05",
                "--output-format",
                "json",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert "friction_factor" in output
        assert output["friction_factor"] > 0

    def test_pressure_drop_calculation(self) -> None:
        """Test pressure drop command."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "pipe",
                "pressure-drop",
                "--friction",
                "0.02",
                "--length",
                "100",
                "--diameter",
                "0.05",
                "--velocity",
                "2",
                "--density",
                "1000",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0
        assert "pressure" in result.stdout.lower() or "ΔP" in result.stdout

    def test_pressure_drop_json_output(self) -> None:
        """Test pressure drop command with JSON output."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "pipe",
                "pressure-drop",
                "--friction",
                "0.02",
                "--length",
                "100",
                "--diameter",
                "0.05",
                "--velocity",
                "2",
                "--density",
                "1000",
                "--output-format",
                "json",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert "pressure_drop" in output
        assert output["pressure_drop"] > 0

    def test_us_unit_system(self) -> None:
        """Test with US customary units."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "pipe",
                "reynolds",
                "--density",
                "62.4",  # lb/ft³
                "--velocity",
                "6.56",  # ft/s
                "--diameter",
                "0.164",  # ft
                "--viscosity",
                "0.000672",  # lb/(ft·s)
                "--unit-system",
                "US",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0

    def test_error_handling_negative_value(self) -> None:
        """Test error handling for invalid inputs."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "pipe",
                "reynolds",
                "--density",
                "-1000",  # Invalid: negative
                "--velocity",
                "2",
                "--diameter",
                "0.05",
                "--viscosity",
                "0.001",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode != 0
        assert "Error" in result.stderr or "error" in result.stderr.lower()

    def test_help_command(self) -> None:
        """Test help output."""
        result = subprocess.run(
            [sys.executable, "-m", "fluids.cli.main", "pipe", "--help"],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0
        assert "reynolds" in result.stdout
        assert "friction" in result.stdout
        assert "pressure-drop" in result.stdout
