# Database Implementation Guide: Projects, Files, and Jobs

This guide walks you through implementing the missing database tables (`projects`, `files`, `jobs`) yourself.

## Prerequisites
- Ensure your virtual environment is active (`qasm_env`).
- Ensure the database is running (`docker-compose up -d`).

---

## Step 1: Define the Models

Open `backend/app/models/database_models.py` and add the following code.

### 1.1 Add Imports
Update the imports at the top of the file to include `ForeignKey`, `Text`, `Integer`, `Float`, `JSON` and `relationship`:

```python
from sqlalchemy import Column, String, Boolean, Enum, TIMESTAMP, ForeignKey, Text, Integer, Float, JSON
from sqlalchemy.orm import relationship
```

### 1.2 Update User Model
Add the relationships to the existing `User` class (inside the class definition):

```python
class User(Base):
    # ... existing fields ...
    
    # Add these lines before the methods:
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")
```

### 1.3 Add New Models
Append these classes to the end of the file:

```python
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="projects")
    files = relationship("File", back_populates="project", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="project")


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    is_main = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="files")


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    backend = Column(String(50), nullable=False)
    shots = Column(Integer, default=1024, nullable=False)
    
    execution_time_ms = Column(Float, nullable=True)
    result_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="jobs")
    project = relationship("Project", back_populates="jobs")
```

---

## Step 2: Generate Migration

Run the following command to let Alembic detect your changes and create a migration script:

```bash
python -m alembic revision --autogenerate -m "add_projects_files_jobs"
```

**Verify:** Check `backend/alembic/versions/` for a new file. Open it and ensure it contains `op.create_table('projects'...)`, etc.

---

## Step 3: Apply Migration

Apply the changes to the database:

```bash
python -m alembic upgrade head
```

---

## Step 4: Verify

Check if the tables were created:

```bash
# Connect to DB
docker exec -it qcanvas_postgres psql -U postgres -d qcanvas_db

# List tables
\dt
```

You should see `users`, `projects`, `files`, and `jobs`.
