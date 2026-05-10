# Test-Pypi-Imports

A temporary demo app that lets you paste Cirq code, compile it with `qcanvas`, and view the generated OpenQASM 3.0.

## Run locally

```powershell
cd "C:\Study Material\FYP\QCanvas-Project\QCanvas\Test-Pypi-Imports"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn backend.app:app --reload
```

Open http://127.0.0.1:8000/ in your browser.

The app imports `qcanvas` from the repository source tree, so you do not need
to install the PyPI package for local testing.
If your global Python environment already has a different `qcanvas` package
installed, always use the virtual environment shown above. That avoids package
conflicts such as `cachetools` version mismatches.

The demo requirements also install `qiskit` and `pennylane`, because the app's
framework selector supports all three frameworks.

The demo uses a modern Qiskit release range (`>=1.1,<3`) so it works cleanly
with newer quantum packages already present in your environment.

## Notes

