# CIA Compliance Manual Verification Guide

This guide explains how to manually verify the Confidentiality, Integrity, and Availability (CIA) security features implemented in the QCanvas backend.

## Prerequisites

1. **Backend Running**: Ensure your backend server is running.
   ```bash
   cd backend
   python app/main.py
   # OR
   uvicorn app.main:app --reload
   ```
2. **Frontend/Browser**: You need a web browser (Chrome/Edge/Firefox) or a tool like `curl`/Postman.

---

## 1. Confidentiality: Security Headers

**Goal**: Verify that the server sends security headers to protect against common attacks (XSS, Clickjacking, etc.).

**Steps**:
1. Open your web browser (e.g., Chrome).
2. Navigate to your API URL (e.g., `http://localhost:8000/docs` or `http://localhost:8000/health`).
3. Right-click anywhere on the page and select **Inspect** to open Developer Tools.
4. Select the **Network** tab.
5. Refresh the page (F5).
6. Click on the first request (e.g., `docs` or `health`) in the Name column.
7. Look at the **Response Headers** section on the right.

**Expected Headers**:
You should see the following headers:
- `X-Frame-Options: DENY` (Prevents clickjacking)
- `X-Content-Type-Options: nosniff` (Prevents MIME sniffing)
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` (Enforces HTTPS - *Note: Effective only over HTTPS, but header should be present*)
- `Content-Security-Policy: default-src 'self'` (Resctricts resource loading)

---

## 2. Integrity: Audit Logging

**Goal**: Verify that every API action is recorded in the database to ensure non-repudiation and traceability.

**Steps**:
1. Perform some actions on the website or via API directly.
   - Example 1: Open `http://localhost:8000/api/frameworks` in your browser.
   - Example 2: Log in (if you have the frontend running).
2. Open your terminal in the `backend` directory.
3. Run the database inspection script to view the Audit Log (`api_activity` table):
   ```bash
   python show_db_data.py api_activity
   ```

**Expected Result**:
You should see a table listing your recent requests, similar to this:

| ID | User ID | Method | Endpoint | Status Code | Response Time (ms) | Created At |
|:---|:---|:---|:---|:---|:---|:---|
| 1  | None    | GET    | /api/frameworks | 200 | 12 | 2025-12-07 10:30:00 |

*Note: `User ID` will be `None` for unauthenticated requests.*

---

## 3. Availability: Rate Limiting

**Goal**: Verify that the system blocks excessive requests to prevent Denial of Service (DoS) attacks.

**Steps**:
1. You can test this using `curl` loop or by rapidly refreshing the browser.
2. **Using Browser**: 
   - Open `http://localhost:8000/api/frameworks`.
   - Hold down `F5` (Refresh) or click the refresh button rapidly (50+ times in a few seconds).
3. **Using Bash/Terminal** (Linux/Mac/Git Bash):
   ```bash
   for i in {1..50}; do curl -I -o /dev/null -s -w "%{http_code}\n" http://localhost:8000/api/frameworks; done
   ```
4. **Using Automated Script**:
   I have created a script that automatically sends a burst of requests to verify the limit.
   ```bash
   python verify_rate_limit.py
   ```
   **Expected Result**:
   - 5 requests should match (Status 200).
   - Remaining requests should be BLOCKED (Status 429).
   - The script will print "🎉 VERIFICATION SUCCESSFUL".
