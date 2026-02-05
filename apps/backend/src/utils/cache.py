import time
from typing import Any, Dict, Optional, Union
from collections import OrderedDict
import threading
import uuid


class LRUCache:
    """
    Simple in-memory LRU cache for conversation metadata.
    Thread-safe with basic locking mechanism.
    """
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache = OrderedDict()  # Key: (cache_key), Value: (value, timestamp)
        self.lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache if it exists and hasn't expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        with self.lock:
            if key not in self.cache:
                return None

            value, timestamp = self.cache[key]

            # Check if TTL has expired
            if time.time() - timestamp > self.ttl_seconds:
                del self.cache[key]
                return None

            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return value

    def put(self, key: str, value: Any):
        """
        Put a value in the cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        with self.lock:
            # Remove expired entries if needed
            current_time = time.time()
            expired_keys = []
            for k, (_, ts) in self.cache.items():
                if current_time - ts > self.ttl_seconds:
                    expired_keys.append(k)

            for k in expired_keys:
                del self.cache[k]

            self.cache[key] = (value, current_time)

            # Remove oldest entries if we exceed max_size
            while len(self.cache) > self.max_size:
                self.cache.popitem(last=False)

    def delete(self, key: str):
        """
        Delete a key from the cache.

        Args:
            key: Cache key to delete
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]

    def clear(self):
        """Clear all entries from the cache."""
        with self.lock:
            self.cache.clear()


# Global cache instance for conversation metadata
conversation_cache = LRUCache(max_size=500, ttl_seconds=300)  # 500 entries, 5 min TTL


def get_conversation_cache_key(conversation_id: uuid.UUID) -> str:
    """
    Generate a cache key for conversation metadata.

    Args:
        conversation_id: ID of the conversation

    Returns:
        Cache key string
    """
    return f"conversation_meta:{conversation_id}"


def get_user_conversations_cache_key(user_id: uuid.UUID) -> str:
    """
    Generate a cache key for user's conversation list.

    Args:
        user_id: ID of the user

    Returns:
        Cache key string
    """
    return f"user_conversations:{user_id}"


def invalidate_conversation_cache(conversation_id: uuid.UUID):
    """
    Invalidate cached data for a specific conversation.

    Args:
        conversation_id: ID of the conversation to invalidate
    """
    cache_key = get_conversation_cache_key(conversation_id)
    conversation_cache.delete(cache_key)

    # Also invalidate user's conversation list
    # We'd need to know the user_id for this, so we'll skip for now
    # This would require additional tracking of user-conversation relationships


def invalidate_user_conversations_cache(user_id: uuid.UUID):
    """
    Invalidate cached conversation list for a user.

    Args:
        user_id: ID of the user
    """
    cache_key = get_user_conversations_cache_key(user_id)
    conversation_cache.delete(cache_key)