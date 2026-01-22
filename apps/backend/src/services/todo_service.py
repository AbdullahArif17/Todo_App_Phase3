from sqlmodel import Session, select
from typing import List, Optional
from ..models.todo_task import TodoTask
from ..schemas.todo_task import TodoTaskCreate, TodoTaskUpdate
from ..models.user import User

class TodoService:
    @staticmethod
    async def create_todo(todo_data: TodoTaskCreate, user: User, db: Session) -> TodoTask:
        # Create the todo task
        db_todo = TodoTask(
            title=todo_data.title,
            description=todo_data.description,
            user_id=user.id
        )

        # Add to database
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)

        return db_todo

    @staticmethod
    async def get_todos(user: User, db: Session) -> List[TodoTask]:
        # Get all todos for the user
        statement = select(TodoTask).where(TodoTask.user_id == user.id)
        todos = db.exec(statement).all()
        return todos

    @staticmethod
    async def get_todo_by_id(todo_id: str, user: User, db: Session) -> Optional[TodoTask]:
        # Get a specific todo for the user
        statement = select(TodoTask).where(TodoTask.id == todo_id, TodoTask.user_id == user.id)
        todo = db.exec(statement).first()
        return todo

    @staticmethod
    async def update_todo(todo_id: str, todo_update: TodoTaskUpdate, user: User, db: Session) -> Optional[TodoTask]:
        # Get the todo
        statement = select(TodoTask).where(TodoTask.id == todo_id, TodoTask.user_id == user.id)
        todo = db.exec(statement).first()

        if not todo:
            return None

        # Update the todo with provided data
        update_data = todo_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(todo, field, value)

        db.add(todo)
        db.commit()
        db.refresh(todo)

        return todo

    @staticmethod
    async def delete_todo(todo_id: str, user: User, db: Session) -> bool:
        # Get the todo
        statement = select(TodoTask).where(TodoTask.id == todo_id, TodoTask.user_id == user.id)
        todo = db.exec(statement).first()

        if not todo:
            return False

        # Delete the todo
        db.delete(todo)
        db.commit()

        return True

    @staticmethod
    async def toggle_complete(todo_id: str, is_completed: bool, user: User, db: Session) -> Optional[TodoTask]:
        # Get the todo
        statement = select(TodoTask).where(TodoTask.id == todo_id, TodoTask.user_id == user.id)
        todo = db.exec(statement).first()

        if not todo:
            return None

        # Update completion status
        todo.is_completed = is_completed

        db.add(todo)
        db.commit()
        db.refresh(todo)

        return todo