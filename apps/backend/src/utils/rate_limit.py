import time
from typing import Dict
from collections import defaultdict
import threading
from uuid import UUID


class AIRateLimiter:
    """
    Simple rate limiter for AI service usage per user.
    """
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[UUID, list] = defaultdict(list)  # user_id -> list of request timestamps
        self._lock = threading.Lock()

    def is_allowed(self, user_id: UUID) -> bool:
        """
        Check if a user is allowed to make an AI request.

        Args:
            user_id: The ID of the user making the request

        Returns:
            True if the request is allowed, False otherwise
        """
        with self._lock:
            now = time.time()

            # Remove requests older than 1 minute
            self.requests[user_id] = [
                req_time for req_time in self.requests[user_id]
                if now - req_time < 60
            ]

            # Check if the user has exceeded the rate limit
            if len(self.requests[user_id]) >= self.requests_per_minute:
                return False

            # Add the current request
            self.requests[user_id].append(now)
            return True

    def reset_user(self, user_id: UUID):
        """
        Reset the rate limit for a specific user.

        Args:
            user_id: The ID of the user to reset
        """
        with self._lock:
            if user_id in self.requests:
                del self.requests[user_id]


class ConversationAwareRateLimiter:
    """
    Rate limiter that considers conversation-specific factors for more nuanced control.
    """
    def __init__(self,
                 global_requests_per_minute: int = 30,
                 conversation_requests_per_minute: int = 10,
                 burst_requests: int = 5):
        self.global_requests_per_minute = global_requests_per_minute
        self.conversation_requests_per_minute = conversation_requests_per_minute
        self.burst_requests = burst_requests

        # Track requests globally per user
        self.global_requests: Dict[UUID, list] = defaultdict(list)

        # Track requests per conversation
        self.conversation_requests: Dict[UUID, Dict[UUID, list]] = defaultdict(lambda: defaultdict(list))  # user_id -> conversation_id -> list of timestamps

        self._lock = threading.Lock()

    def is_allowed(self, user_id: UUID, conversation_id: UUID = None) -> bool:
        """
        Check if a request is allowed based on both global and conversation-specific limits.

        Args:
            user_id: The ID of the user making the request
            conversation_id: Optional ID of the conversation (for conversation-specific limits)

        Returns:
            True if the request is allowed, False otherwise
        """
        with self._lock:
            now = time.time()

            # Check global user limit
            self.global_requests[user_id] = [
                req_time for req_time in self.global_requests[user_id]
                if now - req_time < 60
            ]

            if len(self.global_requests[user_id]) >= self.global_requests_per_minute:
                return False

            # If a conversation is specified, check conversation-specific limit
            if conversation_id:
                # Clean up old requests for this conversation
                self.conversation_requests[user_id][conversation_id] = [
                    req_time for req_time in self.conversation_requests[user_id][conversation_id]
                    if now - req_time < 60
                ]

                if len(self.conversation_requests[user_id][conversation_id]) >= self.conversation_requests_per_minute:
                    return False

            # Add the current request
            self.global_requests[user_id].append(now)

            if conversation_id:
                self.conversation_requests[user_id][conversation_id].append(now)

            return True

    def reset_user(self, user_id: UUID):
        """
        Reset the rate limit for a specific user.

        Args:
            user_id: The ID of the user to reset
        """
        with self._lock:
            if user_id in self.global_requests:
                del self.global_requests[user_id]

            if user_id in self.conversation_requests:
                del self.conversation_requests[user_id]

    def reset_conversation(self, user_id: UUID, conversation_id: UUID):
        """
        Reset the rate limit for a specific conversation.

        Args:
            user_id: The ID of the user
            conversation_id: The ID of the conversation to reset
        """
        with self._lock:
            if user_id in self.conversation_requests and conversation_id in self.conversation_requests[user_id]:
                del self.conversation_requests[user_id][conversation_id]


# Global rate limiter instances
ai_rate_limiter = AIRateLimiter(requests_per_minute=30)  # 30 requests per minute per user
conversation_aware_rate_limiter = ConversationAwareRateLimiter(
    global_requests_per_minute=30,
    conversation_requests_per_minute=10,
    burst_requests=5
)