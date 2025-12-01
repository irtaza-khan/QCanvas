# QCanvas Complete Setup Guide

Quick setup guide for running QCanvas with Docker, database, and authentication.

## Prerequisites

- Python 3.9+
- Node.js 18+
- Docker & Docker Compose
- Git

## Windows Quick Start

### 1. Clone and Setup Environment
```bash
git clone https://github.com/your-username/qcanvas.git
cd qcanvas
python -m venv qcanvas_env
.\qcanvas_env\Scripts\activate
pip install -r requirements.txt
```

### 2. Start Docker Services
```bash
docker-compose up -d
docker-compose ps  # Verify services running
```

**Services:**
- PostgreSQL (port 5433)
- Redis (port 6379)
- SonarQube (port 9000)

### 3. Setup Database
```bash
# Set Python path
$env:PYTHONPATH="path\to\QCanvas\backend"

# Run migrations
python -m alembic upgrade head

# Verify database
python backend/verify_database.py
```

### 4. Create Admin User
```bash
python backend/create_user.py
```

Follow prompts:
- Email: admin@qcanvas.dev
- Username: admin
- Password: (your choice)
- Role: Admin

### 5. Start Backend
```bash
$env:PYTHONPATH="path\to\QCanvas\backend"
python backend/start.py
```

Access:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### 6. Start Frontend (New Terminal)
```bash
cd frontend
npm install
npm run dev
```

Access: http://localhost:3000

## Authentication Endpoints

### Register
```bash
POST http://localhost:8000/api/auth/register
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

### Login
```bash
POST http://localhost:8000/api/auth/login
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

### Get Current User
```bash
GET http://localhost:8000/api/auth/me
Headers: {
  "Authorization": "Bearer YOUR_JWT_TOKEN"
}
```

## Database Schema

See `docs/database-schema.md` for complete schema documentation.

**Tables:**
- `users` - User accounts with encrypted passwords
- `alembic_version` - Migration tracking

**Security Features:**
- Bcrypt password hashing
- AES-256 API key encryption
- JWT tokens (30-min expiration)
- Unique email/username constraints

## Common Commands

### Docker
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs postgres
docker-compose logs redis

# Check status
docker-compose ps
```

### Database
```bash
# Create migration
python -m alembic revision --autogenerate -m "description"

# Apply migrations
python -m alembic upgrade head

# Rollback
python -m alembic downgrade -1

# Check current version
python -m alembic current
```

### User Management
```bash
# Create user
python backend/create_user.py

# Verify database
python backend/verify_database.py

# Test authentication
python backend/test_auth.py
```

## Troubleshooting

### Port Already in Use
If port 5432 is in use (local Postgres), Docker uses port 5433.

### Import Errors
Ensure `PYTHONPATH` is set:
```bash
$env:PYTHONPATH="path\to\QCanvas\backend"
```

### Database Connection Failed
1. Check Docker services: `docker-compose ps`
2. Verify credentials in `backend/app/config/settings.py`
3. Ensure port 5433 is accessible

### Migration Errors
```bash
# Reset database (⚠️ deletes all data)
docker-compose down -v
docker-compose up -d
python -m alembic upgrade head
```

## Next Steps

- Read `docs/database-schema.md` for schema details
- Check `backend/test_auth.py` for authentication examples
- Visit `http://localhost:8000/docs` for interactive API docs
- See `Description.md` for complete project overview
