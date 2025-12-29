"""Test package version and imports."""

def test_version_exists() -> None:
    """Test that package version is defined."""
    import chemeng_core
    assert hasattr(chemeng_core, "__version__")
    assert isinstance(chemeng_core.__version__, str)
