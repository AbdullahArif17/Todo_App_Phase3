from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from typing import Generator
from src.database import get_session
from src.models.user import User
from src.core.security import verify_token
from uuid import UUID

security = HTTPBearer()

def get_db_session():
    """
    Dependency to get a database session
    """
    with Session(engine) as session:
        yield session

async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(security),
    db_session: Session = Depends(get_db_session)
) -> User:
    """
    Dependency to get the current authenticated user from the token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = verify_token(token.credentials)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    # Get user from database
    user = db_session.get(User, UUID(user_id))
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user

async def get_current_active_user(
    token: HTTPAuthorizationCredentials = Depends(security),
    db_session: Session = Depends(get_db_session)
) -> User:
    """
    Dependency to get the current authenticated active user from the token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = verify_token(token.credentials)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    # Get user from database
    user = db_session.get(User, UUID(user_id))
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user