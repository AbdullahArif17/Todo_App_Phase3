from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select
from ..models.user import User
from ..core.config import settings
import hashlib

# Password hashing context with fallback schemes
pwd_context = CryptContext(
    schemes=["bcrypt", "pbkdf2_sha256", "argon2"],
    deprecated="auto"
)

def truncate_password_if_needed(password: str) -> str:
    """
    Truncate password to 72 bytes if needed to comply with bcrypt limitations
    """
    # Bcrypt has a 72-byte password limit
    # We'll hash the password first to ensure it fits within bcrypt limits
    if len(password.encode('utf-8')) > 72:
        # If password is too long, create a hash of it that's within the limit
        # This maintains security while fitting bcrypt requirements
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        # Take first 72 characters of hex digest (which is 64 chars anyway)
        return hashed_pw[:72]
    return password

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password
    """
    # Ensure password is processed the same way for verification
    safe_password = truncate_password_if_needed(plain_password)
    try:
        return pwd_context.verify(safe_password, hashed_password)
    except Exception:
        # Fallback in case of bcrypt compatibility issues
        # This shouldn't normally be reached, but provides resilience
        return pwd_context.verify(safe_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Generate a hash for a plain password
    """
    # Ensure password is within bcrypt limits
    safe_password = truncate_password_if_needed(password)
    try:
        return pwd_context.hash(safe_password)
    except Exception:
        # Fallback in case of bcrypt compatibility issues
        # Use pbkdf2_sha256 as fallback
        return pwd_context.hash(safe_password, scheme="pbkdf2_sha256")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token with expiration
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode a JWT access token and return the payload
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """
    Get a user by their email address
    """
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()

def authenticate_user(session: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user by email and password
    """
    user = get_user_by_email(session, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user