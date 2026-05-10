from __future__ import annotations

import sys
import traceback
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from qcanvas import compile as qcanvas_compile  # noqa: E402
import qcanvas as qcanvas_module  # noqa: E402

print(f"qcanvas imported from: {getattr(qcanvas_module, '__file__', 'unknown')}")
if REPO_ROOT.as_posix().lower() not in str(getattr(qcanvas_module, '__file__', '')).lower():
    print(
        "Warning: the backend is not importing qcanvas from the repository source tree. "
        "Activate the demo virtual environment and restart Uvicorn."
    )

app = FastAPI(title="Test-Pypi-Imports Demo", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CompileRequest(BaseModel):
    code: str
    framework: str = "cirq"


class CompileResponse(BaseModel):
    ok: bool
    qasm: str | None = None
    error: str | None = None


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    frontend_file = ROOT / "frontend" / "index.html"
    return frontend_file.read_text(encoding="utf-8")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/compile", response_model=CompileResponse)
def compile_code(payload: CompileRequest) -> CompileResponse:
    try:
        qasm = qcanvas_compile(payload.code, framework=payload.framework)
        return CompileResponse(ok=True, qasm=qasm)
    except Exception as exc:
        return CompileResponse(ok=False, error=str(exc))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)
