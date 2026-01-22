from sqlmodel import Session, select
from typing import Optional
from ..models.user import User
from ..schemas.user import UserCreate, UserInDB
from ..utils.security import get_password_hash
from ..core.security import create_access_token
from datetime import timedelta

class AuthService:
    @staticmethod
    async def register_user(user_data: UserCreate, db: Session) -> User:
        # Hash the password
        hashed_password = get_password_hash(user_data.password)

        # Create the user
        db_user = User(
            email=user_data.email,
            hashed_password=hashed_password
        )

        # Add to database
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    @staticmethod
    async def authenticate_user(email: str, password: str, db: Session) -> Optional[User]:
        # Find user by email
        statement = select(User).where(User.email == email)
        user = db.exec(statement).first()

        if not user:
            return None

        # Verify password
        from ..utils.security import verify_password
        if not verify_password(password, user.hashed_password):
            return None

        return user

    @staticmethod
    async def create_token_for_user(user: User) -> str:
        # Create access token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=access_token_expires
        )
        return access_token