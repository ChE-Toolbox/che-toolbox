"""Unit tests for mixing rules."""

import pytest

from src.eos.mixing_rules import calculate_a_mix, calculate_b_mix, validate_kij_matrix


class TestMixingRules:
    """Test van der Waals mixing rules."""

    def test_calculate_b_mix_binary(self) -> None:
        """Test linear mixing rule for 'b' with binary mixture."""
        b_values = [1.0, 2.0]
        mole_fractions = [0.6, 0.4]
        b_mix = calculate_b_mix(b_values, mole_fractions)
        expected = 0.6 * 1.0 + 0.4 * 2.0
        assert pytest.approx(b_mix, abs=1e-10) == expected

    def test_calculate_b_mix_ternary(self) -> None:
        """Test linear mixing rule for 'b' with ternary mixture."""
        b_values = [1.0, 2.0, 3.0]
        mole_fractions = [0.5, 0.3, 0.2]
        b_mix = calculate_b_mix(b_values, mole_fractions)
        expected = 0.5 * 1.0 + 0.3 * 2.0 + 0.2 * 3.0
        assert pytest.approx(b_mix, abs=1e-10) == expected

    def test_calculate_b_mix_invalid_length(self) -> None:
        """Test that mismatched lengths raise error."""
        with pytest.raises(ValueError, match="Length mismatch"):
            calculate_b_mix([1.0, 2.0], [0.5])

    def test_calculate_b_mix_invalid_sum(self) -> None:
        """Test that mole fractions not summing to 1.0 raise error."""
        with pytest.raises(ValueError, match="sum to"):
            calculate_b_mix([1.0, 2.0], [0.5, 0.4])

    def test_calculate_a_mix_binary(self) -> None:
        """Test geometric mixing rule for 'a' with binary mixture."""

        a_values = [4.0, 9.0]  # sqrt values are 2 and 3
        mole_fractions = [0.6, 0.4]
        kij_matrix = [[0.0, 0.1], [0.1, 0.0]]

        a_mix = calculate_a_mix(a_values, mole_fractions, kij_matrix)

        # Manual calculation:
        # a_11 = 4.0, a_22 = 9.0
        # a_12 = a_21 = (1 - 0.1) * sqrt(4.0 * 9.0) = 0.9 * 6 = 5.4
        # a_mix = x1^2*a_11 + 2*x1*x2*a_12 + x2^2*a_22
        # = 0.36*4 + 2*0.24*5.4 + 0.16*9
        expected = 0.36 * 4.0 + 2 * 0.24 * 5.4 + 0.16 * 9.0
        assert pytest.approx(a_mix, abs=1e-8) == expected

    def test_calculate_a_mix_invalid_dimensions(self) -> None:
        """Test that mismatched dimensions raise error."""
        with pytest.raises(ValueError, match="Length mismatch"):
            calculate_a_mix([1.0, 2.0], [0.5], [[0.0, 0.1], [0.1, 0.0]])

    def test_calculate_a_mix_invalid_kij_matrix_size(self) -> None:
        """Test that invalid kij matrix size raises error."""
        with pytest.raises(ValueError, match="dimension"):
            calculate_a_mix(
                [1.0, 2.0],
                [0.5, 0.5],
                [[0.0, 0.1]],  # Only 1 row, need 2
            )

    def test_calculate_a_mix_invalid_kij_row_size(self) -> None:
        """Test that invalid kij matrix row size raises error."""
        with pytest.raises(ValueError, match="row"):
            calculate_a_mix(
                [1.0, 2.0],
                [0.5, 0.5],
                [[0.0, 0.1, 0.2], [0.1, 0.0, 0.1]],  # First row has 3 elements
            )

    def test_validate_kij_matrix_valid(self) -> None:
        """Test valid kij matrix passes validation."""
        kij_matrix = [
            [0.0, 0.01],
            [0.01, 0.0],
        ]
        # Should not raise
        validate_kij_matrix(kij_matrix, 2)

    def test_validate_kij_matrix_invalid_bounds(self) -> None:
        """Test that kij outside bounds raises error."""
        kij_matrix = [
            [0.0, 0.6],  # 0.6 is outside (-0.5, 0.5)
            [0.6, 0.0],
        ]
        with pytest.raises(ValueError, match="bounds"):
            validate_kij_matrix(kij_matrix, 2)

    def test_validate_kij_matrix_not_symmetric(self) -> None:
        """Test that non-symmetric kij matrix raises error."""
        kij_matrix = [
            [0.0, 0.1],
            [0.15, 0.0],  # Different from kij[0][1]
        ]
        with pytest.raises(ValueError, match="not symmetric"):
            validate_kij_matrix(kij_matrix, 2)

    def test_validate_kij_matrix_invalid_dimension(self) -> None:
        """Test that wrong dimension raises error."""
        kij_matrix = [
            [0.0, 0.1],
            [0.1, 0.0],
        ]
        with pytest.raises(ValueError, match="dimension"):
            validate_kij_matrix(kij_matrix, 3)
