# QCanvas Database Schema Documentation

> **Version:** 1.0.0  
> **Last Updated:** 2025-12-02  
> **Security:** CIA Principles (Confidentiality, Integrity, Availability)

---

## Overview

This document describes the complete database schema for the QCanvas quantum computing platform. The schema is designed with security-first principles following the CIA triad:

- **Confidentiality:** Encryption and hashing for sensitive data
- **Integrity:** Audit logging and data validation
- **Availability:** Indexing and caching strategies

---

## Entity Relationship Diagram

```
┌─────────────┐
│    users    │
└──────┬──────┘
       │
       ├──────────────┐
       │              │
       ▼              ▼
┌─────────────┐  ┌──────────────┐
│ conversions │  │ simulations  │
└──────┬──────┘  └──────────────┘
       │
       ▼
┌──────────────────┐
│ conversion_stats │
└──────────────────┘

┌──────────────┐
│  sessions    │ (FK to users, nullable)
└──────────────┘

┌──────────────┐
│ api_activity │ (Audit log, FK to users)
└──────────────┘
```

---

## Tables

### 1. `users`

**Purpose:** Store user accounts with secure authentication and authorization.

| Column | Type | Constraints | Description | Security |
|--------|------|-------------|-------------|----------|
| `id` | UUID | PRIMARY KEY | Unique user identifier | - |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | User email address | Indexed |
| `username` | VARCHAR(100) | UNIQUE, NOT NULL | Unique username | Indexed |
| `password_hash` | VARCHAR(255) | NOT NULL | Password stored as bcrypt hash | **BCRYPT HASHED** |
| `full_name` | VARCHAR(255) | NOT NULL | User's display name | - |
| `is_active` | BOOLEAN | DEFAULT TRUE | Account active status | - |
| `is_verified` | BOOLEAN | DEFAULT FALSE | Email verification status | - |
| `role` | ENUM | NOT NULL | User role: 'user', 'admin', 'researcher' | - |
| `api_key_encrypted` | TEXT | NULLABLE | Encrypted API key for programmatic access | **AES-256-GCM ENCRYPTED** |
| `created_at` | TIMESTAMP | NOT NULL | Account creation timestamp | - |
| `updated_at` | TIMESTAMP | NOT NULL | Last update timestamp | Auto-updated |
| `last_login_at` | TIMESTAMP | NULLABLE | Last successful login | - |
| `deleted_at` | TIMESTAMP | NULLABLE | Soft delete timestamp | - |

**Indexes:**
- `idx_users_email` ON `email`
- `idx_users_username` ON `username`
- `idx_users_deleted_at` ON `deleted_at` (for soft delete queries)

---

### 2. `conversions`

**Purpose:** Store quantum circuit conversion history between frameworks.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique conversion identifier |
| `user_id` | UUID | FOREIGN KEY (users.id), NOT NULL | Owner of conversion |
| `source_framework` | ENUM | NOT NULL | Source framework: 'cirq', 'qiskit', 'pennylane' |
| `target_framework` | ENUM | NOT NULL | Target framework: 'cirq', 'qiskit', 'pennylane' |
| `source_code` | TEXT | NOT NULL | Original circuit code |
| `target_code` | TEXT | NULLABLE | Converted circuit code (NULL if failed) |
| `qasm_code` | TEXT | NULLABLE | OpenQASM 3.0 intermediate representation |
| `status` | ENUM | NOT NULL | Conversion status: 'success', 'failed', 'pending' |
| `error_message` | TEXT | NULLABLE | Error details if failed |
| `execution_time_ms` | INTEGER | NULLABLE | Conversion execution time in milliseconds |
| `created_at` | TIMESTAMP | NOT NULL | When conversion was performed |

**Indexes:**
- `idx_conversions_user_id` ON `user_id`
- `idx_conversions_created_at` ON `created_at` (for time-based queries)
- `idx_conversions_status` ON `status`

**Relationships:**
- `user_id` → `users.id` (CASCADE on delete)

---

### 3. `conversion_stats`

**Purpose:** Store detailed metrics and statistics for each conversion.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique stats identifier |
| `conversion_id` | UUID | FOREIGN KEY (conversions.id), UNIQUE, NOT NULL | Associated conversion |
| `num_qubits` | INTEGER | NOT NULL | Number of qubits in circuit |
| `num_gates` | INTEGER | NOT NULL | Total gate count |
| `circuit_depth` | INTEGER | NOT NULL | Maximum circuit depth |
| `optimization_level` | INTEGER | DEFAULT 0 | Optimization level (0-3) |

**Indexes:**
- `idx_conversion_stats_conversion_id` ON `conversion_id`

**Relationships:**
- `conversion_id` → `conversions.id` (CASCADE on delete)

---

### 4. `simulations`

**Purpose:** Store quantum circuit simulation results.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique simulation identifier |
| `user_id` | UUID | FOREIGN KEY (users.id), NOT NULL | Owner of simulation |
| `qasm_code` | TEXT | NOT NULL | OpenQASM 3.0 circuit to simulate |
| `backend` | ENUM | NOT NULL | Simulator backend: 'statevector', 'density_matrix', 'stabilizer' |
| `shots` | INTEGER | NOT NULL | Number of measurement shots |
| `results_json` | JSONB | NULLABLE | Simulation results (counts, probabilities, etc.) |
| `status` | ENUM | NOT NULL | Simulation status: 'success', 'failed', 'running' |
| `error_message` | TEXT | NULLABLE | Error details if failed |
| `execution_time_ms` | INTEGER | NULLABLE | Simulation execution time in milliseconds |
| `created_at` | TIMESTAMP | NOT NULL | When simulation was performed |

**Indexes:**
- `idx_simulations_user_id` ON `user_id`
- `idx_simulations_created_at` ON `created_at`
- `idx_simulations_status` ON `status`

**Relationships:**
- `user_id` → `users.id` (CASCADE on delete)

---

### 5. `sessions`

**Purpose:** Track active user sessions (WebSocket, API, Web).

| Column | Type | Constraints | Description | Security |
|--------|------|-------------|-------------|----------|
| `id` | UUID | PRIMARY KEY | Unique session identifier | - |
| `user_id` | UUID | FOREIGN KEY (users.id), NULLABLE | Associated user (NULL for anonymous) | - |
| `session_token` | VARCHAR(255) | UNIQUE, NOT NULL | Session authentication token | **SHA-256 HASHED** |
| `session_type` | ENUM | NOT NULL | Session type: 'websocket', 'api', 'web' | - |
| `ip_address` | VARCHAR(45) | NOT NULL | Client IP address (IPv4/IPv6) | - |
| `user_agent` | TEXT | NOT NULL | Browser or client user agent | - |
| `expires_at` | TIMESTAMP | NOT NULL | Session expiration timestamp | Indexed |
| `created_at` | TIMESTAMP | NOT NULL | Session creation timestamp | - |

**Indexes:**
- `idx_sessions_user_id` ON `user_id`
- `idx_sessions_expires_at` ON `expires_at` (for cleanup queries)
- `idx_sessions_session_token` ON `session_token`

**Relationships:**
- `user_id` → `users.id` (SET NULL on delete)

---

### 6. `api_activity`

**Purpose:** Comprehensive audit log for security monitoring and analytics.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique activity log identifier |
| `user_id` | UUID | FOREIGN KEY (users.id), NULLABLE | User who made the request (NULL for unauthenticated) |
| `endpoint` | VARCHAR(255) | NOT NULL | API endpoint path |
| `method` | VARCHAR(10) | NOT NULL | HTTP method (GET, POST, PUT, DELETE, etc.) |
| `status_code` | INTEGER | NOT NULL | HTTP response status code |
| `ip_address` | VARCHAR(45) | NOT NULL | Client IP address |
| `user_agent` | TEXT | NOT NULL | Client user agent |
| `request_body_hash` | VARCHAR(64) | NULLABLE | SHA-256 hash of request payload |
| `response_time_ms` | INTEGER | NOT NULL | Request processing time in milliseconds |
| `created_at` | TIMESTAMP | NOT NULL | When the request was made |

**Indexes:**
- `idx_api_activity_user_id` ON `user_id`
- `idx_api_activity_created_at` ON `created_at`
- `idx_api_activity_endpoint` ON `endpoint`
- `idx_api_activity_status_code` ON `status_code`

**Relationships:**
- `user_id` → `users.id` (SET NULL on delete)

---

## Security Implementation

### Confidentiality (Data Privacy)

#### Password Hashing
- **Algorithm:** Bcrypt with automatic salt
- **Rounds:** 12 (configurable)
- **Storage:** `users.password_hash`
- **Implementation:** Python `bcrypt` library

```python
import bcrypt

# Hash password
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))

# Verify password
is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash)
```

#### API Key Encryption
- **Algorithm:** AES-256-GCM (authenticated encryption)
- **Key Derivation:** PBKDF2 from SECRET_KEY
- **Storage:** `users.api_key_encrypted`
- **Implementation:** Python `cryptography` library

```python
from cryptography.fernet import Fernet

# Encrypt API key
cipher = Fernet(encryption_key)
encrypted = cipher.encrypt(api_key.encode('utf-8'))

# Decrypt API key
decrypted = cipher.decrypt(encrypted).decode('utf-8')
```

#### Session Token Hashing
- **Algorithm:** SHA-256
- **Storage:** `sessions.session_token`
- **Token Generation:** Secure random 32-byte token

```python
import hashlib
import secrets

# Generate token
raw_token = secrets.token_urlsafe(32)
token_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
```

---

### Integrity (Data Accuracy)

#### Audit Logging
- All API requests logged to `api_activity`
- Request payloads hashed (SHA-256) for integrity verification
- Immutable log entries (no updates/deletes)

#### Timestamps
- All tables include `created_at`
- Mutable tables include `updated_at` (auto-updated on changes)
- Tracks data lifecycle

#### Soft Deletes
- `users.deleted_at` allows account recovery
- Prevents accidental data loss
- Maintains referential integrity

#### Foreign Key Constraints
- Enforces data relationships
- Prevents orphaned records
- Cascade deletes where appropriate

---

### Availability (Uptime & Performance)

#### Database Indexing
- Indexes on frequently queried columns
- Composite indexes for complex queries
- Regular `ANALYZE` for query optimization

#### Redis Caching
- Cache frequently accessed conversions
- Cache simulation results (with TTL)
- Reduce database load by 70-80%

```python
# Cache conversion result
redis_client.setex(f"conversion:{conversion_id}", 300, json.dumps(result))

# Get from cache
cached = redis_client.get(f"conversion:{conversion_id}")
```

#### Connection Pooling
- SQLAlchemy engine with pooling
- Pool size: 20 connections
- Max overflow: 10 connections
- Prevents connection exhaustion

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)
```

---

## Data Types Reference

### ENUM Types

```sql
-- User roles
CREATE TYPE user_role AS ENUM ('user', 'admin', 'researcher');

-- Quantum frameworks
CREATE TYPE quantum_framework AS ENUM ('cirq', 'qiskit', 'pennylane');

-- Simulation backends
CREATE TYPE simulation_backend AS ENUM ('statevector', 'density_matrix', 'stabilizer');

-- Conversion/Simulation status
CREATE TYPE execution_status AS ENUM ('success', 'failed', 'pending', 'running');

-- Session types
CREATE TYPE session_type AS ENUM ('websocket', 'api', 'web');
```

---

## Migration Strategy

### Alembic Setup

1. **Initialize Alembic:**
   ```bash
   cd backend
   alembic init alembic
   ```

2. **Configure `alembic.ini`:**
   ```ini
   sqlalchemy.url = postgresql://postgres:postgres@127.0.0.1:5433/qcanvas_db
   ```

3. **Create Initial Migration:**
   ```bash
   alembic revision -m "Initial schema"
   ```

4. **Apply Migration:**
   ```bash
   alembic upgrade head
   ```

5. **Rollback (if needed):**
   ```bash
   alembic downgrade -1
   ```

---

## Best Practices

### Data Retention
- **Conversions/Simulations:** Keep for 90 days, then archive
- **API Activity:** Keep for 30 days for security auditing
- **Sessions:** Clean up expired sessions daily

### Backup Strategy
- **Full Backup:** Weekly (Sundays at 00:00 UTC)
- **Incremental Backup:** Daily (00:00 UTC)
- **Retention:** 30 days
- **Storage:** Encrypted backups on separate infrastructure

### Monitoring
- Track slow queries (>100ms)
- Monitor table sizes and index usage
- Alert on failed login attempts (>5 in 1 hour)
- Monitor disk usage (alert at 80%)

---

## Compliance & Privacy

### GDPR Compliance
- Users can request data export (JSON format)
- Users can request account deletion (soft delete with 30-day grace period)
- Personal data minimization (only store what's necessary)

### Data Anonymization
- Before archiving, anonymize IP addresses and user agents
- Hash email addresses for analytics
- Remove PII from old records

---

## Future Enhancements

### Phase 2
- Add `teams` table for collaborative workspaces
- Add `shared_circuits` table for circuit sharing
- Add `webhooks` table for event notifications

### Phase 3
- PostgreSQL read replicas for scaling
- Partitioning for `api_activity` by month
- TimescaleDB for time-series analytics

---

## Appendix

### Dependencies
- PostgreSQL 15+
- Python `bcrypt>=4.0.0`
- Python `cryptography>=42.0.0`
- Python `sqlalchemy>=2.0.0`
- Python `alembic>=1.13.0`
- Python `psycopg2-binary>=2.9.9`

### Configuration
All sensitive configuration should be stored in environment variables:
- `SECRET_KEY`: For encryption key derivation
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string

### Contact
For questions about this schema, contact the QCanvas development team.
