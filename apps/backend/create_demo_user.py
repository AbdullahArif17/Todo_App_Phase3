import asyncio
from sqlmodel import SQLModel, create_engine, Session, select
from src.models.user import User
from src.utils.security import get_password_hash
from src.core.config import settings

def create_demo_user():
    # Create engine and connect to database
    engine = create_engine(settings.DATABASE_URL)

    # Create tables if they don't exist
    SQLModel.metadata.create_all(bind=engine)

    # Create a session
    with Session(engine) as session:
        # Check if demo user already exists
        demo_email = "demo@example.com"
        existing_user = session.exec(select(User).where(User.email == demo_email)).first()

        if existing_user:
            print("Demo user already exists!")
            print(f"Email: {demo_email}")
            print("Password: demopass123")
            return

        # Create hashed password
        hashed_password = get_password_hash("demopass123")

        # Create demo user
        demo_user = User(
            email=demo_email,
            hashed_password=hashed_password,
            is_active=True
        )

        # Add to database
        session.add(demo_user)
        session.commit()
        session.refresh(demo_user)

        print("Demo user created successfully!")
        print(f"Email: {demo_email}")
        print("Password: demopass123")
        print(f"User ID: {demo_user.id}")

if __name__ == "__main__":
    create_demo_user()