# Database CRUD Operations Guide

This guide explains how to perform Create, Read, Update, and Delete (CRUD) operations on your new `Project`, `File`, and `Job` tables using SQLAlchemy.

## 📋 Prerequisites

In your API routes (e.g., in `backend/app/api/routes/`), you will typically access the database using the `db` dependency:

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.database_models import Project, File, Job, User

# In your route function:
def my_route(db: Session = Depends(get_db)):
    # ... code here ...
```

---

## 1. Projects

### Create a Project
```python
def create_project(db: Session, user_id: str, name: str, description: str = None):
    new_project = Project(
        user_id=user_id,
        name=name,
        description=description,
        is_public=False
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project
```

### Read Projects (List all for a user)
```python
def get_user_projects(db: Session, user_id: str):
    return db.query(Project).filter(Project.user_id == user_id).all()
```

### Get Single Project
```python
def get_project(db: Session, project_id: int):
    return db.query(Project).filter(Project.id == project_id).first()
```

### Update Project
```python
def update_project(db: Session, project_id: int, new_name: str):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project:
        project.name = new_name
        db.commit()
        db.refresh(project)
    return project
```

### Delete Project
```python
def delete_project(db: Session, project_id: int):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project:
        db.delete(project)
        db.commit()
        return True
    return False
```

---

## 2. Files

### Add File to Project
```python
def add_file(db: Session, project_id: int, filename: str, content: str, is_main: bool = False):
    new_file = File(
        project_id=project_id,
        filename=filename,
        content=content,
        is_main=is_main
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    return new_file
```

### Get Files in Project
```python
def get_project_files(db: Session, project_id: int):
    return db.query(File).filter(File.project_id == project_id).all()
```

---

## 3. Jobs

### Create Job
```python
from app.models.database_models import JobStatus

def create_job(db: Session, user_id: str, project_id: int, backend: str, shots: int):
    new_job = Job(
        user_id=user_id,
        project_id=project_id,
        backend=backend,
        shots=shots,
        status=JobStatus.PENDING
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job
```

### Update Job Status (e.g., after execution)
```python
def update_job_result(db: Session, job_id: int, result_data: dict, execution_time: float):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job:
        job.status = JobStatus.COMPLETED
        job.result_data = result_data
        job.execution_time_ms = execution_time
        db.commit()
    return job
```

---

## 💡 Tips
- **Relationships**: You can access related data easily.
  ```python
  project = db.query(Project).first()
  print(project.files)  # Automatically fetches related files
  print(project.owner.email)  # Automatically fetches the user
  ```
- **Transactions**: `db.commit()` saves changes. If an error occurs, `db.rollback()` is handled automatically by FastAPI's dependency if you raise an exception.
