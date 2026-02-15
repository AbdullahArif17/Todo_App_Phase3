"""
Performance benchmarks for conversation optimization features.
"""
import time
import asyncio
import pytest
from sqlmodel import Session
from database import engine
from models.user import User
from models.conversation import Conversation
from models.message import Message
from services.chat_service import ChatService
from utils.ai_utils import intelligent_conversation_truncation, truncate_conversation_history
from utils.metrics import record_response_time, get_current_metrics
import uuid
from datetime import datetime, timedelta
from typing import List
import statistics


class PerformanceBenchmarkSuite:
    """
    Suite of performance benchmarks for conversation optimization features.
    """

    def __init__(self):
        self.chat_service = ChatService()
        self.results = {}

    def benchmark_message_creation_performance(self, num_messages: int = 1000) -> dict:
        """
        Benchmark the performance of creating messages in bulk vs individually.

        Args:
            num_messages: Number of messages to create for the benchmark

        Returns:
            Dictionary with performance metrics
        """
        print(f"Benchmarking message creation for {num_messages} messages...")

        # Create a test user and conversation
        with Session(engine) as session:
            # Create test user
            test_user = User(
                id=uuid.uuid4(),
                email=f"perf_test_{uuid.uuid4()}@example.com",
                hashed_password="hashed_password",
                full_name="Performance Test User"
            )
            session.add(test_user)
            session.commit()
            session.refresh(test_user)

            # Create test conversation
            test_conversation = self.chat_service.create_conversation(
                session=session,
                user_id=test_user.id,
                title="Performance Test Conversation"
            )

            # Test individual message creation
            start_time = time.time()
            for i in range(num_messages):
                self.chat_service.create_message(
                    session=session,
                    conversation_id=test_conversation.id,
                    role="user",
                    content=f"Performance test message {i}"
                )
            individual_time = time.time() - start_time

            # Create another conversation for bulk test
            test_conversation_2 = self.chat_service.create_conversation(
                session=session,
                user_id=test_user.id,
                title="Performance Test Conversation 2"
            )

            # Prepare bulk message data
            bulk_messages_data = [
                {"role": "user", "content": f"Bulk test message {i}"} for i in range(num_messages)
            ]

            # Test bulk message creation
            start_time = time.time()
            self.chat_service.create_bulk_messages(
                session=session,
                conversation_id=test_conversation_2.id,
                messages_data=bulk_messages_data
            )
            bulk_time = time.time() - start_time

            # Calculate metrics
            individual_rate = num_messages / individual_time if individual_time > 0 else 0
            bulk_rate = num_messages / bulk_time if bulk_time > 0 else 0

            results = {
                "individual_creation_time": individual_time,
                "bulk_creation_time": bulk_time,
                "num_messages": num_messages,
                "individual_rate": individual_rate,  # messages per second
                "bulk_rate": bulk_rate,  # messages per second
                "bulk_improvement_factor": individual_rate / bulk_rate if bulk_rate > 0 else float('inf'),
                "timestamp": datetime.utcnow().isoformat()
            }

            print(f"Individual creation: {individual_time:.2f}s ({individual_rate:.2f} msg/s)")
            print(f"Bulk creation: {bulk_time:.2f}s ({bulk_rate:.2f} msg/s)")
            print(f"Bulk improvement factor: {results['bulk_improvement_factor']:.2f}x")

            return results

    def benchmark_conversation_truncation_algorithms(self, num_messages: int = 500) -> dict:
        """
        Benchmark different conversation truncation algorithms.

        Args:
            num_messages: Number of messages to simulate in the conversation

        Returns:
            Dictionary with performance metrics for each algorithm
        """
        print(f"Benchmarking truncation algorithms with {num_messages} messages...")

        # Create mock messages
        from models.message import Message
        import random
        from datetime import datetime, timedelta

        mock_messages = []
        base_time = datetime.utcnow() - timedelta(days=7)  # One week of messages

        for i in range(num_messages):
            msg = Message(
                id=uuid.uuid4(),
                conversation_id=uuid.uuid4(),
                role="user" if i % 2 == 0 else "assistant",
                content=f"This is a sample message {i} with some content that varies in length. " +
                       f"The message contains important information that might be relevant for context. " +
                       f"{'Additional content to make the message longer ' * random.randint(1, 3)}",
                timestamp=base_time + timedelta(minutes=i)
            )
            mock_messages.append(msg)

        # Test basic truncation
        start_time = time.time()
        basic_result = truncate_conversation_history(mock_messages, max_tokens=1000)
        basic_time = time.time() - start_time

        # Test intelligent truncation
        start_time = time.time()
        intelligent_result = intelligent_conversation_truncation(
            mock_messages,
            max_tokens=1000,
            preserve_recent=10,
            preserve_first=5
        )
        intelligent_time = time.time() - start_time

        results = {
            "basic_truncation": {
                "time": basic_time,
                "result_size": len(basic_result),
                "tokens_used": sum(len(msg.content) for msg in basic_result) // 4
            },
            "intelligent_truncation": {
                "time": intelligent_time,
                "result_size": len(intelligent_result),
                "tokens_used": sum(len(msg.content) for msg in intelligent_result) // 4
            },
            "input_size": num_messages,
            "timestamp": datetime.utcnow().isoformat()
        }

        print(f"Basic truncation: {basic_time:.4f}s, output: {len(basic_result)} messages")
        print(f"Intelligent truncation: {intelligent_time:.4f}s, output: {len(intelligent_result)} messages")

        return results

    def benchmark_conversation_loading_performance(self, num_conversations: int = 50, messages_per_conversation: int = 20) -> dict:
        """
        Benchmark performance of loading conversations with varying message counts.

        Args:
            num_conversations: Number of conversations to create and test
            messages_per_conversation: Number of messages per conversation

        Returns:
            Dictionary with performance metrics
        """
        print(f"Benchmarking conversation loading with {num_conversations} conversations and {messages_per_conversation} messages each...")

        with Session(engine) as session:
            # Create test user
            test_user = User(
                id=uuid.uuid4(),
                email=f"perf_load_test_{uuid.uuid4()}@example.com",
                hashed_password="hashed_password",
                full_name="Performance Load Test User"
            )
            session.add(test_user)
            session.commit()
            session.refresh(test_user)

            # Create multiple conversations with messages
            conversation_ids = []
            for i in range(num_conversations):
                conv = self.chat_service.create_conversation(
                    session=session,
                    user_id=test_user.id,
                    title=f"Load Test Conversation {i}"
                )
                conversation_ids.append(conv.id)

                # Add messages to each conversation
                for j in range(messages_per_conversation):
                    self.chat_service.create_message(
                        session=session,
                        conversation_id=conv.id,
                        role="user" if j % 2 == 0 else "assistant",
                        content=f"Load test message {j} in conversation {i}"
                    )

            # Benchmark loading conversations one by one
            start_time = time.time()
            for conv_id in conversation_ids:
                # Load messages for each conversation
                messages = self.chat_service.get_conversation_messages(
                    session=session,
                    conversation_id=conv_id,
                    user_id=test_user.id,
                    limit=messages_per_conversation
                )
            loading_time = time.time() - start_time

            # Benchmark loading with pagination
            start_time = time.time()
            for conv_id in conversation_ids:
                # Load messages in chunks
                offset = 0
                chunk_size = 10
                all_messages = []
                while True:
                    chunk = self.chat_service.get_conversation_messages(
                        session=session,
                        conversation_id=conv_id,
                        user_id=test_user.id,
                        limit=chunk_size,
                        offset=offset
                    )
                    all_messages.extend(chunk)
                    if len(chunk) < chunk_size:
                        break
                    offset += chunk_size

            paginated_loading_time = time.time() - start_time

            results = {
                "direct_loading_time": loading_time,
                "paginated_loading_time": paginated_loading_time,
                "num_conversations": num_conversations,
                "messages_per_conversation": messages_per_conversation,
                "total_messages": num_conversations * messages_per_conversation,
                "timestamp": datetime.utcnow().isoformat()
            }

            print(f"Direct loading: {loading_time:.2f}s for {num_conversations} conversations")
            print(f"Paginated loading: {paginated_loading_time:.2f}s for {num_conversations} conversations")

            return results

    def benchmark_search_performance(self, num_conversations: int = 100, messages_per_conversation: int = 50) -> dict:
        """
        Benchmark performance of conversation search functionality.

        Args:
            num_conversations: Number of conversations to create
            messages_per_conversation: Number of messages per conversation

        Returns:
            Dictionary with search performance metrics
        """
        print(f"Benchmarking search performance with {num_conversations} conversations...")

        with Session(engine) as session:
            # Create test user
            test_user = User(
                id=uuid.uuid4(),
                email=f"perf_search_test_{uuid.uuid4()}@example.com",
                hashed_password="hashed_password",
                full_name="Performance Search Test User"
            )
            session.add(test_user)
            session.commit()
            session.refresh(test_user)

            # Create conversations with searchable content
            target_conversations = []
            for i in range(num_conversations):
                conv = self.chat_service.create_conversation(
                    session=session,
                    user_id=test_user.id,
                    title=f"Search Test Conversation {i}"
                )

                # Add messages, including some with target search terms
                for j in range(messages_per_conversation):
                    if j % 10 == 0:  # Every 10th message contains search term
                        content = f"This is a special message about groceries and shopping {j} in conversation {i}"
                        target_conversations.append(conv.id)
                    else:
                        content = f"Regular test message {j} in conversation {i}"

                    self.chat_service.create_message(
                        session=session,
                        conversation_id=conv.id,
                        role="user" if j % 2 == 0 else "assistant",
                        content=content
                    )

            # Benchmark search performance
            search_terms = ["groceries", "shopping", "special"]
            search_times = []

            for term in search_terms:
                start_time = time.time()
                results = self.chat_service.search_conversations(
                    session=session,
                    user_id=test_user.id,
                    search_term=term,
                    limit=50,
                    offset=0
                )
                search_time = time.time() - start_time
                search_times.append(search_time)

                print(f"Search for '{term}': {search_time:.4f}s, found {len(results)} conversations")

            avg_search_time = statistics.mean(search_times) if search_times else 0
            median_search_time = statistics.median(search_times) if search_times else 0

            results = {
                "average_search_time": avg_search_time,
                "median_search_time": median_search_time,
                "max_search_time": max(search_times) if search_times else 0,
                "search_times": search_times,
                "num_searches_performed": len(search_terms),
                "num_conversations_searched": num_conversations,
                "messages_per_conversation": messages_per_conversation,
                "timestamp": datetime.utcnow().isoformat()
            }

            return results

    def run_all_benchmarks(self) -> dict:
        """
        Run all performance benchmarks and return comprehensive results.

        Returns:
            Dictionary with all benchmark results
        """
        print("Starting comprehensive performance benchmark suite...")

        results = {
            "benchmark_suite": "Conversation Optimization Performance",
            "timestamp": datetime.utcnow().isoformat(),
            "benchmarks": {}
        }

        # Run message creation benchmark
        print("\n1. Running message creation benchmark...")
        results["benchmarks"]["message_creation"] = self.benchmark_message_creation_performance(500)

        # Run truncation algorithm benchmark
        print("\n2. Running truncation algorithm benchmark...")
        results["benchmarks"]["truncation_algorithms"] = self.benchmark_conversation_truncation_algorithms(300)

        # Run conversation loading benchmark
        print("\n3. Running conversation loading benchmark...")
        results["benchmarks"]["conversation_loading"] = self.benchmark_conversation_loading_performance(20, 30)

        # Run search performance benchmark
        print("\n4. Running search performance benchmark...")
        results["benchmarks"]["search_performance"] = self.benchmark_search_performance(50, 25)

        # Add system metrics
        try:
            metrics = get_current_metrics()
            results["system_metrics"] = metrics
        except Exception as e:
            print(f"Could not retrieve system metrics: {e}")
            results["system_metrics"] = {"error": str(e)}

        print("\nBenchmark suite completed!")
        return results


def run_performance_benchmarks():
    """
    Main function to run all performance benchmarks.
    """
    benchmark_suite = PerformanceBenchmarkSuite()
    results = benchmark_suite.run_all_benchmarks()

    # Print summary
    print("\n" + "="*60)
    print("PERFORMANCE BENCHMARK SUMMARY")
    print("="*60)

    if "message_creation" in results["benchmarks"]:
        mc = results["benchmarks"]["message_creation"]
        print(f"Message Creation:")
        print(f"  - Individual rate: {mc['individual_rate']:.2f} msg/s")
        print(f"  - Bulk rate: {mc['bulk_rate']:.2f} msg/s")
        print(f"  - Bulk improvement: {mc['bulk_improvement_factor']:.2f}x")

    if "truncation_algorithms" in results["benchmarks"]:
        ta = results["benchmarks"]["truncation_algorithms"]
        print(f"\nTruncation Algorithms:")
        print(f"  - Basic truncation: {ta['basic_truncation']['time']:.4f}s")
        print(f"  - Intelligent truncation: {ta['intelligent_truncation']['time']:.4f}s")

    if "search_performance" in results["benchmarks"]:
        sp = results["benchmarks"]["search_performance"]
        print(f"\nSearch Performance:")
        print(f"  - Average search time: {sp['average_search_time']:.4f}s")
        print(f"  - Median search time: {sp['median_search_time']:.4f}s")

    print("="*60)

    return results


if __name__ == "__main__":
    run_performance_benchmarks()