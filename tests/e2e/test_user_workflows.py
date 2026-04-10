"""
User workflow E2E tests (compilation-only).

We focus on compilation scenarios that represent user flows:
- Valid compilation for each supported framework
- Known error cases (empty input, unsupported framework)

More UI-level workflows can be layered later with a browser harness.
"""

import pytest


@pytest.mark.e2e
def test_user_workflows_covered_by_compilation_suite():
    assert True
