"""
Database models for QCanvas.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Enum, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from app.config.database import Base
from app.utils.security import SecurityUtils
import enum


class UserRole(str, enum.Enum):
    """User role enumeration."""
    USER = "user"
    ADMIN = "admin"
    DEMO = "demo"  # Demo account - data cleared on logout


class User(Base):
    """
    User model for authentication and authorization.
    Implements CIA security principles:
    - Confidentiality: Bcrypt password hashing, AES-256 API key encryption
    - Integrity: Timestamps, soft deletes
    - Availability: Indexed columns for fast queries
    """
    __tablename__ = "users"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # Bcrypt hash
    
    # Profile
    full_name = Column(String(255), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Authorization
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    
    # API access (encrypted)
    api_key_encrypted = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(TIMESTAMP, nullable=True)
    
    # Soft delete
    deleted_at = Column(TIMESTAMP, nullable=True, index=True)
    
    def set_password(self, password: str) -> None:
        """
        Hash and set the user's password using bcrypt.
        
        Args:
            password: Plain text password
        """
        self.password_hash = SecurityUtils.hash_password(password)
    
    def verify_password(self, password: str) -> bool:
        """
        Verify a password against the stored hash.
        
        Args:
            password: Plain text password to verify
            
        Returns:
            True if password matches, False otherwise
        """
        return SecurityUtils.verify_password(password, self.password_hash)
    
    def set_api_key(self, api_key: str) -> None:
        """
        Encrypt and set the user's API key using AES-256.
        
        Args:
            api_key: Plain text API key
        """
        self.api_key_encrypted = SecurityUtils.encrypt_api_key(api_key)
    
    def get_api_key(self) -> str | None:
        """
        Decrypt and return the user's API key.
        
        Returns:
            Plain text API key or None if not set
        """
        if self.api_key_encrypted:
            return SecurityUtils.decrypt_api_key(self.api_key_encrypted)
        return None
    
    def generate_and_set_api_key(self) -> str:
        """
        Generate a new API key, encrypt it, and store it.
        
        Returns:
            The generated plain text API key (for one-time display to user)
        """
        api_key = SecurityUtils.generate_api_key()
        self.set_api_key(api_key)
        return api_key
    
    def soft_delete(self) -> None:
        """Soft delete the user account."""
        self.deleted_at = datetime.utcnow()
        self.is_active = False
    
    def restore(self) -> None:
        """Restore a soft-deleted user account."""
        self.deleted_at = None
        self.is_active = True
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role.value})>"
