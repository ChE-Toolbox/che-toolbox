"""Test package version and imports."""


def test_version_exists() -> None:
    """Test that package version is defined."""
    import chemeng_fluids

    assert hasattr(chemeng_fluids, "__version__")
    assert isinstance(chemeng_fluids.__version__, str)
