# QCanvas Database Management Guide

This guide provides practical steps for managing the QCanvas PostgreSQL database, including daily operations, schema changes, and troubleshooting.

## 🚀 Quick Reference

| Action | Command |
|--------|---------|
| **Start DB** | `docker-compose up -d postgres` |
| **Stop DB** | `docker-compose stop postgres` |
| **View Logs** | `docker-compose logs -f postgres` |
| **Connect (CLI)** | `docker exec -it qcanvas_postgres psql -U postgres -d qcanvas_db` |
| **Apply Migrations** | `python -m alembic upgrade head` |
| **Make Migration** | `python -m alembic revision --autogenerate -m "message"` |

---

## 🐳 Service Management

The database runs in a Docker container named `qcanvas_postgres`.

### Starting the Database
To start the database (and other services like Redis/SonarQube):
```bash
docker-compose up -d
```
*The `-d` flag runs it in the background.*

### Stopping the Database
```bash
docker-compose stop postgres
```

### Resetting the Database
**⚠️ WARNING: This destroys all data!**
To completely wipe the database and start fresh:
```bash
docker-compose down -v
docker-compose up -d
python -m alembic upgrade head
```

---

## 🔄 Schema Management (Alembic)

We use **Alembic** to manage database schema changes. All commands should be run from the project root.

### 1. Create a New Migration
After modifying your SQLAlchemy models in `backend/app/models/`, generate a migration script:
```bash
python -m alembic revision --autogenerate -m "describe_your_change"
```
*   This creates a new file in `backend/alembic/versions/`.
*   **Always review** the generated file to ensure it's correct.

### 2. Apply Migrations
To update the database to the latest schema:
```bash
python -m alembic upgrade head
```

### 3. Rollback Changes
To undo the last migration:
```bash
python -m alembic downgrade -1
```

### 4. View Migration History
To see the history of applied migrations:
```bash
python -m alembic history
```

---

## 💾 Data Management

### Connecting via CLI
You can connect directly to the PostgreSQL shell inside the container:
```bash
docker exec -it qcanvas_postgres psql -U postgres -d qcanvas_db
```
*   **List tables:** `\dt`
*   **Quit:** `\q`

### Connecting via GUI (DBeaver / pgAdmin)
Use these credentials to connect with a GUI tool:
*   **Host:** `localhost`
*   **Port:** `5433` (Note: It's mapped to 5433 locally to avoid conflicts)
*   **Database:** `qcanvas_db`
*   **Username:** `postgres`
*   **Password:** `postgres`

### Backup & Restore

**Backup:**
```bash
docker exec -t qcanvas_postgres pg_dump -U postgres qcanvas_db > backup_$(date +%Y%m%d).sql
```

**Restore:**
```bash
cat backup_file.sql | docker exec -i qcanvas_postgres psql -U postgres -d qcanvas_db
```

---

## 🛠️ Troubleshooting

### "Multiple head revisions" Error
This happens when two branches of migrations exist (e.g., two people created migrations at the same time).
**Fix:**
1.  Identify the heads: `python -m alembic heads`
2.  Merge them: `python -m alembic merge heads -m "merge_branches"`
3.  **OR** (if one is invalid) delete the rogue file and fix the dependency chain manually.

### "Target database is not up to date"
This means your database schema is behind the code.
**Fix:** Run `python -m alembic upgrade head`.

### "Connection Refused"
**Fix:** Ensure the container is running (`docker ps`) and you are using port `5433`.
