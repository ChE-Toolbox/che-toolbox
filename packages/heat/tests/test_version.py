"""Test package version and imports."""

def test_version_exists() -> None:
    """Test that package version is defined."""
    import chemeng_heat
    assert hasattr(chemeng_heat, "__version__")
    assert isinstance(chemeng_heat.__version__, str)
