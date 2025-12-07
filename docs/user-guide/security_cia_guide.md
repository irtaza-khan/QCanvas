# CIA Security Implementation Guide

This guide explains how to implement the **CIA Triad** (Confidentiality, Integrity, Availability) for your QCanvas database, specifically focusing on the new `Project`, `File`, and `Job` entities.

---

## 1. Confidentiality
*Ensuring data is accessible ONLY to authorized users.*

### 1.1 Ownership Verification (Application Level)
Since `projects` and `jobs` belong to specific users, you **MUST** verify ownership before every access.

**Implementation Pattern:**
```python
def get_project_secure(db: Session, project_id: int, current_user_id: UUID):
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # CRITICAL: Check if the requester is the owner
    if project.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
        
    return project
```

### 1.2 Data Minimization
Do not return sensitive internal fields (like `hashed_password` or raw `result_data` if it's large/sensitive) unless necessary. Use Pydantic schemas (`response_model`) to filter output.

---

## 2. Integrity
*Ensuring data accuracy, consistency, and trustworthiness.*

### 2.1 Foreign Key Constraints (Database Level)
We enforce relationships at the database level to prevent "orphaned" records.
- `Project.user_id` -> `users.id`
- `File.project_id` -> `projects.id`

**Why?** If a User is deleted, we don't want ghost Projects left behind.
**Implementation:** The `ForeignKey` in your models handles this.

### 2.2 Cascading Deletes
When a parent is deleted, children should be deleted automatically to maintain state consistency.

**Implementation (in `database_models.py`):**
```python
# In User model:
projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")

# In Project model:
files = relationship("File", back_populates="project", cascade="all, delete-orphan")
```
*This ensures that deleting a User deletes their Projects, and deleting a Project deletes its Files.*

### 2.3 Transactions
Use database transactions to ensure that multi-step operations either **fully succeed** or **fully fail**.

**Example:** Creating a Project AND its initial main File.
```python
def create_project_with_file(db: Session, ...):
    try:
        # 1. Create Project
        project = Project(...)
        db.add(project)
        db.flush() # Get ID without committing yet
        
        # 2. Create File
        file = File(project_id=project.id, ...)
        db.add(file)
        
        # 3. Commit both together
        db.commit() 
    except Exception:
        db.rollback() # If file creation fails, project is also undone
        raise
```

---

## 3. Availability
*Ensuring data is accessible when needed.*

### 3.1 Indexing
Indexes speed up data retrieval. You should index columns that are frequently used in `WHERE` clauses.

**Implementation (in `database_models.py`):**
```python
# In Project model:
id = Column(Integer, primary_key=True, index=True) # Fast lookup by ID
user_id = Column(UUID, ForeignKey("users.id"), index=True) # Fast lookup of "all projects for user X"
```
*Note: We added `index=True` to `user_id` implicitly or explicitly to speed up dashboard queries.*

### 3.2 Connection Pooling
Your application uses SQLAlchemy's connection pool (configured in `database.py`). This maintains a set of open connections to avoid the overhead of opening/closing a connection for every request.

### 3.3 Soft Deletes (Optional but Recommended)
Instead of permanently deleting data (which hurts availability if done by mistake), use a `deleted_at` timestamp.

**Implementation:**
Add `deleted_at` to your `Project` model and filter by `deleted_at is None` in your queries.
