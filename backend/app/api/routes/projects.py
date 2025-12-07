from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.models.database_models import User, Project, File
from app.models.schemas import ProjectCreate, ProjectResponse, FileCreate, FileResponse
from app.api.routes.auth import get_current_user

router = APIRouter(prefix="/api/projects", tags=["Projects"])

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new project."""
    new_project = Project(
        user_id=current_user.id,
        name=project.name,
        description=project.description,
        is_public=project.is_public
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@router.get("/", response_model=List[ProjectResponse])
def get_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all projects for the current user."""
    return db.query(Project).filter(Project.user_id == current_user.id).all()

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific project by ID."""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/{project_id}/files", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
def add_file_to_project(
    project_id: int,
    file: FileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a file to a project."""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    new_file = File(
        project_id=project.id,
        filename=file.filename,
        content=file.content,
        is_main=file.is_main
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    return new_file
