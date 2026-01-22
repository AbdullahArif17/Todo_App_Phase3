from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Dict
from ...database import get_session
from ...models.user import User
from ...schemas.user import UserCreate
from ...services.auth_service import AuthService

router = APIRouter()

@router.post("/register", response_model=Dict[str, str])
async def register_user(user_data: UserCreate, session: Session = Depends(get_session)):
    # Check if user already exists
    existing_user = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Register the user
    db_user = await AuthService.register_user(user_data, session)

    # Create access token
    access_token = await AuthService.create_token_for_user(db_user)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Dict[str, str])
async def login_user(user_credentials: UserCreate, session: Session = Depends(get_session)):
    user = await AuthService.authenticate_user(
        user_credentials.email,
        user_credentials.password,
        session
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = await AuthService.create_token_for_user(user)

    return {"access_token": access_token, "token_type": "bearer"}