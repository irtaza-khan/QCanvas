"""Call /jobs/submit directly (bypassing SDK) to see the real 500 error body."""
import os, json, base64
import requests
from dotenv import load_dotenv

load_dotenv()

API_BASE = os.getenv("FASTQUBIT_ENDPOINT", "https://fastqubit.dev/api").rstrip("/")
SESSION_TOKEN = os.getenv("FASTQUBIT_SESSION_TOKEN", "")

# Decode session_id from the JWT in the pod token
def get_session_id(token):
    payload_enc = token[4:].split(".", 1)[0]
    padding = "=" * (-len(payload_enc) % 4)
    payload = json.loads(base64.urlsafe_b64decode(payload_enc + padding))
    return payload.get("sid", "")

session_id = get_session_id(SESSION_TOKEN) if SESSION_TOKEN else "UNKNOWN"
print(f"Session token present: {bool(SESSION_TOKEN)}")
print(f"Session ID from token: {session_id}")

qasm = """OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
bit[2] c;
h q[0];
cx q[0], q[1];
c = measure q;
"""

headers = {
    "Authorization": f"Bearer {SESSION_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

payload = {
    "session_id": session_id,
    "circuit_qasm": qasm,
    "backend": "qiskit",
    "shots": 512,
    "device": "cpu",
    "simulation_type": "statevector",
    "metadata": {},
    "options": {},
    "tags": {},
}

print(f"\nPOST {API_BASE}/jobs/submit")
print(f"Payload: {json.dumps({k: v for k, v in payload.items() if k != 'circuit_qasm'}, indent=2)}")

r = requests.post(f"{API_BASE}/jobs/submit", headers=headers, json=payload, timeout=30)

print(f"\nStatus: {r.status_code}")
try:
    print("Body:", json.dumps(r.json(), indent=2))
except Exception:
    print("Body (raw):", r.text[:500])
