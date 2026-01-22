from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from ..utils.security import verify_password, get_password_hash
from .config import settings
from sqlmodel import Session, select
from ..models.user import User

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str, db_session: Session):
    credentials_exception = Exception("Could not validate credentials")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Fetch the user from the database
    statement = select(User).where(User.email == email)
    user = db_session.exec(statement).first()
    if user is None:
        raise credentials_exception
    return user