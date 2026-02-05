from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime
import asyncio
import hashlib
from dataclasses import dataclass


@dataclass
class ShardInfo:
    """Information about a shard for distributed storage."""
    shard_id: str
    server_url: str
    region: str
    capacity: int
    current_load: int


class DistributedConversationService:
    """
    Service for handling distributed conversation storage and retrieval across multiple shards/servers.
    """

    def __init__(self):
        # In a real implementation, this would connect to a service discovery mechanism
        # For this implementation, we'll simulate with a simple sharding approach
        self.shards = [
            ShardInfo("shard-1", "http://shard1.example.com", "us-east-1", 10000, 0),
            ShardInfo("shard-2", "http://shard2.example.com", "us-west-1", 10000, 0),
            ShardInfo("shard-3", "http://shard3.example.com", "eu-central-1", 10000, 0),
        ]
        self.current_shard_index = 0

    def get_shard_for_conversation(self, conversation_id: uuid.UUID) -> ShardInfo:
        """
        Determine which shard should handle a specific conversation.

        Args:
            conversation_id: ID of the conversation

        Returns:
            ShardInfo for the appropriate shard
        """
        # Simple hash-based sharding
        hash_value = int(hashlib.sha256(str(conversation_id).encode()).hexdigest(), 16)
        shard_index = hash_value % len(self.shards)
        return self.shards[shard_index]

    def get_shard_for_user(self, user_id: uuid.UUID) -> ShardInfo:
        """
        Determine which shard should handle conversations for a specific user.

        Args:
            user_id: ID of the user

        Returns:
            ShardInfo for the appropriate shard
        """
        # Hash-based sharding by user ID to ensure all conversations for a user are on the same shard
        hash_value = int(hashlib.sha256(str(user_id).encode()).hexdigest(), 16)
        shard_index = hash_value % len(self.shards)
        return self.shards[shard_index]

    async def store_conversation_distributed(self, conversation_data: Dict[str, Any]) -> bool:
        """
        Store a conversation in the distributed system.

        Args:
            conversation_data: Dictionary containing conversation data

        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract user_id to determine the correct shard
            user_id = uuid.UUID(conversation_data.get("user_id", ""))
            shard = self.get_shard_for_user(user_id)

            # Simulate storing conversation on the shard
            # In a real implementation, this would make an HTTP request to the shard
            print(f"Storing conversation on {shard.shard_id} at {shard.server_url}")

            # Update shard load
            shard.current_load += 1

            return True
        except Exception as e:
            print(f"Distributed storage error: {str(e)}")
            return False

    async def retrieve_conversation_distributed(self, conversation_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """
        Retrieve a conversation from the distributed system.

        Args:
            conversation_id: ID of the conversation to retrieve

        Returns:
            Conversation data dictionary or None if not found
        """
        try:
            # Determine which shard has this conversation
            shard = self.get_shard_for_conversation(conversation_id)

            # Simulate retrieving conversation from the shard
            # In a real implementation, this would make an HTTP request to the shard
            print(f"Retrieving conversation from {shard.shard_id} at {shard.server_url}")

            # For simulation, return a placeholder
            return {
                "id": str(conversation_id),
                "shard": shard.shard_id,
                "status": "found"
            }
        except Exception as e:
            print(f"Distributed retrieval error: {str(e)}")
            return None

    async def store_message_distributed(self, conversation_id: uuid.UUID, message_data: Dict[str, Any]) -> bool:
        """
        Store a message in the distributed system, associated with a conversation.

        Args:
            conversation_id: ID of the conversation
            message_data: Dictionary containing message data

        Returns:
            True if successful, False otherwise
        """
        try:
            # Route to the correct shard based on conversation ID
            shard = self.get_shard_for_conversation(conversation_id)

            # Simulate storing message on the shard
            print(f"Storing message for conversation {conversation_id} on {shard.shard_id}")

            # Update shard load
            shard.current_load += 1

            return True
        except Exception as e:
            print(f"Distributed message storage error: {str(e)}")
            return False

    def get_conversation_shard_location(self, conversation_id: uuid.UUID) -> str:
        """
        Get the shard location for a specific conversation.

        Args:
            conversation_id: ID of the conversation

        Returns:
            String identifier of the shard
        """
        shard = self.get_shard_for_conversation(conversation_id)
        return shard.shard_id

    def rebalance_shards(self) -> Dict[str, Any]:
        """
        Rebalance conversations across shards based on load.

        Returns:
            Dictionary with rebalancing results
        """
        # Calculate average load
        total_load = sum(shard.current_load for shard in self.shards)
        avg_load = total_load / len(self.shards) if len(self.shards) > 0 else 0

        # Identify overloaded and underloaded shards
        overloaded = [shard for shard in self.shards if shard.current_load > avg_load * 1.2]
        underloaded = [shard for shard in self.shards if shard.current_load < avg_load * 0.8]

        rebalance_actions = []
        for over_shard in overloaded:
            for under_shard in underloaded:
                if over_shard.current_load > under_shard.current_load:
                    # Simulate moving some conversations from over_shard to under_shard
                    move_count = min(
                        over_shard.current_load - int(avg_load),
                        int(avg_load) - under_shard.current_load
                    )

                    if move_count > 0:
                        over_shard.current_load -= move_count
                        under_shard.current_load += move_count
                        rebalance_actions.append({
                            "from_shard": over_shard.shard_id,
                            "to_shard": under_shard.shard_id,
                            "moved_conversations": move_count
                        })

        return {
            "actions_taken": rebalance_actions,
            "shard_status": [
                {
                    "shard_id": shard.shard_id,
                    "current_load": shard.current_load,
                    "capacity": shard.capacity,
                    "utilization_percent": (shard.current_load / shard.capacity) * 100
                }
                for shard in self.shards
            ]
        }

    def get_system_health(self) -> Dict[str, Any]:
        """
        Get health status of the distributed system.

        Returns:
            Dictionary with system health information
        """
        total_capacity = sum(shard.capacity for shard in self.shards)
        total_current_load = sum(shard.current_load for shard in self.shards)
        utilization = (total_current_load / total_capacity) * 100 if total_capacity > 0 else 0

        shard_health = []
        for shard in self.shards:
            shard_utilization = (shard.current_load / shard.capacity) * 100 if shard.capacity > 0 else 0
            status = "healthy" if shard_utilization < 80 else "warning" if shard_utilization < 95 else "critical"

            shard_health.append({
                "shard_id": shard.shard_id,
                "status": status,
                "utilization_percent": round(shard_utilization, 2),
                "current_load": shard.current_load,
                "capacity": shard.capacity,
                "region": shard.region
            })

        return {
            "overall_utilization_percent": round(utilization, 2),
            "total_shards": len(self.shards),
            "healthy_shards": len([sh for sh in shard_health if sh["status"] == "healthy"]),
            "shard_details": shard_health,
            "timestamp": datetime.utcnow().isoformat()
        }


# Singleton instance
distributed_service = DistributedConversationService()