"""
Database models for QCanvas.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Enum, TIMESTAMP, ForeignKey, Text, Integer, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.config.database import Base
from app.utils.security import SecurityUtils
import enum


class UserRole(str, enum.Enum):
    """User role enumeration."""
    USER = "user"
    ADMIN = "admin"
    DEMO = "demo"  # Demo account - data cleared on logout


class QuantumFramework(str, enum.Enum):
    CIRQ = "cirq"
    QISKIT = "qiskit"
    PENNYLANE = "pennylane"


class SimulationBackend(str, enum.Enum):
    STATEVECTOR = "statevector"
    DENSITY_MATRIX = "density_matrix"
    STABILIZER = "stabilizer"


class ExecutionStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    RUNNING = "running"


class SessionType(str, enum.Enum):
    WEBSOCKET = "websocket"
    API = "api"
    WEB = "web"


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
    
    # Relationships
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")
    conversions = relationship("Conversion", back_populates="user", cascade="all, delete-orphan")
    simulations = relationship("Simulation", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user")
    api_activities = relationship("ApiActivity", back_populates="user")
    files = relationship("File", back_populates="user", cascade="all, delete-orphan")
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # Bcrypt hash
    
    # Profile
    full_name = Column(String(255), nullable=False)
    bio = Column(String(500), nullable=True)
    
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
    folders = relationship("Folder", back_populates="project", cascade="all, delete-orphan")
    files = relationship("File", back_populates="project", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="project")


class Folder(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    parent_id = Column(Integer, ForeignKey("folders.id"), nullable=True, index=True)

    name = Column(String(255), nullable=False)

    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    owner = relationship("User")
    project = relationship("Project", back_populates="folders")
    parent = relationship("Folder", remote_side=[id], backref="children")
    files = relationship("File", back_populates="folder", cascade="all, delete-orphan")


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True) # Nullable for migration, should be filled
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    folder_id = Column(Integer, ForeignKey("folders.id"), nullable=True, index=True)
    filename = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    is_main = Column(Boolean, default=False, nullable=False)
    is_shared = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="files")
    user = relationship("User", back_populates="files")
    folder = relationship("Folder", back_populates="files")


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
    # Relationships
    user = relationship("User", back_populates="jobs")
    project = relationship("Project", back_populates="jobs")


class Conversion(Base):
    __tablename__ = "conversions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    source_framework = Column(Enum(QuantumFramework), nullable=False)
    target_framework = Column(Enum(QuantumFramework), nullable=False)
    source_code = Column(Text, nullable=False)
    target_code = Column(Text, nullable=True)
    qasm_code = Column(Text, nullable=True)
    status = Column(Enum(ExecutionStatus), nullable=False)
    error_message = Column(Text, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="conversions")
    stats = relationship("ConversionStats", back_populates="conversion", uselist=False, cascade="all, delete-orphan")


class ConversionStats(Base):
    __tablename__ = "conversion_stats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversion_id = Column(UUID(as_uuid=True), ForeignKey("conversions.id", ondelete="CASCADE"), unique=True, nullable=False)
    num_qubits = Column(Integer, nullable=False)
    num_gates = Column(Integer, nullable=False)
    circuit_depth = Column(Integer, nullable=False)
    optimization_level = Column(Integer, default=0)

    # Relationships
    conversion = relationship("Conversion", back_populates="stats")


class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    qasm_code = Column(Text, nullable=False)
    backend = Column(Enum(SimulationBackend), nullable=False)
    shots = Column(Integer, nullable=False)
    results_json = Column(JSON, nullable=True)
    status = Column(Enum(ExecutionStatus), nullable=False)
    error_message = Column(Text, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="simulations")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    session_token = Column(String(255), unique=True, nullable=False)
    session_type = Column(Enum(SessionType), nullable=False)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=False)
    expires_at = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="sessions")


class ApiActivity(Base):
    __tablename__ = "api_activity"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=False)
    request_body_hash = Column(String(64), nullable=True)
    response_time_ms = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="api_activities")


class SharedSnippet(Base):
    """
    Model for community shared quantum code snippets.
    These are the projects shared via the Share feature.
    """
    __tablename__ = "shared_snippets"

    id = Column(String(255), primary_key=True)  # The unique share link ID
    
    # Author Info
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    author_name = Column(String(255), nullable=False)
    
    # Snippet Data
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    framework = Column(String(50), nullable=False)
    difficulty = Column(String(50), nullable=False)
    category = Column(String(100), nullable=False)
    tags = Column(String(500), nullable=True)  # Comma-separated list of tags
    code = Column(Text, nullable=False)
    filename = Column(String(255), nullable=False)
    
    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    author = relationship("User", backref="shared_snippets")
