from sqlmodel import SQLModel, create_engine
from .engine import engine
from ..models.user import User
from ..models.todo_task import TodoTask

def init_db():
    """
    Initialize the database with required tables
    """
    print("Initializing database tables...")
    SQLModel.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()