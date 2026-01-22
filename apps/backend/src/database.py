from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session
from .core.config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    poolclass=StaticPool if "sqlite" in settings.DATABASE_URL else None
)

def get_session():
    with Session(engine) as session:
        yield session