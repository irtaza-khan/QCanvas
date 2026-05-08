"""Minimal smoke test: verify qcanvas imports and version is accessible."""


def test_qcanvas_import():
    """Test that qcanvas package can be imported."""
    import qcanvas

    assert qcanvas is not None


def test_qcanvas_version():
    """Test that qcanvas has a __version__ attribute."""
    import qcanvas

    assert hasattr(qcanvas, "__version__")
    assert isinstance(qcanvas.__version__, str)
    assert len(qcanvas.__version__) > 0


def test_qcanvas_exports():
    """Test that qcanvas exports the expected public API."""
    import qcanvas

    assert hasattr(qcanvas, "compile")
    assert callable(qcanvas.compile)
    assert hasattr(qcanvas, "compile_and_execute")
    assert callable(qcanvas.compile_and_execute)
    assert hasattr(qcanvas, "SimulationResult")
    assert hasattr(qcanvas, "HybridExecutionResult")
