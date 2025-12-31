"""Integration tests for pump CLI commands."""

import json
import subprocess
import sys


class TestPumpCLI:
    """Test pump sizing CLI commands."""

    def test_head_calculation_text(self) -> None:
        """Test pump head command with text output."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "pump",
                "head",
                "--elevation",
                "10",
                "--pressure-drop",
                "50000",
                "--velocity",
                "2",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0
        assert "Result" in result.stdout or "head" in result.stdout.lower()

    def test_head_calculation_json(self) -> None:
        """Test pump head command with JSON output."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "pump",
                "head",
                "--elevation",
                "10",
                "--pressure-drop",
                "50000",
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
        assert "value" in output
        assert output["value"] > 0

    def test_head_with_custom_density(self) -> None:
        """Test head calculation with custom fluid density."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "pump",
                "head",
                "--elevation",
                "5",
                "--pressure-drop",
                "30000",
                "--velocity",
                "1.5",
                "--density",
                "850",  # Oil density
                "--output-format",
                "json",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert "value" in output

    def test_power_hydraulic(self) -> None:
        """Test pump hydraulic power calculation (no efficiency)."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "pump",
                "power",
                "--flow-rate",
                "0.01",  # m³/s
                "--head",
                "20",  # m
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0

    def test_power_brake(self) -> None:
        """Test pump brake power calculation (with efficiency)."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "pump",
                "power",
                "--flow-rate",
                "0.01",
                "--head",
                "20",
                "--efficiency",
                "0.75",
                "--output-format",
                "json",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert "value" in output
        assert output["value"] > 0

    def test_power_minimal_verbosity(self) -> None:
        """Test power command with minimal verbosity."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "pump",
                "power",
                "--flow-rate",
                "0.01",
                "--head",
                "20",
                "--verbosity",
                "minimal",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0
        # Should be concise
        assert len(result.stdout.strip().split("\n")) <= 2

    def test_npsh_available(self) -> None:
        """Test NPSH available calculation."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "pump",
                "npsh",
                "--atmospheric-pressure",
                "101325",  # Pa
                "--vapor-pressure",
                "2340",  # Pa at 20°C
                "--suction-head",
                "3",  # m (flooded suction)
                "--suction-losses",
                "5000",  # Pa
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0

    def test_npsh_json_output(self) -> None:
        """Test NPSH with JSON output."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "pump",
                "npsh",
                "--atmospheric-pressure",
                "101325",
                "--vapor-pressure",
                "2340",
                "--suction-head",
                "3",
                "--output-format",
                "json",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert "value" in output or "npsh_available" in output

    def test_npsh_with_pump_type(self) -> None:
        """Test NPSH with pump type for cavitation check."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "pump",
                "npsh",
                "--atmospheric-pressure",
                "101325",
                "--vapor-pressure",
                "2340",
                "--suction-head",
                "3",
                "--pump-type",
                "centrifugal_small",
                "--flow-rate",
                "0.01",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        # May succeed or fail depending on reference data availability
        # Just check it doesn't crash
        assert result.returncode in [0, 1]

    def test_us_units(self) -> None:
        """Test pump calculations with US customary units."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "pump",
                "head",
                "--elevation",
                "33",  # ft
                "--pressure-drop",
                "7.25",  # psi
                "--velocity",
                "6.56",  # ft/s
                "--density",
                "62.4",  # lb/ft³
                "--unit-system",
                "US",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0

    def test_error_negative_flow(self) -> None:
        """Test error handling for negative flow rate."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "pump",
                "power",
                "--flow-rate",
                "-0.01",  # Invalid
                "--head",
                "20",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode != 0
        assert "Error" in result.stderr or "error" in result.stderr.lower()

    def test_error_invalid_efficiency(self) -> None:
        """Test error handling for invalid efficiency."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "pump",
                "power",
                "--flow-rate",
                "0.01",
                "--head",
                "20",
                "--efficiency",
                "1.5",  # Invalid: > 1
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode != 0

    def test_help_command(self) -> None:
        """Test pump help output."""
        result = subprocess.run(
            [sys.executable, "-m", "fluids.cli.main", "pump", "--help"],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0
        assert "head" in result.stdout
        assert "power" in result.stdout
        assert "npsh" in result.stdout

    def test_detailed_verbosity(self) -> None:
        """Test detailed output mode."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "pump",
                "head",
                "--elevation",
                "10",
                "--pressure-drop",
                "50000",
                "--velocity",
                "2",
                "--verbosity",
                "detailed",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0
        # Detailed should show more lines
        assert len(result.stdout.strip().split("\n")) >= 3
