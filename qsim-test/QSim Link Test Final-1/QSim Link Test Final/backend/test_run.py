import requests, json

qasm = """OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
bit[2] c;
h q[0];
cx q[0], q[1];
c = measure q;
"""

payload = {
    "circuit": qasm,
    "backend": "qiskit",
    "shots": 512,
    "asynchronous": False,
}

r = requests.post("http://localhost:5000/api/run", json=payload, timeout=120)
print(f"Status: {r.status_code}")
print(json.dumps(r.json(), indent=2))
