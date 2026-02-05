"""
Authentication Middleware for MCP Server
Handles authentication and authorization for MCP tools
"""
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import jwt
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session
from apps.backend.src.config import settings
from apps.backend.src.models.user import User
from apps.backend.src.database import engine
from apps.backend.src.services.user_service import UserService
import uuid


security = HTTPBearer()


def verify_token(token: str) -> dict:
    """
    Verify JWT token and return payload.

    Args:
        token: JWT token string

    Returns:
        Token payload as dictionary

    Raises:
        jwt.exceptions.InvalidTokenError: If token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except InvalidTokenError:
        raise InvalidTokenError("Could not decode token")


async def get_current_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    Get current user from JWT token in authorization header.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        User object if token is valid and user exists

    Raises:
        HTTPException: If token is invalid, user doesn't exist, or user is inactive
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = verify_token(credentials.credentials)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    # Get user from database
    with Session(engine) as session:
        user_service = UserService()
        user = user_service.get_user_by_id(session, uuid.UUID(user_id))

    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user


async def validate_user_owns_resource(user: User, resource_user_id: uuid.UUID) -> bool:
    """
    Validate that a user owns a specific resource by comparing user IDs.

    Args:
        user: The authenticated user
        resource_user_id: The user ID associated with the resource

    Returns:
        True if user owns the resource, False otherwise
    """
    return str(user.id) == str(resource_user_id)


def require_user_ownership(user: User, resource_user_id: uuid.UUID):
    """
    Decorator-like function to require that a user owns a resource.

    Args:
        user: The authenticated user
        resource_user_id: The user ID associated with the resource

    Raises:
        HTTPException: If the user doesn't own the resource
    """
    if not validate_user_owns_resource(user, resource_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have permission to access this resource"
        )


# For use in MCP tools, we'll provide a function that validates user_id parameter
def validate_user_id_param(user_id_param: str, authenticated_user: User) -> bool:
    """
    Validate that the user_id parameter matches the authenticated user.

    Args:
        user_id_param: The user_id passed as a parameter to the tool
        authenticated_user: The user authenticated via JWT

    Returns:
        True if the user_id parameter matches the authenticated user, False otherwise
    """
    try:
        param_uuid = uuid.UUID(user_id_param)
        return str(param_uuid) == str(authenticated_user.id)
    except ValueError:
        # If the parameter is not a valid UUID, it definitely doesn't match
        return False


def validate_user_access_to_task(user: User, task_user_id: uuid.UUID) -> bool:
    """
    Validate that a user has access to a specific task by checking ownership.

    Args:
        user: The authenticated user
        task_user_id: The user ID associated with the task

    Returns:
        True if user has access to the task, False otherwise
    """
    return str(user.id) == str(task_user_id)