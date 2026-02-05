import uuid
from typing import List, Dict, Any
from apps.backend.src.models.message import Message
from apps.backend.src.models.conversation import Conversation


def format_conversation_for_ai(messages: List[Message], max_history: int = 20) -> List[Dict[str, str]]:
    """
    Format conversation messages for AI consumption.

    Args:
        messages: List of Message objects from the database
        max_history: Maximum number of messages to include in history

    Returns:
        List of dictionaries with role and content for AI consumption
    """
    # Take the most recent messages up to max_history
    recent_messages = messages[-max_history:] if len(messages) > max_history else messages

    formatted_messages = []
    for msg in recent_messages:
        formatted_messages.append({
            "role": msg.role,
            "content": msg.content
        })

    return formatted_messages


def truncate_conversation_history(messages: List[Message], max_tokens: int = 2000) -> List[Message]:
    """
    Truncate conversation history to stay within token limits.

    Args:
        messages: List of Message objects
        max_tokens: Maximum number of tokens to keep

    Returns:
        Truncated list of Message objects
    """
    # Simple token estimation: 1 token ≈ 4 characters
    estimated_tokens = 0
    truncated_messages = []

    # Process messages in reverse to keep recent ones
    for msg in reversed(messages):
        msg_tokens = len(msg.content) // 4
        if estimated_tokens + msg_tokens > max_tokens:
            break

        truncated_messages.insert(0, msg)  # Insert at beginning to maintain order
        estimated_tokens += msg_tokens

    return truncated_messages


def intelligent_conversation_truncation(messages: List[Message], max_tokens: int = 2000,
                                     preserve_recent: int = 5, preserve_first: int = 2) -> List[Message]:
    """
    Intelligently truncate conversation history by preserving important messages.

    Args:
        messages: List of Message objects
        max_tokens: Maximum number of tokens to keep
        preserve_recent: Number of most recent messages to always preserve
        preserve_first: Number of first messages to always preserve

    Returns:
        Intelligently truncated list of Message objects
    """
    if len(messages) <= preserve_recent + preserve_first:
        # If we have fewer messages than the sum of preserved amounts, return as is
        return messages

    # Calculate tokens for preserved messages
    preserved_tokens = 0
    for msg in messages[:preserve_first] + messages[-preserve_recent:]:
        preserved_tokens += len(msg.content) // 4

    # If preserved messages already exceed max_tokens, return just the most recent ones
    if preserved_tokens > max_tokens:
        # Return just the most recent messages that fit
        result = []
        tokens_used = 0
        for msg in reversed(messages[-preserve_recent:]):
            msg_tokens = len(msg.content) // 4
            if tokens_used + msg_tokens > max_tokens:
                break
            result.insert(0, msg)
            tokens_used += msg_tokens
        return result

    # Start with preserved messages
    result = messages[:preserve_first] + messages[-preserve_recent:]

    # Calculate remaining token budget
    remaining_tokens = max_tokens - preserved_tokens

    # Select important messages from the middle
    middle_messages = messages[preserve_first:-preserve_recent]

    # For now, we'll use a simple approach: take messages from the middle that fit
    # In a more sophisticated implementation, we might use NLP to identify important messages
    for msg in middle_messages:
        msg_tokens = len(msg.content) // 4
        if msg_tokens <= remaining_tokens:
            result.insert(preserve_first, msg)  # Insert after the initial preserved messages
            remaining_tokens -= msg_tokens

    # Sort to maintain chronological order
    result = sorted(result, key=lambda x: x.timestamp)

    return result


def calculate_message_importance(message: Message, position: int, total_messages: int) -> float:
    """
    Calculate the importance score of a message for intelligent selection.

    Args:
        message: Message object
        position: Position of message in conversation (0-indexed)
        total_messages: Total number of messages in conversation

    Returns:
        Importance score (higher is more important)
    """
    importance = 0.0

    # Messages at the beginning and end are typically more important
    if position < total_messages * 0.1:  # First 10%
        importance += 1.0
    elif position > total_messages * 0.9:  # Last 10%
        importance += 1.5  # Slightly higher weight for recent messages

    # Assistant responses may be more important for context
    if message.role == "assistant":
        importance += 0.5

    # Longer messages might contain more important information
    if len(message.content) > 100:  # Adjust threshold as needed
        importance += 0.3

    # Keywords that might indicate importance
    important_keywords = ["summary", "conclusion", "important", "key", "critical", "remember", "note"]
    content_lower = message.content.lower()
    for keyword in important_keywords:
        if keyword in content_lower:
            importance += 0.2

    return importance


def intelligent_truncate_by_importance(messages: List[Message], max_tokens: int = 2000) -> List[Message]:
    """
    Truncate conversation by selecting messages based on calculated importance.

    Args:
        messages: List of Message objects
        max_tokens: Maximum number of tokens to keep

    Returns:
        Intelligently truncated list of Message objects
    """
    if not messages:
        return []

    # Calculate importance scores for all messages
    message_importance_pairs = []
    for i, msg in enumerate(messages):
        importance = calculate_message_importance(msg, i, len(messages))
        message_importance_pairs.append((msg, importance))

    # Sort by importance in descending order
    message_importance_pairs.sort(key=lambda x: x[1], reverse=True)

    # Select messages until we reach the token limit
    selected_messages = []
    tokens_used = 0

    for msg, _ in message_importance_pairs:
        msg_tokens = len(msg.content) // 4
        if tokens_used + msg_tokens <= max_tokens:
            selected_messages.append(msg)
            tokens_used += msg_tokens
        else:
            break

    # Return selected messages in chronological order
    return sorted(selected_messages, key=lambda x: x.timestamp)


def intelligent_conversation_truncation(messages: List[Message], max_tokens: int = 2000, preserve_recent: int = 5, preserve_first: int = 2) -> List[Message]:
    """
    Truncate conversation by preserving important messages based on position and content.

    Args:
        messages: List of Message objects
        max_tokens: Maximum number of tokens to keep
        preserve_recent: Number of most recent messages to always preserve
        preserve_first: Number of first messages to always preserve

    Returns:
        Intelligently truncated list of Message objects
    """
    if len(messages) <= preserve_recent + preserve_first:
        # If we have fewer messages than the sum of preserved amounts, return as is
        return messages

    # Calculate tokens for preserved messages
    preserved_tokens = 0
    preserved_portion = messages[:preserve_first] + messages[-preserve_recent:]
    for msg in preserved_portion:
        preserved_tokens += len(msg.content) // 4

    # If preserved messages already exceed max_tokens, return just the most recent ones
    if preserved_tokens > max_tokens:
        # Return just the most recent messages that fit
        result = []
        tokens_used = 0
        for msg in reversed(messages[-preserve_recent:]):
            msg_tokens = len(msg.content) // 4
            if tokens_used + msg_tokens > max_tokens:
                break
            result.insert(0, msg)  # Insert at beginning to maintain order
            tokens_used += msg_tokens
        return result

    # Start with preserved messages
    result = preserved_portion

    # Calculate remaining token budget
    remaining_tokens = max_tokens - preserved_tokens

    # Select important messages from the middle
    middle_messages = messages[preserve_first:-preserve_recent]

    # For now, we'll use a simple approach: take messages from the middle that fit
    # In a more sophisticated implementation, we might use NLP to identify important messages
    for msg in middle_messages:
        msg_tokens = len(msg.content) // 4
        if msg_tokens <= remaining_tokens:
            # Insert after the initial preserved messages, but maintain chronological order
            insert_idx = preserve_first
            result.insert(insert_idx, msg)
            remaining_tokens -= msg_tokens

    # Sort to maintain chronological order
    result = sorted(result, key=lambda x: x.timestamp)

    return result


def build_system_prompt_for_user(user_id: uuid.UUID) -> str:
    """
    Build a system prompt tailored to the specific user.

    Args:
        user_id: The ID of the user

    Returns:
        System prompt string
    """
    return (
        f"You are a helpful AI assistant that helps user {str(user_id)[:8]} manage their todo lists. "
        "You can help create, update, delete, and list todos. "
        "Always respond in a friendly and helpful manner. "
        "If the user wants to perform a todo operation, you should respond with clear instructions about what you're doing. "
        "Keep your responses concise but helpful."
    )


def estimate_token_count(text: str) -> int:
    """
    Estimate the number of tokens in a text string.

    Args:
        text: Input text string

    Returns:
        Estimated token count
    """
    # Simple estimation: 1 token ≈ 4 characters
    return len(text) // 4


def format_todo_list_for_ai(todo_items: List[Any]) -> str:
    """
    Format a list of todo items for AI consumption.

    Args:
        todo_items: List of todo objects

    Returns:
        Formatted string representation of todo list
    """
    if not todo_items:
        return "No todos in the list."

    formatted_list = "Current todos:\n"
    for i, todo in enumerate(todo_items, 1):
        status = "✓" if getattr(todo, 'completed', False) else "○"
        formatted_list += f"{i}. [{status}] {getattr(todo, 'title', 'Unknown')} - {getattr(todo, 'description', '')}\n"

    return formatted_list