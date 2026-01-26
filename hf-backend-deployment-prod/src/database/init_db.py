from sqlmodel import SQLModel, create_engine
from ..core.config import settings
from ..models.user import User
from ..models.todo_task import TodoTask

def init_db():
    """
    Initialize the database with required tables
    """
    engine = create_engine(settings.DATABASE_URL)
    # Create all tables
    SQLModel.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()