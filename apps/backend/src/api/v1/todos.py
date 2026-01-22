from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List
from uuid import UUID
from ...database import get_session
from ...models.user import User
from ...models.todo_task import TodoTask
from ...schemas.todo_task import TodoTaskCreate, TodoTaskUpdate
from ...services.todo_service import TodoService
from ..deps import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[TodoTask])
async def get_todos(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    todos = await TodoService.get_todos(current_user, session)
    return todos


@router.post("/", response_model=TodoTask)
async def create_todo(
    todo_data: TodoTaskCreate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    todo = await TodoService.create_todo(todo_data, current_user, session)
    return todo


@router.get("/{id}", response_model=TodoTask)
async def get_todo(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    todo = await TodoService.get_todo_by_id(str(id), current_user, session)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    return todo


@router.put("/{id}", response_model=TodoTask)
async def update_todo(
    id: UUID,
    todo_update: TodoTaskUpdate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    todo = await TodoService.update_todo(str(id), todo_update, current_user, session)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    return todo


@router.delete("/{id}")
async def delete_todo(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    success = await TodoService.delete_todo(str(id), current_user, session)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    return {"message": "Todo deleted successfully"}


@router.patch("/{id}/complete")
async def toggle_todo_completion(
    id: UUID,
    is_completed: bool,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    todo = await TodoService.toggle_complete(str(id), is_completed, current_user, session)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    return todo