# QCanvas Database Commands Guide

This guide provides a quick reference for all commands related to managing the QCanvas database.

## 1. Environment Setup

Before running any database commands, ensure you are using the correct Python environment (`qasm_env`).

### Windows (PowerShell)
```powershell
.\qasm_env\Scripts\Activate.ps1
```

### Windows (Command Prompt)
```cmd
qasm_env\Scripts\activate.bat
```

## 2. Database Migrations (Alembic)

All Alembic commands should be run from the project root directory (`d:\Study Material\FYP\Practice\Test8\QCanvas`).

### Apply Migrations (Upgrade)
Update the database to the latest schema version.
```bash
python -m alembic upgrade head
```

### Create a New Migration
Generate a new migration script after modifying `database_models.py`.
```bash
python -m alembic revision --autogenerate -m "Description of changes"
```
*Note: If autogenerate fails to detect changes, you may need to create a manual revision:*
```bash
python -m alembic revision -m "Description of changes"
```

### Revert Migrations (Downgrade)
Undo the last migration.
```bash
python -m alembic downgrade -1
```

### View Current Revision
Check the current version of the database.
```bash
python -m alembic current
```

### View History
See the history of migrations.
```bash
python -m alembic history
```

## 3. Verification

### Run Verification Script
Run the included script to verify table creation and basic CRUD operations.
```bash
python -u backend/verify_db.py
```

### Debug Alembic
If migrations are not being detected, run the debug script to check registered tables.
```bash
python -u backend/debug_alembic.py
```

## 4. Troubleshooting

### "ModuleNotFoundError"
If you see errors about missing modules (e.g., `pydantic_settings`), ensure you are running commands using the `qasm_env` Python executable.

You can explicitly use the full path if activation doesn't work:
```bash
"d:\Study Material\FYP\Practice\Test8\QCanvas\qasm_env\Scripts\python.exe" -m alembic upgrade head
```

### "Target database is not up to date"
If `alembic revision` fails, try running `alembic upgrade head` first to ensure your local database is synced with the latest migration scripts.
