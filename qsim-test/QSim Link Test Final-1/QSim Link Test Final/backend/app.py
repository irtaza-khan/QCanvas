import json as pyjson
import os
import traceback
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID
from flask import Flask, Response, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import fastqsim
import requests
from fastqsim import (
    FastQSimError, JobFailedError, JobTimeoutError,
    ValidationError, AuthenticationError,
)

from kernel_ws import execute_python_on_kernel

# Load environment variables from .env
load_dotenv()

app = Flask(__name__, static_folder='../frontend')
CORS(app)

CONTENT_TYPE_JSON = "application/json"

# Last-known session fields from FastQubit (ws_url + ws_token for Jupyter kernel WebSocket).
_pod_session: dict = {}


def _sync_pod_session_from_body(body):
    """Merge SessionResponse fields used for kernel /channels WebSocket."""
    global _pod_session
    if not isinstance(body, dict):
        return
    for key in (
        "session_id",
        "ws_url",
        "ws_token",
        "ws_token_expires_at",
        "state",
        "kernel_id",
    ):
        if key in body:
            _pod_session[key] = body[key]


def _api_base():
    return (os.getenv("FASTQUBIT_ENDPOINT") or "https://fastqubit.dev/api").rstrip("/")

def _integrator_headers(extra=None):
    """Headers for calling FastQubit platform APIs (sessions, usage, etc.) using the integrator key."""
    token = os.getenv("FASTQSIM_API_TOKEN") or os.getenv("FASTQUBIT_INTEGRATOR_KEY", "")
    end_user = os.getenv("FASTQUBIT_USER_ID") or os.getenv("FASTQUBIT_END_USER_ID", "")
    headers = {
        "Authorization": f"Bearer {token}",
        "X-End-User-Id": end_user,
    }
    if extra:
        headers.update(extra)
    return headers

def _extract_session_token(body):
    """
    Extract the session_token from a /sessions/start response.
    The docs define it as a plain string field called 'session_token'.
    """
    if not isinstance(body, dict):
        return None
    return body.get("session_token") or None

def _terminate_session(session_id):
    """Terminate an existing session so a fresh one can be started."""
    try:
        requests.post(
            f"{_api_base()}/sessions/{session_id}/terminate",
            headers=_integrator_headers(),
            timeout=15,
        )
    except Exception:
        pass

def _provision_session(payload=None):
    """
    Call POST /sessions/start with the integrator key.
    If a session is already active, terminate it first so we get a fresh session_token.
    On success, store the returned session_token in FASTQUBIT_SESSION_TOKEN
    and return (session_token, full_response_body).
    """
    resp = requests.post(
        f"{_api_base()}/sessions/start",
        headers=_integrator_headers({"Content-Type": CONTENT_TYPE_JSON}),
        json=payload or {},
        timeout=30,
    )
    body = resp.json() if CONTENT_TYPE_JSON in resp.headers.get("content-type", "") else {"raw": resp.text}
    if resp.status_code >= 400:
        _sync_pod_session_from_body(body if isinstance(body, dict) else {})
        return None, body

    # If there's already an active session, session_token will be null.
    # Terminate the old one and start fresh to get a real token.
    if isinstance(body, dict) and body.get("already_active") and not body.get("session_token"):
        existing_id = body.get("session_id")
        if existing_id:
            print(f"Active session {existing_id} found — terminating and restarting...")
            _terminate_session(existing_id)
            resp = requests.post(
                f"{_api_base()}/sessions/start",
                headers=_integrator_headers({"Content-Type": CONTENT_TYPE_JSON}),
                json=payload or {},
                timeout=30,
            )
            body = resp.json() if CONTENT_TYPE_JSON in resp.headers.get("content-type", "") else {"raw": resp.text}
            if resp.status_code >= 400:
                _sync_pod_session_from_body(body if isinstance(body, dict) else {})
                return None, body

    tok = _extract_session_token(body)
    if tok:
        # Set in-process env so child processes (Flask reloader workers) inherit it
        os.environ["FASTQUBIT_SESSION_TOKEN"] = tok
    _sync_pod_session_from_body(body if isinstance(body, dict) else {})
    return tok, body

def _ensure_session_and_init():
    """Provision a session if needed, then (re-)initialize the SDK. Returns (ok, error_str)."""
    existing = os.getenv("FASTQUBIT_SESSION_TOKEN")
    if not existing:
        tok, _ = _provision_session()
        if not tok:
            return False, "Session provisioning failed — no session_token returned"
    return _init_sdk()

client = None  # module-level default so routes never get NameError

def _init_sdk():
    global client
    try:
        try:
            fastqsim.reset()  # safe no-op if no prior client exists
        except Exception:
            pass
        client = fastqsim.init()
        return True, None
    except Exception as e:
        client = None
        return False, str(e)

# Startup: try direct init first (token already in env from a previous provisioning).
# If that fails, provision a new session using the integrator key, then retry.
_ok, _err = _init_sdk()
if _ok:
    print("FastQSim SDK initialized successfully.")
else:
    print(f"SDK direct init failed ({_err}), attempting session provisioning...")
    _tok, _body = _provision_session()
    if _tok:
        _ok, _err = _init_sdk()
        if _ok:
            print("FastQSim SDK initialized successfully after session provisioning.")
        else:
            print(f"Warning: SDK init failed after provisioning: {_err}")
    else:
        print(f"Warning: Session provisioning failed. Response: {_body}")

# --- Frontend Routes ---

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

# --- API Routes ---

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "sdk_initialized": client is not None,
        "user_id": os.getenv("FASTQUBIT_USER_ID")
    })

@app.route('/api/session/start', methods=['POST'])
def session_start():
    """
    Provision a FastQubit session using the integrator key.
    Returns the full upstream response (session_id, ws_token, session_token, etc.)
    and also stores the session_token so the SDK can re-initialize.
    """
    try:
        tok, body = _provision_session(request.json or {})
        if tok:
            _init_sdk()
        return jsonify(body), (200 if tok else 502)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/session/active', methods=['GET'])
def session_active():
    try:
        resp = requests.get(
            f"{_api_base()}/sessions/active",
            headers=_integrator_headers(),
            timeout=30,
        )
        body = resp.json() if CONTENT_TYPE_JSON in resp.headers.get("content-type", "") else {"raw": resp.text}
        return jsonify(body), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _ensure_kernel_ws_credentials():
    """
    Ensure _pod_session has ws_url + ws_token for Jupyter kernel WebSocket.
    Returns (ok, error_message, http_status).
    """
    ar = requests.get(
        f"{_api_base()}/sessions/active",
        headers=_integrator_headers(),
        timeout=30,
    )
    if ar.status_code == 200:
        body = ar.json()
        _sync_pod_session_from_body(body)
    elif ar.status_code == 404:
        _pod_session.clear()
    else:
        return False, ar.text or "GET /sessions/active failed", 502

    if _pod_session.get("ws_url") and _pod_session.get("ws_token"):
        return True, None, 200

    sid = _pod_session.get("session_id")
    if sid:
        rr = requests.post(
            f"{_api_base()}/sessions/{sid}/reconnect-token",
            headers=_integrator_headers({"Content-Type": CONTENT_TYPE_JSON}),
            json={},
            timeout=30,
        )
        rb = rr.json() if CONTENT_TYPE_JSON in rr.headers.get("content-type", "") else {}
        if rr.status_code == 200:
            _sync_pod_session_from_body(rb)

    if _pod_session.get("ws_url") and _pod_session.get("ws_token"):
        return True, None, 200

    tok, body = _provision_session()
    if not tok:
        return False, "Session provisioning failed — cannot obtain kernel WebSocket credentials", 502
    _sync_pod_session_from_body(body if isinstance(body, dict) else {})

    if _pod_session.get("ws_url") and _pod_session.get("ws_token"):
        return True, None, 200

    st = _pod_session.get("state")
    return (
        False,
        f"Kernel channel not ready yet (state={st!r}). Wait until the session pod is ready/active, then retry.",
        503,
    )


@app.route('/api/kernel/status', methods=['GET'])
def kernel_status():
    """Safe subset of session/kernel readiness (no ws_token)."""
    try:
        ar = requests.get(
            f"{_api_base()}/sessions/active",
            headers=_integrator_headers(),
            timeout=30,
        )
        if ar.status_code != 200:
            return jsonify(
                {
                    "active": False,
                    "ready": False,
                    "http_status": ar.status_code,
                }
            )
        body = ar.json()
        _sync_pod_session_from_body(body)
        ready = bool(body.get("ws_url") and body.get("ws_token"))
        if not ready and body.get("session_id"):
            rr = requests.post(
                f"{_api_base()}/sessions/{body['session_id']}/reconnect-token",
                headers=_integrator_headers({"Content-Type": CONTENT_TYPE_JSON}),
                json={},
                timeout=30,
            )
            if rr.status_code == 200:
                rb = rr.json()
                _sync_pod_session_from_body(rb)
                ready = bool(rb.get("ws_url") and rb.get("ws_token"))
                body = rb
        return jsonify(
            {
                "active": True,
                "ready": ready,
                "state": body.get("state"),
                "kernel_id": body.get("kernel_id"),
                "ws_token_expires_at": body.get("ws_token_expires_at"),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e), "ready": False}), 500


@app.route('/api/kernel/execute', methods=['POST'])
def kernel_execute():
    """
    Run Python on the user's Jupyter Kernel Gateway pod via WebSocket (server-side).
    The browser cannot send X-WS-Token on WebSocket; this route proxies that channel.
    """
    data = request.json or {}
    code = (data.get("code") or "").strip()
    if not code:
        return jsonify({"error": "Empty code", "ok": False}), 400
    timeout = float(data.get("timeout", 300))

    try:
        ok, err, status = _ensure_kernel_ws_credentials()
        if not ok:
            return jsonify({"error": err, "ok": False}), status

        out = execute_python_on_kernel(
            _pod_session["ws_url"],
            _pod_session["ws_token"],
            code,
            timeout=timeout,
        )
        safe = _json_safe(out)
        # Use dumps(..., default=str) so nothing in Jupyter payloads can break the HTTP body.
        return Response(
            pyjson.dumps(safe, default=str),
            mimetype="application/json",
        )
    except Exception as e:
        err_body = {"error": str(e), "ok": False}
        if app.debug:
            err_body["traceback"] = traceback.format_exc()
        return Response(
            pyjson.dumps(_json_safe(err_body), default=str),
            mimetype="application/json",
            status=500,
        )


@app.route('/api/debug/submit', methods=['POST'])
def debug_submit():
    """
    Bypass the SDK and call POST /jobs/submit directly so we can see the raw
    server response (including 500 error bodies that the SDK swallows).
    """
    import base64, json as _json
    tok = os.getenv("FASTQUBIT_SESSION_TOKEN", "")
    if not tok:
        return jsonify({"error": "No FASTQUBIT_SESSION_TOKEN in memory"}), 400

    try:
        payload_enc = tok[4:].split(".", 1)[0]
        padding = "=" * (-len(payload_enc) % 4)
        sid = _json.loads(base64.urlsafe_b64decode(payload_enc + padding)).get("sid", "")
    except Exception as e:
        return jsonify({"error": f"Cannot decode token: {e}"}), 400

    qasm = (request.json or {}).get(
        "circuit",
        'OPENQASM 3.0; include "stdgates.inc"; qubit[2] q; bit[2] c; h q[0]; cx q[0],q[1]; c = measure q;'
    )
    payload = {
        "session_id": sid,
        "circuit_qasm": qasm,
        "backend": (request.json or {}).get("backend", "qiskit"),
        "shots": (request.json or {}).get("shots", 512),
        "device": (request.json or {}).get("device", "cpu"),
        "simulation_type": (request.json or {}).get("simulation_type", "statevector"),
        "metadata": {},
        "options": {},
        "tags": {},
    }
    try:
        resp = requests.post(
            f"{_api_base()}/jobs/submit",
            headers={"Authorization": f"Bearer {tok}", "Content-Type": CONTENT_TYPE_JSON, "Accept": CONTENT_TYPE_JSON},
            json=payload,
            timeout=30,
        )
        body = resp.json() if CONTENT_TYPE_JSON in resp.headers.get("content-type", "") else {"raw": resp.text}
        return jsonify({"status_code": resp.status_code, "response": body, "session_id": sid}), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/run', methods=['POST'])
def run_circuit():
    if not client:
        ok, err = _ensure_session_and_init()
        if not ok:
            return jsonify({"error": f"SDK not initialized: {err}"}), 500
    
    data = request.json
    try:
        job = client.run(
            circuit=data.get('circuit'),
            backend=data.get('backend', 'qiskit'),
            device=data.get('device', 'cpu'),
            shots=int(data.get('shots', 1024)),
            simulation_type=data.get('simulation_type'),
            asynchronous=data.get('asynchronous', False),
            job_name=data.get('job_name'),
            seed=data.get('seed'),
            metadata=data.get('metadata'),
            options=data.get('options'),
            tags=data.get('tags'),
        )
        
        # If synchronous, return the result immediately
        if not data.get('asynchronous', False):
            result = job.result()
            return jsonify(serialize_job(job, result))
        
        # If asynchronous, return the job handle
        return jsonify(serialize_job(job))

    except ValidationError as e:
        return jsonify({"error": str(e)}), 422
    except AuthenticationError as e:
        return jsonify({"error": "Authentication failed"}), 401
    except FastQSimError as e:
        return jsonify({"error": str(e)}), 400
    except requests.exceptions.HTTPError as e:
        detail = None
        if hasattr(e, "response") and e.response is not None:
            try:
                detail = e.response.json()
            except Exception:
                detail = e.response.text
        return jsonify({"error": str(e), "detail": detail}), 500
    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500

@app.route('/api/job/<job_id>', methods=['GET'])
def get_job(job_id):
    try:
        job = client.get(job_id)
        return jsonify(serialize_job(job))
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route('/api/wait/<job_id>', methods=['POST'])
def wait_job(job_id):
    timeout = request.json.get('timeout', 300)
    try:
        job = client.wait(job_id, timeout=timeout)
        result = job.result()
        return jsonify(serialize_job(job, result))
    except JobTimeoutError:
        return jsonify({"error": "Job timed out"}), 408
    except JobFailedError as e:
        return jsonify({"error": f"Job failed: {e.reason}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cancel/<job_id>', methods=['DELETE'])
def cancel_job(job_id):
    try:
        job = client.cancel(job_id)
        return jsonify(serialize_job(job))
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/search', methods=['GET'])
def search_jobs():
    try:
        limit = request.args.get('limit', 10, type=int)
        status = request.args.get('status')
        backend = request.args.get('backend')
        
        jobs = client.search(run_status=status, backend=backend, limit=limit)
        return jsonify([serialize_job(j) for j in jobs])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Helpers ---

def _json_safe(obj):
    """Recursively make values JSON-serializable (Jupyter execute_reply, SDK payloads)."""
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, memoryview):
        try:
            return obj.tobytes().decode("utf-8", errors="replace")
        except Exception:
            return str(obj)
    if isinstance(obj, (bytes, bytearray)):
        return bytes(obj).decode("utf-8", errors="replace")
    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, set):
        try:
            return [_json_safe(v) for v in sorted(obj, key=lambda x: str(x))]
        except TypeError:
            return [_json_safe(v) for v in obj]
    if hasattr(obj, "item"):
        try:
            return _json_safe(obj.item())
        except Exception:
            pass
    return str(obj)


def serialize_job(job, result=None):
    """Convert Job and Result objects to JSON-serializable dict"""
    data = {
        "job_id": job.job_id,
        "job_name": job.job_name,
        "status": job.status.value if hasattr(job.status, 'value') else job.status,
        "backend": job.backend,
        "shots": job.shots,
        "simulation_type": job.simulation_type,
        "execution_time_seconds": job.execution_time_seconds,
        "error_message": job.error_message,
        "created_at": job.created_at,
    }

    if result:
        data["counts"] = result.counts
        # Convert complex numbers to strings/lists for JSON
        if result.statevector:
            data["statevector"] = [str(c) for c in result.statevector]

    return _json_safe(data)

if __name__ == '__main__':
    # use_reloader=False keeps a single process so the session token stays in memory.
    # Full debug error pages still work; just restart manually after code changes.
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
