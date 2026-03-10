from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.config.database import get_db
from app.models.database_models import User, SharedSnippet
from app.models.schemas import SharedSnippetCreate, SharedSnippetResponse
from app.api.routes.auth import get_optional_user

router = APIRouter(prefix="/api/shared", tags=["Shared"])

@router.post("/", response_model=SharedSnippetResponse, status_code=status.HTTP_201_CREATED)
def create_shared_snippet(
    snippet: SharedSnippetCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Create a new community shared project."""
    
    # Check uniqueness of ID
    existing = db.query(SharedSnippet).filter(SharedSnippet.id == snippet.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="A shared project with this ID already exists")

    # Determine author
    author_id = current_user.id if current_user else None
    
    # Extract Author Name fallback (user's full name, username, or provided string from frontend, or 'Anonymous')
    author_name = "Anonymous User"
    if current_user:
        author_name = current_user.full_name or current_user.username
    elif snippet.author:
        author_name = snippet.author
        
    tags_string = ",".join(snippet.tags) if snippet.tags else ""

    new_snippet = SharedSnippet(
        id=snippet.id,
        title=snippet.title,
        description=snippet.description,
        framework=snippet.framework,
        difficulty=snippet.difficulty,
        category=snippet.category,
        tags=tags_string,
        code=snippet.code,
        filename=snippet.filename,
        author_id=author_id,
        author_name=author_name
    )
    
    db.add(new_snippet)
    db.commit()
    db.refresh(new_snippet)
    
    # Convert string back to list for response
    response_data = new_snippet.__dict__.copy()
    response_data['tags'] = response_data['tags'].split(',') if response_data['tags'] else []
    return response_data


@router.get("/", response_model=List[SharedSnippetResponse])
def get_shared_snippets(db: Session = Depends(get_db)):
    """Retrieve all community shared projects."""
    snippets = db.query(SharedSnippet).order_by(SharedSnippet.created_at.desc()).all()
    
    response = []
    for snippet in snippets:
        data = snippet.__dict__.copy()
        data['tags'] = data['tags'].split(',') if data['tags'] else []
        response.append(data)
        
    return response
