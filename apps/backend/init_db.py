from sqlmodel import SQLModel, create_engine
from src.core.config import settings
from src.models.user import User
from src.models.todo_task import TodoTask

def init_db():
    engine = create_engine(settings.DATABASE_URL)
    SQLModel.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()