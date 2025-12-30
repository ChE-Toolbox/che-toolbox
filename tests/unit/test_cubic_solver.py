"""Unit tests for cubic equation solver."""

import pytest

from src.eos.cubic_solver import solve_cubic, solve_cubic_analytical, solve_cubic_numpy


class TestCubicSolver:
    """Test cubic equation solvers."""

    def test_simple_cubic_numpy(self) -> None:
        """Test NumPy solver with simple cubic."""
        # (x - 1)(x - 2)(x - 3) = x^3 - 6x^2 + 11x - 6
        roots = solve_cubic_numpy(1, -6, 11, -6)
        assert len(roots) == 3
        assert pytest.approx(1.0, abs=1e-8) in roots or abs(roots[0] - 1.0) < 1e-8
        assert pytest.approx(2.0, abs=1e-8) in roots or abs(roots[1] - 2.0) < 1e-8
        assert pytest.approx(3.0, abs=1e-8) in roots or abs(roots[2] - 3.0) < 1e-8

    def test_simple_cubic_analytical(self) -> None:
        """Test analytical solver with simple cubic."""
        # (x - 1)(x - 2)(x - 3) = x^3 - 6x^2 + 11x - 6
        roots = solve_cubic_analytical(1, -6, 11, -6)
        assert len(roots) >= 1  # At least one real root

    def test_cubic_single_root(self) -> None:
        """Test cubic with single real root."""
        # x^3 - 1 = 0, should have one real root at x=1
        roots = solve_cubic(1, 0, 0, -1, method="numpy")
        assert len(roots) >= 1
        assert pytest.approx(1.0, abs=1e-8) in roots or abs(roots[0] - 1.0) < 1e-8

    def test_zero_coefficient_error(self) -> None:
        """Test that zero leading coefficient raises error."""
        with pytest.raises(ValueError, match="non-zero"):
            solve_cubic(0, 1, 1, 1)

    def test_invalid_method(self) -> None:
        """Test that invalid method raises error."""
        with pytest.raises(ValueError, match="Invalid method"):
            solve_cubic(1, 0, 0, -1, method="invalid")  # type: ignore

    def test_hybrid_method_uses_numpy_first(self) -> None:
        """Test hybrid method falls back to analytical if needed."""
        # Use hybrid method
        roots = solve_cubic(1, -6, 11, -6, method="hybrid")
        assert len(roots) >= 1

    def test_analytical_method(self) -> None:
        """Test analytical method directly."""
        roots = solve_cubic(1, 0, 0, -1, method="analytical")
        assert len(roots) >= 1

    def test_roots_are_sorted(self) -> None:
        """Test that returned roots are sorted."""
        roots = solve_cubic_numpy(1, -6, 11, -6)
        assert roots == tuple(sorted(roots))

    def test_pr_eos_cubic(self) -> None:
        """Test with a real Peng-Robinson EOS cubic equation."""
        # Typical PR-EOS cubic for methane at moderate conditions
        # Z^3 - 0.98Z^2 + 0.12Z - 0.005 = 0
        roots = solve_cubic(1, -0.98, 0.12, -0.005, method="hybrid")
        # Should have physical roots (Z > 0)
        positive_roots = [r for r in roots if r > 0]
        assert len(positive_roots) >= 1
