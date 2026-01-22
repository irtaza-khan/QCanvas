import requests
import json

def debug_update():
    # 1. Login to get token
    login_resp = requests.post("http://127.0.0.1:8000/api/auth/login", json={
        "email": "demo@qcanvas.dev",
        "password": "demo123"
    })
    
    if not login_resp.ok:
        print("Login failed")
        return

    token = login_resp.json()["access_token"]
    
    # 2. Try PUT update exactly as frontend does
    url = "http://127.0.0.1:8000/api/projects/1/files/1"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "content": "DEBUG_CONTENT_UPDATE"
    }
    
    print(f"Sending PUT to {url}")
    print(f"Headers: {headers}")
    print(f"Body: {json.dumps(data)}")
    
    resp = requests.put(url, json=data, headers=headers)
    
    print(f"Status: {resp.status_code}")
    if resp.status_code == 422:
        print("422 Details:")
        print(json.dumps(resp.json(), indent=2))
    elif resp.status_code == 200:
        print("Success! (Unable to reproduce 422 with script)")
    else:
        print(f"Failed: {resp.text}")

if __name__ == "__main__":
    debug_update()
