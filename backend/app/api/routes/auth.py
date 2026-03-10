"""
Authentication endpoints for QCanvas.
Handles user registration, login, and authentication.
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.database_models import User, UserRole
from app.models.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
    ErrorResponse,
    UpdateProfileRequest,
    UpdateProfileResponse,
)
from app.utils.jwt_auth import create_access_token, get_user_id_from_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token
        db: Database session
        
    Returns:
        Current user object
        
    Raises:
        HTTPException: If token is invalid or user not found
   """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    user_id = get_user_id_from_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == user_id, User.deleted_at == None).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or has been deleted",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to get the current authenticated user if token is present.
    Returns None if no token or invalid token.
    """
    if not credentials:
        return None
        
    try:
        token = credentials.credentials
        user_id = get_user_id_from_token(token)
        
        if not user_id:
            return None
        
        user = db.query(User).filter(User.id == user_id, User.deleted_at == None).first()
        if not user or not user.is_active:
            return None
            
        return user
    except Exception:
        return None



@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Email or username already exists"},
        422: {"model": ErrorResponse, "description": "Validation error"}
    }
)
def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user account.
    
    - **email**: Valid email address (must be unique)
    - **username**: Username (must be unique, 3-100 chars)
    - **password**: Password (minimum 8 characters)
    - **full_name**: User's full name
    
    Returns JWT access token and user details.
    """
    # Validate password strength
    if len(request.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == request.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = db.query(User).filter(User.username == request.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    user = User(
        email=request.email,
        username=request.username,
        full_name=request.full_name,
        role=UserRole.USER  # Default role
    )
    user.set_password(request.password)
    
    # Save to database
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    # Prepare user response
    user_response = UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        role=user.role.value,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at.isoformat(),
        last_login_at=None
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"}
    }
)
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Login with email and password.
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns JWT access token and user details.
    """
    # Find user by email
    user = db.query(User).filter(
        User.email == request.email,
        User.deleted_at == None
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not user.verify_password(request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Update last login time
    user.last_login_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    # Prepare user response
    user_response = UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        role=user.role.value,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at.isoformat(),
        last_login_at=user.last_login_at.isoformat() if user.last_login_at else None,
        bio=user.bio
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )


@router.get(
    "/me",
    response_model=UserResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"}
    }
)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's information.
    
    Requires valid JWT token in Authorization header:
    `Authorization: Bearer <token>`
    
    Returns user details without sensitive information.
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role.value,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at.isoformat(),
        last_login_at=current_user.last_login_at.isoformat() if current_user.last_login_at else None,
        bio=current_user.bio
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout():
    """
    Logout endpoint (stateless JWT, so just a placeholder).
    
    In a stateless JWT system, logout is handled on the client side
    by deleting the token. This endpoint exists for API completeness.
    
    For production, consider implementing token blacklisting with Redis.
    """
    return {"message": "Successfully logged out"}


@router.put(
    "/me",
    response_model=UpdateProfileResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Username already taken"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    }
)
def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the current authenticated user's profile.

    Updatable fields:
    - **full_name**: User's display name
    - **username**: Unique username (must not be taken by another user)
    - **bio**: Short bio (stored client-side, echoed back in response)

    Requires valid JWT token in Authorization header.
    """
    # Check username uniqueness if changing it
    if request.username and request.username != current_user.username:
        existing = db.query(User).filter(
            User.username == request.username,
            User.id != current_user.id,
            User.deleted_at == None
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        current_user.username = request.username

    if request.full_name:
        current_user.full_name = request.full_name

    if request.bio is not None:
        current_user.bio = request.bio

    db.commit()
    db.refresh(current_user)

    return UpdateProfileResponse(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role.value,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at.isoformat(),
        last_login_at=current_user.last_login_at.isoformat() if current_user.last_login_at else None,
        bio=current_user.bio,
    )

