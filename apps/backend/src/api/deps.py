from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session
from ..database import get_session
from ..models.user import User
from ..core.security import get_current_user

security = HTTPBearer()

async def get_current_active_user(
    session: Session = Depends(get_session),
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> User:
    user = await get_current_user(credentials.credentials, session)
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user