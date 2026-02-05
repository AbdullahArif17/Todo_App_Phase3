import logging
from typing import Optional
import uuid


def setup_chat_logging():
    """
    Set up logging configuration for chat operations.
    """
    logger = logging.getLogger("chat_operations")
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def log_chat_access_attempt(user_id: uuid.UUID, conversation_id: Optional[uuid.UUID], success: bool, action: str):
    """
    Log chat access attempts for security monitoring.

    Args:
        user_id: The ID of the user attempting access
        conversation_id: The ID of the conversation (if applicable)
        success: Whether the access was successful
        action: The type of action being performed
    """
    logger = logging.getLogger("chat_operations")

    if success:
        logger.info(f"User {user_id} successfully accessed conversation {conversation_id} for {action}")
    else:
        logger.warning(f"User {user_id} failed to access conversation {conversation_id} for {action}")


def log_security_event(event_type: str, user_id: Optional[uuid.UUID] = None, details: str = ""):
    """
    Log security-related events.

    Args:
        event_type: Type of security event
        user_id: The ID of the user involved (if applicable)
        details: Additional details about the event
    """
    logger = logging.getLogger("security_events")
    logger.warning(f"Security event: {event_type} - User: {user_id} - Details: {details}")