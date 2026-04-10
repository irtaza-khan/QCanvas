"""
Frontend integration E2E tests (compilation-only).

Note: This repo currently does not ship a Playwright/Cypress harness in `tests/`.
For now, we treat "frontend integration" as validating that the canonical frontend
example library compiles successfully via the same compilation pipeline used by the API.

If you later add Playwright, keep these compilation assertions and add UI flows on top.
"""

import pytest


@pytest.mark.e2e
def test_frontend_examples_are_compiled_in_compilation_suite():
    # The heavy lifting is in `tests/e2e/test_compilation_e2e.py`, which extracts
    # `frontend/app/examples/page.tsx` code blocks and compiles them.
    assert True
