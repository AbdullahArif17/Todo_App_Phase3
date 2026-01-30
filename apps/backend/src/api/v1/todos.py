from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List
from uuid import UUID
from src.api.deps import get_current_user, get_db_session
from src.models.user import User
from src.models.todo_task import TodoTask, TodoTaskCreate, TodoTaskUpdate
from src.services.todo_service import TodoService

router = APIRouter()

@router.get("/", response_model=List[TodoTask])
async def get_todos(
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
) -> List[TodoTask]:
    """
    Get all todo tasks for the current user
    """
    todos = await TodoService.get_user_todos(current_user, db_session)
    return todos


@router.post("/", response_model=TodoTask)
async def create_todo(
    todo_data: TodoTaskCreate,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
) -> TodoTask:
    """
    Create a new todo task for the current user
    """
    todo = await TodoService.create_todo(todo_data, current_user, db_session)
    return todo


@router.get("/{todo_id}", response_model=TodoTask)
async def get_todo(
    todo_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
) -> TodoTask:
    """
    Get a specific todo task by ID (user must own the task)
    """
    todo = await TodoService.get_todo_by_id(todo_id, current_user, db_session)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo task not found"
        )
    return todo


@router.put("/{todo_id}", response_model=TodoTask)
async def update_todo(
    todo_id: UUID,
    todo_update: TodoTaskUpdate,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
) -> TodoTask:
    """
    Update a specific todo task (user must own the task)
    """
    todo = await TodoService.update_todo(todo_id, todo_update, current_user, db_session)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo task not found"
        )
    return todo


@router.delete("/{todo_id}")
async def delete_todo(
    todo_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
) -> dict:
    """
    Delete a specific todo task (user must own the task)
    """
    success = await TodoService.delete_todo(todo_id, current_user, db_session)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo task not found"
        )
    return {"message": "Todo task deleted successfully"}


@router.patch("/{todo_id}/complete")
async def toggle_todo_completion(
    todo_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
) -> TodoTask:
    """
    Toggle completion status of a specific todo task (user must own the task)
    """
    # Get the current todo to check its current completion status
    current_todo = await TodoService.get_todo_by_id(todo_id, current_user, db_session)
    if not current_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo task not found"
        )

    # Toggle the completion status
    new_completion_status = not current_todo.is_completed

    # Update using the service
    todo = await TodoService.toggle_todo_completion(todo_id, new_completion_status, current_user, db_session)
    return todo