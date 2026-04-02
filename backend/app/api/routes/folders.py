from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.config.database import get_db
from app.models.database_models import User, Project, File, Folder
from app.models.schemas import (
    FolderCreate,
    FolderUpdate,
    FolderResponse,
    ExplorerTreeResponse,
)
from app.api.routes.auth import get_current_user
from sqlalchemy import or_


router = APIRouter(prefix="/api/folders", tags=["Folders"])


def _assert_project_access(project_id: int, db: Session, current_user: User) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != current_user.id and not project.is_public:
        raise HTTPException(status_code=403, detail="Not authorized to view this project")
    return project


def _assert_folder_owner(folder: Folder, current_user: User) -> None:
    if folder.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.post("/", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
def create_folder(
    folder: FolderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Validate project ownership if folder is project-scoped
    if folder.project_id is not None:
        project = db.query(Project).filter(
            Project.id == folder.project_id,
            Project.user_id == current_user.id,
        ).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

    # Validate parent folder (must exist, belong to user, and match project scope)
    if folder.parent_id is not None:
        parent = db.query(Folder).filter(Folder.id == folder.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent folder not found")
        _assert_folder_owner(parent, current_user)
        if parent.project_id != folder.project_id:
            raise HTTPException(status_code=400, detail="Parent folder scope mismatch")

    new_folder = Folder(
        user_id=current_user.id,
        project_id=folder.project_id,
        parent_id=folder.parent_id,
        name=folder.name,
    )
    db.add(new_folder)
    db.commit()
    db.refresh(new_folder)
    return new_folder


@router.get("/", response_model=List[FolderResponse])
def list_folders(
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # If project_id is set, allow owner or public project visibility
    if project_id is not None:
        _assert_project_access(project_id, db, current_user)
        return (
            db.query(Folder)
            .filter(Folder.project_id == project_id)
            .order_by(Folder.parent_id.asc().nullsfirst(), Folder.name.asc())
            .all()
        )

    # Root folders: only the current user's root folders
    return (
        db.query(Folder)
        .filter(Folder.user_id == current_user.id, Folder.project_id == None)
        .order_by(Folder.parent_id.asc().nullsfirst(), Folder.name.asc())
        .all()
    )


@router.get("/tree", response_model=ExplorerTreeResponse)
def get_explorer_tree(
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Explorer tree payload for frontend: returns folders + files for the current scope.

    - If project_id provided: return all folders + files in that project.
      Access allowed for owner or public project.
    - If no project_id: return current user's root folders + root files + shared root files.
    """
    if project_id is not None:
        _assert_project_access(project_id, db, current_user)

        folders = (
            db.query(Folder)
            .filter(Folder.project_id == project_id)
            .order_by(Folder.parent_id.asc().nullsfirst(), Folder.name.asc())
            .all()
        )
        files = (
            db.query(File)
            .filter(File.project_id == project_id)
            .order_by(File.filename.asc())
            .all()
        )
        return {"folders": folders, "files": files}

    # Root
    folders = (
        db.query(Folder)
        .filter(Folder.user_id == current_user.id, Folder.project_id == None)
        .order_by(Folder.parent_id.asc().nullsfirst(), Folder.name.asc())
        .all()
    )
    files = (
        db.query(File)
        .filter(
            or_(
                (File.user_id == current_user.id) & (File.project_id == None),
                (File.is_shared == True) & (File.project_id == None),
            )
        )
        .order_by(File.filename.asc())
        .all()
    )
    return {"folders": folders, "files": files}


@router.put("/{folder_id}", response_model=FolderResponse)
def update_folder(
    folder_id: int,
    folder_update: FolderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    _assert_folder_owner(folder, current_user)

    if folder_update.name is not None:
        folder.name = folder_update.name

    if folder_update.parent_id is not None:
        if folder_update.parent_id == folder.id:
            raise HTTPException(status_code=400, detail="Folder cannot be its own parent")
        parent = db.query(Folder).filter(Folder.id == folder_update.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent folder not found")
        _assert_folder_owner(parent, current_user)
        if parent.project_id != folder.project_id:
            raise HTTPException(status_code=400, detail="Parent folder scope mismatch")
        folder.parent_id = folder_update.parent_id

    db.commit()
    db.refresh(folder)
    return folder


@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    _assert_folder_owner(folder, current_user)

    # Prevent deletion if it still has children or files
    has_children = db.query(Folder).filter(Folder.parent_id == folder_id).first() is not None
    if has_children:
        raise HTTPException(status_code=409, detail="Folder is not empty (has subfolders)")

    has_files = db.query(File).filter(File.folder_id == folder_id).first() is not None
    if has_files:
        raise HTTPException(status_code=409, detail="Folder is not empty (has files)")

    db.delete(folder)
    db.commit()
