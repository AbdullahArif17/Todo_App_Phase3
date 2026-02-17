from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from src.models.todo_task import TodoTask, TodoTaskCreate, TodoTaskUpdate
from src.models.user import User

class TodoService:
    @staticmethod
    async def create_todo(todo_data: TodoTaskCreate, user: User, db_session: Session) -> TodoTask:
        """
        Create a new todo task for a user
        """
        # Create todo instance with user association
        db_todo = TodoTask(
            title=todo_data.title,
            description=todo_data.description,
            is_completed=todo_data.is_completed,
            user_id=user.id
        )

        # Add to database
        db_session.add(db_todo)
        db_session.commit()
        db_session.refresh(db_todo)

        return db_todo

    @staticmethod
    async def get_user_todos(user: User, db_session: Session) -> List[TodoTask]:
        """
        Get all todo tasks for a specific user
        """
        statement = select(TodoTask).where(TodoTask.user_id == user.id)
        todos = db_session.exec(statement).all()
        return todos

    @staticmethod
    async def get_todo_by_id(todo_id: UUID, user: User, db_session: Session) -> Optional[TodoTask]:
        """
        Get a specific todo task by ID for a user (enforces user ownership)
        """
        statement = select(TodoTask).where(TodoTask.id == todo_id, TodoTask.user_id == user.id)
        todo = db_session.exec(statement).first()
        return todo

    @staticmethod
    async def update_todo(todo_id: UUID, todo_update: TodoTaskUpdate, user: User, db_session: Session) -> Optional[TodoTask]:
        """
        Update a todo task for a user (enforces user ownership)
        """
        # Get the existing todo
        statement = select(TodoTask).where(TodoTask.id == todo_id, TodoTask.user_id == user.id)
        todo = db_session.exec(statement).first()

        if not todo:
            return None

        # Update the todo with provided data
        update_data = todo_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(todo, field, value)

        # Update timestamp
        from datetime import datetime
        todo.updated_at = datetime.utcnow()

        # Commit changes
        db_session.add(todo)
        db_session.commit()
        db_session.refresh(todo)

        return todo

    @staticmethod
    async def delete_todo(todo_id: UUID, user: User, db_session: Session) -> bool:
        """
        Delete a todo task for a user (enforces user ownership)
        """
        # Get the existing todo
        statement = select(TodoTask).where(TodoTask.id == todo_id, TodoTask.user_id == user.id)
        todo = db_session.exec(statement).first()

        if not todo:
            return False

        # Delete the todo
        db_session.delete(todo)
        db_session.commit()

        return True

    @staticmethod
    async def delete_all_todos(user: User, db_session: Session) -> int:
        """
        Delete all todo tasks for a specific user
        """
        from sqlmodel import delete
        statement = delete(TodoTask).where(TodoTask.user_id == user.id)
        result = db_session.exec(statement)
        db_session.commit()
        return result.rowcount

    @staticmethod
    async def toggle_todo_completion(todo_id: UUID, is_completed: bool, user: User, db_session: Session) -> Optional[TodoTask]:
        """
        Toggle completion status of a todo task for a user (enforces user ownership)
        """
        # Get the existing todo
        statement = select(TodoTask).where(TodoTask.id == todo_id, TodoTask.user_id == user.id)
        todo = db_session.exec(statement).first()

        if not todo:
            return None

        # Update completion status
        todo.is_completed = is_completed
        from datetime import datetime
        todo.updated_at = datetime.utcnow()

        # Commit changes
        db_session.add(todo)
        db_session.commit()
        db_session.refresh(todo)

        return todo

    @staticmethod
    async def search_todos(query: str, user: User, db_session: Session) -> List[TodoTask]:
        """
        Search for todo tasks for a specific user based on a query string
        """
        from sqlmodel import or_
        search_pattern = f"%{query}%"
        statement = select(TodoTask).where(
            TodoTask.user_id == user.id,
            or_(
                TodoTask.title.ilike(search_pattern),
                TodoTask.description.ilike(search_pattern)
            )
        )
        todos = db_session.exec(statement).all()
        return todos