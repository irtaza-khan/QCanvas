"""One-shot debug script: provisions a session, then inits the SDK, and reports client state."""
import os, sys
sys.path.insert(0, ".")
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

import fastqsim
import requests

CONTENT_TYPE_JSON = "application/json"
client = None


def _api_base():
    return (os.getenv("FASTQUBIT_ENDPOINT") or "https://fastqubit.dev/api").rstrip("/")


def _headers(extra=None):
    h = {
        "Authorization": f"Bearer {os.getenv('FASTQSIM_API_TOKEN', '')}",
        "X-End-User-Id": os.getenv("FASTQUBIT_USER_ID", ""),
    }
    if extra:
        h.update(extra)
    return h


def provision():
    resp = requests.post(
        f"{_api_base()}/sessions/start",
        headers=_headers({"Content-Type": CONTENT_TYPE_JSON}),
        json={},
        timeout=30,
    )
    body = resp.json()
    print(f"POST /sessions/start  status={resp.status_code}")
    print(f"  already_active={body.get('already_active')}  session_id={body.get('session_id')}")
    print(f"  session_token={body.get('session_token')}")

    tok = body.get("session_token") or None
    if not tok and body.get("already_active"):
        sid = body.get("session_id")
        print(f"Terminating session {sid}...")
        requests.post(
            f"{_api_base()}/sessions/{sid}/terminate",
            headers=_headers(),
            timeout=15,
        )
        resp2 = requests.post(
            f"{_api_base()}/sessions/start",
            headers=_headers({"Content-Type": CONTENT_TYPE_JSON}),
            json={},
            timeout=30,
        )
        body = resp2.json()
        print(f"POST /sessions/start (retry)  status={resp2.status_code}")
        print(f"  session_id={body.get('session_id')}")
        print(f"  session_token={body.get('session_token')}")
        tok = body.get("session_token") or None

    if tok:
        os.environ["FASTQUBIT_SESSION_TOKEN"] = tok
        print(f"os.environ['FASTQUBIT_SESSION_TOKEN'] set to: {tok[:30]}...")
    else:
        print("WARNING: no session_token obtained")
    return tok


def init_sdk():
    global client
    try:
        try:
            fastqsim.reset()
        except Exception as e:
            print(f"fastqsim.reset() raised (ignored): {e}")
        print(f"Calling fastqsim.init() with FASTQUBIT_SESSION_TOKEN={os.getenv('FASTQUBIT_SESSION_TOKEN', 'NOT SET')[:30]}...")
        client = fastqsim.init()
        print(f"fastqsim.init() returned: {repr(client)}")
        return True, None
    except Exception as e:
        client = None
        return False, str(e)


print("=== Step 1: Try direct SDK init ===")
ok, err = init_sdk()
print(f"ok={ok}  err={err}  client={repr(client)}")

if not ok:
    print("\n=== Step 2: Provision session ===")
    tok = provision()
    print(f"\n=== Step 3: Retry SDK init ===")
    ok, err = init_sdk()
    print(f"ok={ok}  err={err}  client is not None: {client is not None}")

print("\n=== Final state ===")
print(f"client = {repr(client)}")
print(f"client is not None = {client is not None}")
