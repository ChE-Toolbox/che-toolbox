"""Test package version and imports."""


def test_version_exists() -> None:
    """Test that package version is defined."""
    import chemeng_thermo

    assert hasattr(chemeng_thermo, "__version__")
    assert isinstance(chemeng_thermo.__version__, str)
