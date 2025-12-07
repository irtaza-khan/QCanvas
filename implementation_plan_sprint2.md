# Implementation Plan - Sprint 2 Completion

This plan covers the remaining tasks for Sprint 2: User Authentication, Database Integration, and Benchmarking.

## 1. Backend Infrastructure (Database & Auth)

We need to replace the mock authentication with a real, secure system using PostgreSQL.

### Dependencies
- [ ] Update `backend/requirements.txt`
    - `psycopg2-binary` (PostgreSQL driver)
    - `passlib[bcrypt]` (Password hashing)
    - `python-jose[cryptography]` (JWT tokens)
    - `python-multipart` (Form data parsing for login)

### Database Setup
- [ ] Create `backend/app/core/database.py`
    - Configure SQLAlchemy `engine` and `SessionLocal`.
    - Implement `get_db` dependency.
- [ ] Create `backend/app/models/user.py`
    - Define `User` model (id, email, hashed_password, full_name, created_at).

### Security Implementation
- [ ] Create `backend/app/core/security.py`
    - `verify_password(plain, hashed)`
    - `get_password_hash(password)`
    - `create_access_token(data, expires_delta)`
- [ ] Create `backend/app/core/config.py` (or update existing)
    - Add `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`.

### API Routes
- [ ] Create `backend/app/api/routes/auth.py`
    - `POST /register`: Create new user.
    - `POST /token` (Login): Validate credentials, return JWT.
    - `GET /users/me`: Get current user profile (protected route).
- [ ] Update `backend/app/main.py`
    - Include `auth_router`.
    - Initialize DB tables on startup (for now, until Alembic is set up).

## 2. Frontend Integration

Connect the Next.js frontend to the new backend auth endpoints.

- [ ] Update `frontend/lib/api.ts`
    - Add `login(email, password)` function calling backend.
    - Add `register(email, password, name)` function.
    - Add `getMe()` function.
- [ ] Update `frontend/app/login/page.tsx`
    - Replace `localStorage` mock logic with real API calls.
    - Store JWT token in `localStorage` or Cookie.

## 3. Evaluation & Benchmarking

Create scripts to measure performance as required by the project scope.

- [ ] Create `scripts/benchmark_converters.py`
    - Measure time taken to convert circuits (Qiskit/Cirq/PennyLane -> QASM).
    - Measure accuracy (round-trip tests).
- [ ] Create `scripts/benchmark_simulation.py`
    - Measure `qsim` execution time for varying qubit counts (4, 8, 12, 16, 20).
    - Compare against baseline (if available) or log metrics.
