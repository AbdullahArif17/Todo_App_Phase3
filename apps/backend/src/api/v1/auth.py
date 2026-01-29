from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Dict
from ..deps import get_db_session, get_current_active_user
from ...services.auth_service import AuthService
from ...models.user import UserCreate, UserLogin, UserResponse
from datetime import timedelta
from ..core.config import settings
from ..core.security import create_access_token
from jose import JWTError

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(
    user_data: UserCreate,
    db_session: Session = Depends(get_db_session)
):
    """
    Register a new user
    """
    try:
        # Check if user already exists
        existing_user = AuthService.get_user_by_email(user_data.email, db_session)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        # Register the user
        db_user = AuthService.register_user(user_data, db_session)

        # Create response without sensitive data
        return UserResponse(
            id=db_user.id,
            email=db_user.email,
            full_name=db_user.full_name,
            is_active=db_user.is_active,
            created_at=db_user.created_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login")
def login(
    user_credentials: UserLogin,
    db_session: Session = Depends(get_db_session)
) -> Dict[str, str]:
    """
    Login a user and return an access token
    """
    user = AuthService.authenticate_user(
        user_credentials.email,
        user_credentials.password,
        db_session
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = AuthService.create_access_token_for_user(user)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(user.id),
        "email": user.email
    }


@router.post("/refresh")
def refresh_token(
    current_user: UserResponse = Depends(get_current_active_user)
) -> Dict[str, str]:
    """
    Refresh the access token
    """
    # Create a new access token with the same user data
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(current_user.id), "email": current_user.email},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }