"""
Todo Agent Implementation
Uses OpenAI Agents SDK to create an AI agent that manages todos via MCP tools
"""
from openai import OpenAI
from typing import Dict, Any, List, Optional
import uuid
from sqlmodel import Session

from apps.backend.src.agents.config import agent_config, tool_config
from apps.backend.src.mcp_server.main import mcp_todo_server


class TodoAgent:
    """
    Todo Agent that uses OpenAI Agents SDK to manage todos via MCP tools.
    The agent is configured with system instructions and MCP tools for all operations.
    """

    def __init__(self):
        # Initialize OpenAI client
        self.client = OpenAI()

        # Create the agent with instructions and tools
        self.agent = self.client.beta.agents.create(
            name=agent_config.name,
            instructions=agent_config.instructions,
            tools=self._get_tools(),
            model=agent_config.model
        )

    def _get_tools(self) -> List[Dict[str, Any]]:
        """
        Get the list of available tools for the agent.
        These correspond to the MCP tools for todo operations.
        """
        return [
            {"type": "function", "function": tool_config.add_task},
            {"type": "function", "function": tool_config.list_tasks},
            {"type": "function", "function": tool_config.update_task},
            {"type": "function", "function": tool_config.complete_task},
            {"type": "function", "function": tool_config.delete_task},
        ]

    def get_agent_id(self) -> str:
        """
        Get the ID of the created agent.
        """
        return self.agent.id

    def create_thread(self):
        """
        Create a new thread for a conversation.
        """
        return self.client.beta.threads.create()

    def add_message_to_thread(self, thread_id: str, user_id: str, message: str):
        """
        Add a user message to the thread.
        """
        return self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message
        )

    def run_agent(self, thread_id: str, user_id: str):
        """
        Run the agent on the thread to process the user's message.
        This will execute any required tools and return the agent's response.
        """
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            agent_id=self.agent.id,
            # Pass additional instructions if needed
            additional_instructions=f"The user_id for this request is {user_id}. "
                                  f"Always ensure operations are performed for this user only."
        )

        # Wait for the run to complete
        return self._wait_for_run_completion(thread_id, run.id)

    def run_agent_with_context(self, thread_id: str, user_id: str, additional_context: str = ""):
        """
        Run the agent on the thread with additional context.
        """
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            agent_id=self.agent.id,
            # Pass additional instructions with context
            additional_instructions=f"The user_id for this request is {user_id}. "
                                  f"Always ensure operations are performed for this user only. "
                                  f"{additional_context}"
        )

        # Wait for the run to complete
        return self._wait_for_run_completion(thread_id, run.id)

    def _wait_for_run_completion(self, thread_id: str, run_id: str):
        """
        Wait for a run to complete, handling any required actions (tool calls).
        """
        import time

        while True:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )

            if run.status == "completed":
                break
            elif run.status == "requires_action":
                # Handle tool calls by connecting to the MCP server
                tool_outputs = self._handle_tool_calls(run.required_action.submit_tool_outputs.tool_calls)

                # Submit the tool outputs
                self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run_id,
                    tool_outputs=tool_outputs
                )
            elif run.status in ["failed", "cancelled", "expired"]:
                raise Exception(f"Run failed with status: {run.status}")

            time.sleep(0.5)  # Poll every 0.5 seconds

        # Retrieve the messages from the thread
        messages = self.client.beta.threads.messages.list(
            thread_id=thread_id,
            order="asc"  # Oldest first
        )

        # Get the latest assistant message
        assistant_messages = [msg for msg in messages.data if msg.role == "assistant"]
        if assistant_messages:
            latest_message = assistant_messages[-1]
            # Extract text content
            text_contents = [content.text.value for content in latest_message.content if content.type == "text"]
            return {
                "response_text": "\n".join(text_contents) if text_contents else "",
                "thread_id": thread_id
            }

        return {
            "response_text": "No response from assistant.",
            "thread_id": thread_id
        }

    def _handle_tool_calls(self, tool_calls):
        """
        Handle the tool calls required by the agent.
        Connect to the MCP server to execute tools.
        """
        import json

        tool_outputs = []

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            try:
                # Safely parse the arguments
                function_args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                # If JSON parsing fails, return an error
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": json.dumps({
                        "success": False,
                        "error": f"Invalid JSON arguments for tool {function_name}"
                    })
                })
                continue

            # Execute the tool function using the MCP server
            try:
                # Get the server instance
                server = mcp_todo_server.get_server()

                # Get the tool from the server
                if function_name not in server._tools:
                    result = {
                        "success": False,
                        "error": f"Tool '{function_name}' not found"
                    }
                else:
                    # Execute the tool
                    tool = server._tools[function_name]

                    # For now, we'll simulate the tool execution
                    # In a real implementation, this would call the actual MCP tool
                    if function_name == "add_task":
                        # Validate user_id format
                        try:
                            user_uuid = uuid.UUID(function_args["user_id"])
                        except ValueError:
                            result = {
                                "success": False,
                                "error": "Invalid user_id format"
                            }
                        else:
                            # In a real implementation, this would call the actual tool
                            result = {
                                "success": True,
                                "message": f"Task '{function_args.get('title', 'Untitled')}' added successfully",
                                "task": {
                                    "id": str(uuid.uuid4()),  # Simulated task ID
                                    "title": function_args.get("title"),
                                    "description": function_args.get("description", ""),
                                    "is_completed": False
                                }
                            }

                    elif function_name == "list_tasks":
                        # Validate user_id format
                        try:
                            user_uuid = uuid.UUID(function_args["user_id"])
                        except ValueError:
                            result = {
                                "success": False,
                                "error": "Invalid user_id format"
                            }
                        else:
                            # In a real implementation, this would call the actual tool
                            result = {
                                "success": True,
                                "message": "Retrieved 2 tasks for user",
                                "tasks": [
                                    {
                                        "id": str(uuid.uuid4()),
                                        "title": "Sample Task 1",
                                        "description": "Sample description",
                                        "is_completed": False
                                    },
                                    {
                                        "id": str(uuid.uuid4()),
                                        "title": "Sample Task 2",
                                        "description": "Another sample task",
                                        "is_completed": True
                                    }
                                ]
                            }

                    elif function_name == "update_task":
                        # Validate user_id and task_id formats
                        try:
                            user_uuid = uuid.UUID(function_args["user_id"])
                            task_uuid = uuid.UUID(function_args["task_id"])
                        except ValueError:
                            result = {
                                "success": False,
                                "error": "Invalid user_id or task_id format"
                            }
                        else:
                            # In a real implementation, this would call the actual tool
                            result = {
                                "success": True,
                                "message": "Task updated successfully",
                                "task": {
                                    "id": str(task_uuid),
                                    "title": function_args.get("title", "Updated Task"),
                                    "description": function_args.get("description", ""),
                                    "is_completed": function_args.get("is_completed", False)
                                }
                            }

                    elif function_name == "complete_task":
                        # Validate user_id and task_id formats
                        try:
                            user_uuid = uuid.UUID(function_args["user_id"])
                            task_uuid = uuid.UUID(function_args["task_id"])
                        except ValueError:
                            result = {
                                "success": False,
                                "error": "Invalid user_id or task_id format"
                            }
                        else:
                            status = "completed" if function_args.get("is_completed", True) else "marked as incomplete"
                            # In a real implementation, this would call the actual tool
                            result = {
                                "success": True,
                                "message": f"Task has been {status}",
                                "task": {
                                    "id": str(task_uuid),
                                    "title": "Sample Task",
                                    "description": "Sample description",
                                    "is_completed": function_args.get("is_completed", True)
                                }
                            }

                    elif function_name == "delete_task":
                        # Validate user_id and task_id formats
                        try:
                            user_uuid = uuid.UUID(function_args["user_id"])
                            task_uuid = uuid.UUID(function_args["task_id"])
                        except ValueError:
                            result = {
                                "success": False,
                                "error": "Invalid user_id or task_id format"
                            }
                        else:
                            # In a real implementation, this would call the actual tool
                            result = {
                                "success": True,
                                "message": "Task deleted successfully"
                            }

                    else:
                        # Unknown tool
                        result = {
                            "success": False,
                            "error": f"Unknown tool: {function_name}"
                        }

            except Exception as e:
                result = {
                    "success": False,
                    "error": f"Error executing {function_name}: {str(e)}"
                }

            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps(result)
            })

        return tool_outputs


# Global agent instance
todo_agent = TodoAgent()