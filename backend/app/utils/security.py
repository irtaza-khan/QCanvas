"""
Security utilities for QCanvas.
Provides password hashing (bcrypt) and API key encryption (AES-256-GCM).
"""
import bcrypt
import secrets
import hashlib
import hmac
from cryptography.fernet import Fernet
from app.config.settings import settings


class SecurityUtils:
    """Security utilities for encryption, hashing, and token generation."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt with automatic salt.
        
        Args:
            password: Plain text password
            
        Returns:
            Bcrypt hashed password (stored as string)
        """
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify a password against a bcrypt hash.
        
        Args:
            password: Plain text password to verify
            hashed_password: Stored bcrypt hash
            
        Returns:
            True if password matches, False otherwise
        """
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    
    @staticmethod
    def _get_encryption_key() -> bytes:
        """
        Derive encryption key from SECRET_KEY using PBKDF2.
        This ensures a consistent 32-byte key for Fernet (AES-256).
        
        Returns:
            32-byte encryption key
        """
        # Use PBKDF2 to derive a key from SECRET_KEY
        key = hashlib.pbkdf2_hmac(
            'sha256',
            settings.SECRET_KEY.encode('utf-8'),
            b'qcanvas_salt',  # Static salt (could be per-user in production)
            100000,  # 100k iterations
            dklen=32
        )
        # Fernet needs base64-encoded key
        from base64 import urlsafe_b64encode
        return urlsafe_b64encode(key)
    
    @staticmethod
    def encrypt_api_key(api_key: str) -> str:
        """
        Encrypt an API key using AES-256-GCM (via Fernet).
        
        Args:
            api_key: Plain text API key
            
        Returns:
            Encrypted API key (base64-encoded)
        """
        cipher = Fernet(SecurityUtils._get_encryption_key())
        encrypted = cipher.encrypt(api_key.encode('utf-8'))
        return encrypted.decode('utf-8')
    
    @staticmethod
    def decrypt_api_key(encrypted_api_key: str) -> str:
        """
        Decrypt an encrypted API key.
        
        Args:
            encrypted_api_key: Encrypted API key
            
        Returns:
            Plain text API key
        """
        cipher = Fernet(SecurityUtils._get_encryption_key())
        decrypted = cipher.decrypt(encrypted_api_key.encode('utf-8'))
        return decrypted.decode('utf-8')
    
    @staticmethod
    def generate_api_key() -> str:
        """
        Generate a secure random API key.
        
        Returns:
            32-byte URL-safe random token
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_session_token() -> str:
        """
        Generate a secure random session token.
        
        Returns:
            32-byte URL-safe random token
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_session_token(token: str) -> str:
        """
        Hash a session token using SHA-256.
        
        Args:
            token: Plain text session token
            
        Returns:
            SHA-256 hash (hex string)
        """
        return hashlib.sha256(token.encode('utf-8')).hexdigest()

    @staticmethod
    def generate_otp_code() -> str:
        """Generate a numeric six-digit OTP code."""
        return f"{secrets.randbelow(1_000_000):06d}"

    @staticmethod
    def generate_salt(length: int = 16) -> str:
        """Generate random hex salt for OTP and reset token hashing."""
        return secrets.token_hex(length)

    @staticmethod
    def hash_otp(code: str, salt: str) -> str:
        """Hash an OTP code using HMAC-SHA256 with salt and server pepper."""
        otp_pepper = settings.OTP_PEPPER or settings.SECRET_KEY
        payload = f"{code}:{salt}".encode("utf-8")
        digest = hmac.new(otp_pepper.encode("utf-8"), payload, hashlib.sha256)
        return digest.hexdigest()

    @staticmethod
    def verify_otp(code: str, salt: str, expected_hash: str) -> bool:
        """Verify OTP with constant-time hash comparison."""
        calculated = SecurityUtils.hash_otp(code, salt)
        return hmac.compare_digest(calculated, expected_hash)

    @staticmethod
    def generate_reset_token() -> str:
        """Generate secure password reset completion token."""
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_reset_token(token: str) -> str:
        """Hash password reset completion token."""
        return hashlib.sha256(token.encode("utf-8")).hexdigest()
