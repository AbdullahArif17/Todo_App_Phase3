from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlmodel import Session
from typing import Generator
from ..database.engine import get_session
from ..models.user import User
from ..core.security import verify_token
from uuid import UUID

security = HTTPBearer()

def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency to get a database session
    """
    with get_session() as session:
        yield session

async def get_current_user(
    token: str = Depends(security),
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