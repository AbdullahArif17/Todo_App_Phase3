from typing import Dict, Any, List, Optional
import time
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque
import uuid


class MetricsCollector:
    """
    Collects and stores various conversation-related metrics for monitoring.
    """

    def __init__(self, max_points: int = 1000):
        self.max_points = max_points

        # Metrics storage
        self.request_times = deque(maxlen=max_points)
        self.error_counts = defaultdict(int)
        self.conversation_counts = defaultdict(int)
        self.message_counts = defaultdict(int)

        # Performance tracking
        self.performance_metrics = {
            'avg_response_time': 0.0,
            'request_count': 0,
            'error_rate': 0.0
        }

        self.lock = threading.RLock()

    def record_request_time(self, duration_ms: float):
        """Record the duration of a request."""
        with self.lock:
            self.request_times.append(duration_ms)
            self.performance_metrics['request_count'] += 1

    def record_error(self, error_type: str):
        """Record an error occurrence."""
        with self.lock:
            self.error_counts[error_type] += 1

    def record_conversation_event(self, event_type: str, user_id: Optional[uuid.UUID] = None):
        """Record a conversation-related event."""
        with self.lock:
            self.conversation_counts[event_type] += 1

    def record_message_event(self, event_type: str, user_id: Optional[uuid.UUID] = None):
        """Record a message-related event."""
        with self.lock:
            self.message_counts[event_type] += 1

    def get_avg_response_time(self) -> float:
        """Calculate the average response time."""
        with self.lock:
            if not self.request_times:
                return 0.0
            return sum(self.request_times) / len(self.request_times)

    def get_error_rate(self) -> float:
        """Calculate the error rate."""
        with self.lock:
            total_requests = self.performance_metrics['request_count']
            if total_requests == 0:
                return 0.0
            return sum(self.error_counts.values()) / total_requests

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all collected metrics."""
        with self.lock:
            return {
                'performance': {
                    'avg_response_time_ms': self.get_avg_response_time(),
                    'request_count': self.performance_metrics['request_count'],
                    'error_rate': self.get_error_rate(),
                    'requests_last_minute': self.get_requests_last_n_seconds(60),
                    'errors_last_minute': self.get_errors_last_n_seconds(60)
                },
                'conversations': dict(self.conversation_counts),
                'messages': dict(self.message_counts),
                'errors': dict(self.error_counts),
                'timestamp': datetime.utcnow().isoformat()
            }

    def get_requests_last_n_seconds(self, seconds: int) -> int:
        """Get the number of requests in the last N seconds."""
        # This is a simplified version - in a real implementation,
        # we would track timestamps of requests
        with self.lock:
            # Just return the count from the limited deque as an approximation
            return min(len(self.request_times), self.max_points)

    def get_errors_last_n_seconds(self, seconds: int) -> int:
        """Get the number of errors in the last N seconds."""
        # Simplified implementation
        with self.lock:
            return sum(min(count, 10) for count in list(self.error_counts.values())[-10:])  # Last few error types


class ConversationMetrics:
    """
    Specialized metrics collector for conversation-specific metrics.
    """

    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.active_conversations = set()
        self.conversation_start_times = {}
        self.lock = threading.RLock()

    def start_conversation_timer(self, conversation_id: uuid.UUID):
        """Start timing for a conversation."""
        with self.lock:
            self.conversation_start_times[conversation_id] = time.time()

    def end_conversation_timer(self, conversation_id: uuid.UUID) -> Optional[float]:
        """End timing for a conversation and return duration."""
        with self.lock:
            if conversation_id in self.conversation_start_times:
                start_time = self.conversation_start_times.pop(conversation_id)
                duration = time.time() - start_time
                return duration
            return None

    def track_active_conversation(self, conversation_id: uuid.UUID):
        """Track an active conversation."""
        with self.lock:
            self.active_conversations.add(conversation_id)

    def untrack_active_conversation(self, conversation_id: uuid.UUID):
        """Remove an active conversation from tracking."""
        with self.lock:
            self.active_conversations.discard(conversation_id)

    def get_active_conversation_count(self) -> int:
        """Get the number of currently active conversations."""
        with self.lock:
            return len(self.active_conversations)

    def get_conversation_duration_metrics(self) -> Dict[str, float]:
        """Get metrics about conversation durations."""
        # This would be populated as conversations are completed
        # For now, return a placeholder
        return {
            'avg_conversation_duration_seconds': 0.0,
            'longest_conversation_duration_seconds': 0.0,
            'shortest_conversation_duration_seconds': 0.0
        }

    def record_conversation_message_count(self, conversation_id: uuid.UUID, message_count: int):
        """Record the number of messages in a conversation."""
        # Could be used to track conversation length metrics
        pass


class MonitoringService:
    """
    Main service for monitoring conversation system metrics.
    """

    def __init__(self):
        self.system_metrics = MetricsCollector()
        self.conversation_metrics = ConversationMetrics()
        self.alert_thresholds = {
            'response_time_ms': 5000,  # 5 seconds
            'error_rate': 0.05,       # 5%
            'active_conversations': 1000  # 1000 conversations
        }

    def record_api_call(self, duration_ms: float, endpoint: str):
        """Record an API call with its duration."""
        self.system_metrics.record_request_time(duration_ms)
        self.system_metrics.record_conversation_event(f'api_call_{endpoint}')

    def record_error(self, error_type: str, severity: str = 'medium'):
        """Record an error occurrence."""
        self.system_metrics.record_error(error_type)

    def check_alerts(self) -> List[Dict[str, Any]]:
        """Check if any metrics have crossed alert thresholds."""
        alerts = []
        metrics = self.system_metrics.get_metrics_summary()

        perf = metrics['performance']

        if perf['avg_response_time_ms'] > self.alert_thresholds['response_time_ms']:
            alerts.append({
                'type': 'high_response_time',
                'severity': 'high',
                'message': f"Average response time ({perf['avg_response_time_ms']}ms) exceeds threshold ({self.alert_thresholds['response_time_ms']}ms)",
                'value': perf['avg_response_time_ms'],
                'threshold': self.alert_thresholds['response_time_ms']
            })

        if perf['error_rate'] > self.alert_thresholds['error_rate']:
            alerts.append({
                'type': 'high_error_rate',
                'severity': 'high',
                'message': f"Error rate ({perf['error_rate']:.2%}) exceeds threshold ({self.alert_thresholds['error_rate']:.2%})",
                'value': perf['error_rate'],
                'threshold': self.alert_thresholds['error_rate']
            })

        if self.conversation_metrics.get_active_conversation_count() > self.alert_thresholds['active_conversations']:
            alerts.append({
                'type': 'high_concurrency',
                'severity': 'medium',
                'message': f"Active conversations ({self.conversation_metrics.get_active_conversation_count()}) exceeds threshold ({self.alert_thresholds['active_conversations']})",
                'value': self.conversation_metrics.get_active_conversation_count(),
                'threshold': self.alert_thresholds['active_conversations']
            })

        return alerts

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health."""
        return {
            'system_metrics': self.system_metrics.get_metrics_summary(),
            'conversation_metrics': {
                'active_conversations': self.conversation_metrics.get_active_conversation_count(),
                'conversation_durations': self.conversation_metrics.get_conversation_duration_metrics()
            },
            'alerts': self.check_alerts(),
            'timestamp': datetime.utcnow().isoformat()
        }

    def get_performance_report(self) -> Dict[str, Any]:
        """Get a detailed performance report."""
        metrics = self.system_metrics.get_metrics_summary()

        return {
            'summary': {
                'period': 'last_5_minutes',  # Would be configurable in real implementation
                'start_time': (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                'end_time': datetime.utcnow().isoformat()
            },
            'performance_metrics': metrics['performance'],
            'top_errors': sorted(
                [(k, v) for k, v in metrics['errors'].items()],
                key=lambda x: x[1],
                reverse=True
            )[:10],
            'top_conversation_events': sorted(
                [(k, v) for k, v in metrics['conversations'].items()],
                key=lambda x: x[1],
                reverse=True
            )[:10],
            'timestamp': datetime.utcnow().isoformat()
        }


class PerformanceMonitor:
    """
    Monitor performance metrics specifically for AI responses and conversation operations.
    """

    def __init__(self):
        self.response_times = defaultdict(list)
        self.error_counts = defaultdict(int)
        self.token_usage = defaultdict(int)
        self.lock = threading.RLock()

    def record_ai_response_time(self, duration_ms: float, model_name: str = "default"):
        """Record the time taken for an AI response."""
        with self.lock:
            self.response_times[model_name].append({
                'duration_ms': duration_ms,
                'timestamp': datetime.utcnow()
            })

            # Keep only the last 1000 measurements
            if len(self.response_times[model_name]) > 1000:
                self.response_times[model_name] = self.response_times[model_name][-1000:]

    def record_ai_error(self, error_type: str, model_name: str = "default"):
        """Record an AI-related error."""
        with self.lock:
            self.error_counts[f"{model_name}:{error_type}"] += 1

    def record_token_usage(self, tokens: int, model_name: str = "default", user_id: Optional[uuid.UUID] = None):
        """Record token usage for an AI request."""
        with self.lock:
            key = f"{model_name}:{user_id}" if user_id else model_name
            self.token_usage[key] += tokens

    def get_ai_performance_metrics(self, model_name: str = "default", hours: int = 1) -> Dict[str, Any]:
        """Get performance metrics for AI responses."""
        with self.lock:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)

            # Filter response times to only include recent measurements
            recent_responses = [
                r for r in self.response_times.get(model_name, [])
                if r['timestamp'] >= cutoff_time
            ]

            if not recent_responses:
                return {
                    'model': model_name,
                    'avg_response_time_ms': 0.0,
                    'min_response_time_ms': 0.0,
                    'max_response_time_ms': 0.0,
                    'total_requests': 0,
                    'error_rate': 0.0,
                    'tokens_used': 0
                }

            response_times = [r['duration_ms'] for r in recent_responses]
            total_requests = len(response_times)

            # Calculate error rate for this model
            total_errors = sum(1 for k, v in self.error_counts.items() if k.startswith(model_name))
            error_rate = total_errors / total_requests if total_requests > 0 else 0

            # Calculate token usage for this model
            token_key_prefix = f"{model_name}:"
            tokens_used = sum(v for k, v in self.token_usage.items() if k.startswith(token_key_prefix))

            return {
                'model': model_name,
                'avg_response_time_ms': sum(response_times) / len(response_times),
                'min_response_time_ms': min(response_times),
                'max_response_time_ms': max(response_times),
                'total_requests': total_requests,
                'error_rate': error_rate,
                'tokens_used': tokens_used,
                'period_hours': hours
            }


# Global monitoring service instance
monitoring_service = MonitoringService()

# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def record_api_call(duration_ms: float, endpoint: str):
    """Convenience function to record an API call."""
    monitoring_service.record_api_call(duration_ms, endpoint)


def record_error(error_type: str, severity: str = 'medium'):
    """Convenience function to record an error."""
    monitoring_service.record_error(error_type, severity)


def get_system_health():
    """Convenience function to get system health."""
    return monitoring_service.get_system_health()


def get_performance_report():
    """Convenience function to get performance report."""
    return monitoring_service.get_performance_report()


def check_alerts():
    """Convenience function to check for alerts."""
    return monitoring_service.check_alerts()


# Add performance monitoring for AI responses
def record_ai_response_time(duration_ms: float, model_name: str = "default"):
    """Convenience function to record AI response time."""
    from utils.monitoring import performance_monitor
    performance_monitor.record_ai_response_time(duration_ms, model_name)


def record_ai_error(error_type: str, model_name: str = "default"):
    """Convenience function to record AI error."""
    from utils.monitoring import performance_monitor
    performance_monitor.record_ai_error(error_type, model_name)


def record_token_usage(tokens: int, model_name: str = "default", user_id: Optional[uuid.UUID] = None):
    """Convenience function to record token usage."""
    from utils.monitoring import performance_monitor
    performance_monitor.record_token_usage(tokens, model_name, user_id)


def get_ai_performance_metrics(model_name: str = "default", hours: int = 1) -> Dict[str, Any]:
    """Convenience function to get AI performance metrics."""
    from utils.monitoring import performance_monitor
    return performance_monitor.get_ai_performance_metrics(model_name, hours)