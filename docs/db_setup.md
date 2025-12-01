# QCanvas Database Setup & Security Architecture

This document details the database architecture, security implementation, and management tools for the QCanvas project.

## 🛠️ Technology Stack

- **Database Engine:** PostgreSQL 15 (running via Docker)
- **ORM:** SQLAlchemy 2.0 (Async + Sync support)
- **Migrations:** Alembic
- **Validation:** Pydantic V2
- **Driver:** `psycopg2-binary` (Sync) / `asyncpg` (Async - planned)

## 🔒 Security Architecture (CIA Triad)

We have strictly adhered to the **CIA (Confidentiality, Integrity, Availability)** security model in our database design:

### 1. Confidentiality
*Ensuring sensitive data is accessible only to authorized users.*

- **Password Hashing:** User passwords are **never** stored in plain text. We use **Bcrypt** (via `passlib`) with automatic salting to hash passwords before storage.
- **API Key Encryption:** API keys are encrypted using **AES-256** (Fernet symmetric encryption) before being written to the database. They are only decrypted when needed by the application.
- **Environment Variables:** Database credentials and encryption keys (`SECRET_KEY`) are managed via `.env` files and never hardcoded.

### 2. Integrity
*Ensuring data accuracy and consistency.*

- **Strong Typing:** We use PostgreSQL `ENUM` types for user roles (`USER`, `ADMIN`, `DEMO`) to prevent invalid role assignments.
- **Constraints:**
    - `NOT NULL` constraints on critical fields (email, username, password_hash).
    - `UNIQUE` constraints on `email` and `username` to prevent duplicates.
- **Timestamps:** Automatic `created_at` and `updated_at` timestamps track the lifecycle of every record.
- **Soft Deletes:** The `deleted_at` column allows for "soft deletion," preserving data history and preventing accidental permanent data loss.

### 3. Availability
*Ensuring data is accessible when needed.*

- **Indexing:** We have created B-Tree indexes on frequently queried columns to ensure O(log n) lookup performance:
    - `ix_users_email`: For fast login lookups.
    - `ix_users_username`: For profile lookups.
    - `ix_users_deleted_at`: For filtering active vs. deleted users.
- **Dockerized Infrastructure:** The database runs in a container, ensuring consistent environments across development and production.

## 🗄️ Database Schema: `users` Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK, Not Null | Unique user identifier |
| `email` | VARCHAR(255) | Unique, Not Null, Indexed | User's email address |
| `username` | VARCHAR(100) | Unique, Not Null, Indexed | Public display name |
| `password_hash` | VARCHAR(255) | Not Null | Bcrypt hash of password |
| `full_name` | VARCHAR(255) | Not Null | User's real name |
| `role` | ENUM | Not Null | `USER`, `ADMIN`, or `DEMO` |
| `is_active` | BOOLEAN | Default True | Account status |
| `is_verified` | BOOLEAN | Default False | Email verification status |
| `api_key_encrypted`| VARCHAR(255) | Nullable | AES-256 encrypted API key |
| `created_at` | TIMESTAMP | Default Now | Creation time |
| `updated_at` | TIMESTAMP | Default Now | Last update time |
| `deleted_at` | TIMESTAMP | Nullable, Indexed | Soft delete timestamp |

## 🚀 Setup & Management

### 1. Prerequisites
Ensure Docker is running and the `.env` file is configured with `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`.

### 2. Start Database
```bash
# Start PostgreSQL container
docker-compose up -d db
```

### 3. Apply Migrations
We use Alembic to manage schema changes.
```bash
# Apply all pending migrations
python -m alembic upgrade head
```

### 4. User Management Scripts
We have created utility scripts in the `backend/` directory for common tasks:

- **Create Regular User:**
  ```bash
  python backend/create_user.py
  ```
  *Interactive script to create a new user with password hashing.*

- **Create Demo Account:**
  ```bash
  python backend/create_demo_account.py
  ```
  *Creates the special `demo@qcanvas.dev` account.*

- **Verify Database:**
  ```bash
  python backend/verify_database.py
  ```
  *Checks connection and table existence.*

## ⚠️ Troubleshooting

### Enum Mismatch Error
**Error:** `LookupError: 'demo' is not among the defined enum values`
**Cause:** Mismatch between Python Enum definition (uppercase `DEMO`) and Database Enum value (lowercase `demo`).
**Fix:**
1. Ensure Python `UserRole` class uses uppercase keys.
2. Ensure Database Enum type includes uppercase values.
3. If mismatch occurs, manually add the value to the database type:
   ```sql
   ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'DEMO';
   ```

### Connection Refused
**Cause:** Database container not running or port conflict.
**Fix:**
1. Check container status: `docker ps`
2. Check port mapping (default 5432 or 5433).
3. Restart container: `docker-compose restart db`
