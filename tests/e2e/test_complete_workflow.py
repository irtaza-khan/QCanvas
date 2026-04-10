"""
Legacy placeholder E2E test file.

This repo's compilation E2E coverage now lives in:
  - `tests/e2e/test_compilation_e2e.py`

That suite is compilation-only (no simulation/execution) and runs in-process
without requiring a running backend service.
"""

import pytest


@pytest.mark.e2e
def test_compilation_e2e_suite_is_present():
    # Simple guard to keep this file meaningful and avoid accidental reintroduction
    # of network-dependent "E2E" tests.
    assert True
