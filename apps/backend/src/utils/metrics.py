from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import threading
import time
from enum import Enum


class MetricType(Enum):
    """Types of metrics that can be tracked."""
    CONVERSATION_COUNT = "conversation_count"
    MESSAGE_COUNT = "message_count"
    USER_ACTIVE = "user_active"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    TOKEN_USAGE = "token_usage"


class ConversationMetrics:
    """
    Tracks and manages metrics related to conversations and user interactions.
    """

    def __init__(self):
        self.metrics = defaultdict(list)
        self.counters = defaultdict(int)
        self.timers = defaultdict(float)
        self.histograms = defaultdict(list)
        self.user_sessions = {}  # user_id -> last_active_time
        self.lock = threading.RLock()

    def record_metric(self, metric_type: MetricType, value: float, labels: Optional[Dict[str, str]] = None):
        """
        Record a metric with optional labels.

        Args:
            metric_type: Type of metric being recorded
            value: Numeric value of the metric
            labels: Optional dictionary of labels for the metric
        """
        with self.lock:
            label_key = self._get_label_key(metric_type.value, labels)
            self.metrics[label_key].append({
                'value': value,
                'timestamp': datetime.utcnow()
            })

            # Keep only recent metrics (last hour)
            cutoff = datetime.utcnow() - timedelta(hours=1)
            self.metrics[label_key] = [
                m for m in self.metrics[label_key]
                if m['timestamp'] >= cutoff
            ]

    def increment_counter(self, counter_name: str, amount: int = 1, labels: Optional[Dict[str, str]] = None):
        """
        Increment a counter metric.

        Args:
            counter_name: Name of the counter
            amount: Amount to increment by
            labels: Optional dictionary of labels for the counter
        """
        with self.lock:
            label_key = self._get_label_key(counter_name, labels)
            self.counters[label_key] += amount

    def record_timer(self, timer_name: str, duration: float, labels: Optional[Dict[str, str]] = None):
        """
        Record a timing measurement.

        Args:
            timer_name: Name of the timer
            duration: Duration in seconds
            labels: Optional dictionary of labels for the timer
        """
        with self.lock:
            label_key = self._get_label_key(timer_name, labels)
            self.timers[label_key] = duration

    def record_histogram(self, histogram_name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """
        Record a value in a histogram.

        Args:
            histogram_name: Name of the histogram
            value: Value to record
            labels: Optional dictionary of labels for the histogram
        """
        with self.lock:
            label_key = self._get_label_key(histogram_name, labels)
            self.histograms[label_key].append(value)

            # Keep only recent values (last hour)
            cutoff = time.time() - 3600  # 1 hour ago
            self.histograms[label_key] = [
                v for v in self.histograms[label_key]
            ][-1000:]  # Keep only last 1000 values

    def _get_label_key(self, name: str, labels: Optional[Dict[str, str]]) -> str:
        """
        Generate a unique key for a metric based on name and labels.

        Args:
            name: Name of the metric
            labels: Optional labels for the metric

        Returns:
            Unique string key for the metric
        """
        if not labels:
            return name

        # Create a consistent key from labels
        label_str = ','.join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}[{label_str}]"

    def get_conversation_metrics(self, hours: int = 1) -> Dict[str, Any]:
        """
        Get comprehensive conversation metrics.

        Args:
            hours: Number of hours to look back

        Returns:
            Dictionary containing conversation metrics
        """
        with self.lock:
            cutoff = datetime.utcnow() - timedelta(hours=hours)

            # Calculate conversation count
            conversation_metrics = [
                m for m in self.metrics[MetricType.CONVERSATION_COUNT.value]
                if m['timestamp'] >= cutoff
            ]
            conversation_count = len(conversation_metrics)

            # Calculate message count
            message_metrics = [
                m for m in self.metrics[MetricType.MESSAGE_COUNT.value]
                if m['timestamp'] >= cutoff
            ]
            message_count = len(message_metrics)

            # Calculate average response time
            response_time_metrics = [
                m for m in self.metrics[MetricType.RESPONSE_TIME.value]
                if m['timestamp'] >= cutoff
            ]
            avg_response_time = sum(m['value'] for m in response_time_metrics) / len(response_time_metrics) if response_time_metrics else 0

            # Calculate error rate
            error_metrics = [
                m for m in self.metrics[MetricType.ERROR_RATE.value]
                if m['timestamp'] >= cutoff
            ]
            total_errors = sum(m['value'] for m in error_metrics)
            error_rate = total_errors / len(error_metrics) if error_metrics else 0

            # Calculate token usage
            token_metrics = [
                m for m in self.metrics[MetricType.TOKEN_USAGE.value]
                if m['timestamp'] >= cutoff
            ]
            total_tokens = sum(m['value'] for m in token_metrics)

            return {
                'period_hours': hours,
                'conversation_count': conversation_count,
                'message_count': message_count,
                'average_response_time_seconds': round(avg_response_time, 3),
                'error_rate': round(error_rate, 4),
                'total_tokens_used': int(total_tokens),
                'active_users': len(set(
                    user_id for user_id, last_active in self.user_sessions.items()
                    if datetime.utcnow() - last_active < timedelta(hours=1)
                )),
                'timestamp': datetime.utcnow().isoformat()
            }

    def track_user_activity(self, user_id: uuid.UUID):
        """
        Track when a user was last active.

        Args:
            user_id: ID of the user
        """
        with self.lock:
            self.user_sessions[user_id] = datetime.utcnow()

    def get_user_engagement_metrics(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Get engagement metrics for a specific user.

        Args:
            user_id: ID of the user

        Returns:
            Dictionary containing user engagement metrics
        """
        with self.lock:
            user_key = self._get_label_key('user_conversations', {'user_id': str(user_id)})
            user_conversations = [
                m for m in self.metrics[MetricType.CONVERSATION_COUNT.value]
                if user_key in m.get('labels', {})
            ]

            user_messages_key = self._get_label_key('user_messages', {'user_id': str(user_id)})
            user_messages = [
                m for m in self.metrics[MetricType.MESSAGE_COUNT.value]
                if user_messages_key in m.get('labels', {})
            ]

            return {
                'user_id': str(user_id),
                'conversation_count': len(user_conversations),
                'message_count': len(user_messages),
                'last_active': self.user_sessions.get(user_id, None),
                'is_active_recently': (
                    user_id in self.user_sessions and
                    datetime.utcnow() - self.user_sessions[user_id] < timedelta(minutes=30)
                )
            }

    def get_top_metrics(self, metric_type: MetricType, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top values for a specific metric type.

        Args:
            metric_type: Type of metric to get
            limit: Maximum number of results to return

        Returns:
            List of top metric values
        """
        with self.lock:
            results = []
            for key, values in self.metrics.items():
                if metric_type.value in key:
                    if values:
                        avg_value = sum(v['value'] for v in values) / len(values)
                        results.append({
                            'metric': key,
                            'average_value': avg_value,
                            'count': len(values),
                            'latest_value': values[-1]['value'] if values else 0
                        })

            # Sort by average value (descending)
            results.sort(key=lambda x: x['average_value'], reverse=True)
            return results[:limit]

    def reset_metrics(self):
        """
        Reset all metrics to their initial state.
        """
        with self.lock:
            self.metrics.clear()
            self.counters.clear()
            self.timers.clear()
            self.histograms.clear()
            self.user_sessions.clear()


# Global metrics instance
conversation_metrics = ConversationMetrics()


def record_conversation_started(user_id: uuid.UUID, conversation_id: uuid.UUID):
    """Record when a conversation is started."""
    conversation_metrics.increment_counter(MetricType.CONVERSATION_COUNT.value)
    conversation_metrics.track_user_activity(user_id)


def record_message_sent(user_id: uuid.UUID, conversation_id: uuid.UUID, message_length: int):
    """Record when a message is sent."""
    conversation_metrics.increment_counter(MetricType.MESSAGE_COUNT.value)
    conversation_metrics.track_user_activity(user_id)


def record_response_time(duration_seconds: float, user_id: uuid.UUID = None):
    """Record the response time of an operation."""
    labels = {'user_id': str(user_id)} if user_id else {}
    conversation_metrics.record_metric(MetricType.RESPONSE_TIME.value, duration_seconds, labels)


def record_error_occurred(error_type: str, user_id: uuid.UUID = None):
    """Record when an error occurs."""
    labels = {'user_id': str(user_id), 'error_type': error_type} if user_id else {'error_type': error_type}
    conversation_metrics.record_metric(MetricType.ERROR_RATE.value, 1.0, labels)


def record_token_usage(tokens: int, user_id: uuid.UUID = None):
    """Record token usage."""
    labels = {'user_id': str(user_id)} if user_id else {}
    conversation_metrics.record_metric(MetricType.TOKEN_USAGE.value, tokens, labels)


def get_current_metrics() -> Dict[str, Any]:
    """Get the current state of all metrics."""
    return conversation_metrics.get_conversation_metrics(hours=1)