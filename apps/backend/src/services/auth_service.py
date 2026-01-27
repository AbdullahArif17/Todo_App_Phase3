from sqlmodel import Session, select
from typing import Optional
from datetime import timedelta
from uuid import UUID
from ..models.user import User, UserCreate
from ..utils.security import get_password_hash, verify_password
from sqlmodel import select
from uuid import UUID
from ..core.security import create_access_token
from ..core.config import settings

class AuthService:
    @staticmethod
    def register_user(user_data: UserCreate, db_session: Session) -> User:
        """
        Register a new user with hashed password
        """
        # Hash the password
        hashed_password = get_password_hash(user_data.password)

        # Create user instance
        db_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password
        )

        # Add to database
        db_session.add(db_user)
        db_session.commit()
        db_session.refresh(db_user)

        return db_user

    @staticmethod
    def authenticate_user(email: str, password: str, db_session: Session) -> Optional[User]:
        """
        Authenticate user with email and password
        """
        # Find user by email
        statement = select(User).where(User.email == email)
        user = db_session.exec(statement).first()

        if not user or not verify_password(password, user.hashed_password):
            return None

        return user

    @staticmethod
    def create_access_token_for_user(user: User) -> str:
        """
        Create access token for authenticated user
        """
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires
        )
        return access_token