# API Contract: Chat Endpoint for Todo Management

## Overview
REST API contract for the stateless chat endpoint that enables conversational todo management through an AI agent using MCP tools.

## Base URL
```
https://{host}:{port}/api
```

## Authentication
All endpoints require JWT Bearer token authentication in the `Authorization` header:
```
Authorization: Bearer {jwt_token}
```

## Endpoints

### POST /{user_id}/chat
Process a natural language message through the AI agent for todo management.

#### Request
**Headers:**
- `Authorization: Bearer {token}` (required)
- `Content-Type: application/json` (required)

**Path Parameters:**
- `user_id` (string, UUID format): The ID of the user making the request. Must match the authenticated user.

**Request Body:**
```json
{
  "message": "string (required, 1-5000 characters)",
  "conversation_id": "string (optional, UUID format) - if omitted, creates a new conversation"
}
```

**Example Request:**
```json
{
  "message": "Add a task to buy groceries",
  "conversation_id": null
}
```

#### Response
**Success Response (200 OK):**
```json
{
  "conversation_id": "string (UUID format)",
  "response": "string (AI-generated response)",
  "message_id": "string (UUID format of the assistant's response message)"
}
```

**Example Success Response:**
```json
{
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "response": "I've added the task 'buy groceries' to your list.",
  "message_id": "987e6543-e21b-32d1-a654-426614174999"
}
```

**Error Responses:**

400 Bad Request:
```json
{
  "detail": "Message content cannot be empty"
}
```

401 Unauthorized:
```json
{
  "detail": "Not authenticated"
}
```

403 Forbidden:
```json
{
  "detail": "Not authorized to access this user's chat"
}
```

404 Not Found:
```json
{
  "detail": "Conversation not found"
}
```

429 Too Many Requests:
```json
{
  "detail": "Rate limit exceeded for AI service. Please try again later."
}
```

500 Internal Server Error:
```json
{
  "detail": "Internal server error occurred"
}
```

#### Business Logic
1. If `conversation_id` is null or not provided, create a new conversation
2. Validate that the authenticated user matches the `user_id` in the path
3. Validate message length (1-5000 characters)
4. Persist the user's message to the database before executing the AI agent
5. Load conversation history from the database
6. Execute the AI agent with the conversation context and new message
7. Persist the AI assistant's response to the database after processing
8. Return conversation ID and AI response

---

### GET /{user_id}/conversations
Retrieve a paginated list of user's conversations.

#### Request
**Headers:**
- `Authorization: Bearer {token}` (required)

**Path Parameters:**
- `user_id` (string, UUID format): The ID of the user. Must match the authenticated user.

**Query Parameters:**
- `skip` (integer, optional): Number of conversations to skip (for pagination, default: 0)
- `limit` (integer, optional): Maximum number of conversations to return (default: 20, max: 100)

#### Response
**Success Response (200 OK):**
```json
[
  {
    "id": "string (UUID format)",
    "title": "string",
    "created_at": "string (ISO 8601 datetime)",
    "updated_at": "string (ISO 8601 datetime)",
    "last_activity": "string (ISO 8601 datetime)",
    "message_count": "integer",
    "is_archived": "boolean"
  }
]
```

**Example Success Response:**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Grocery Shopping Plans",
    "created_at": "2023-10-20T10:00:00Z",
    "updated_at": "2023-10-20T11:30:00Z",
    "last_activity": "2023-10-20T11:30:00Z",
    "message_count": 5,
    "is_archived": false
  }
]
```

---

### GET /{user_id}/conversations/{conversation_id}/messages
Retrieve paginated messages from a specific conversation.

#### Request
**Headers:**
- `Authorization: Bearer {token}` (required)

**Path Parameters:**
- `user_id` (string, UUID format): The ID of the user. Must match the authenticated user.
- `conversation_id` (string, UUID format): The ID of the conversation to retrieve messages from.

**Query Parameters:**
- `skip` (integer, optional): Number of messages to skip (for pagination, default: 0)
- `limit` (integer, optional): Maximum number of messages to return (default: 50, max: 200)

#### Response
**Success Response (200 OK):**
```json
[
  {
    "id": "string (UUID format)",
    "role": "string (user|assistant|system)",
    "content": "string",
    "timestamp": "string (ISO 8601 datetime)",
    "created_at": "string (ISO 8601 datetime)"
  }
]
```

**Example Success Response:**
```json
[
  {
    "id": "987e6543-e21b-32d1-a654-426614174999",
    "role": "user",
    "content": "Add a task to buy groceries",
    "timestamp": "2023-10-20T11:00:00Z",
    "created_at": "2023-10-20T11:00:00Z"
  },
  {
    "id": "876e5432-d10a-21c0-z345-315503063888",
    "role": "assistant",
    "content": "I've added the task 'buy groceries' to your list.",
    "timestamp": "2023-10-20T11:00:05Z",
    "created_at": "2023-10-20T11:00:05Z"
  }
]
```

---

### GET /{user_id}/search
Search conversations and messages by content.

#### Request
**Headers:**
- `Authorization: Bearer {token}` (required)

**Path Parameters:**
- `user_id` (string, UUID format): The ID of the user. Must match the authenticated user.

**Query Parameters:**
- `query` (string, required): Search query string
- `limit` (integer, optional): Maximum number of results to return (default: 20, max: 100)
- `offset` (integer, optional): Number of results to skip (default: 0)

#### Response
**Success Response (200 OK):**
```json
{
  "query": "string",
  "conversations": [
    {
      "id": "string (UUID format)",
      "title": "string",
      "created_at": "string (ISO 8601 datetime)",
      "updated_at": "string (ISO 8601 datetime)",
      "last_activity": "string (ISO 8601 datetime)",
      "message_count": "integer"
    }
  ],
  "messages": [
    {
      "id": "string (UUID format)",
      "role": "string (user|assistant|system)",
      "content": "string",
      "timestamp": "string (ISO 8601 datetime)",
      "conversation_id": "string (UUID format)"
    }
  ],
  "total_conversation_results": "integer",
  "total_message_results": "integer",
  "limit": "integer",
  "offset": "integer"
}
```

**Example Success Response:**
```json
{
  "query": "groceries",
  "conversations": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Shopping List",
      "created_at": "2023-10-20T10:00:00Z",
      "updated_at": "2023-10-20T11:30:00Z",
      "last_activity": "2023-10-20T11:30:00Z",
      "message_count": 5
    }
  ],
  "messages": [
    {
      "id": "987e6543-e21b-32d1-a654-426614174999",
      "role": "user",
      "content": "Add a task to buy groceries",
      "timestamp": "2023-10-20T11:00:00Z",
      "conversation_id": "123e4567-e89b-12d3-a456-426614174000"
    }
  ],
  "total_conversation_results": 1,
  "total_message_results": 1,
  "limit": 20,
  "offset": 0
}
```

## Data Models

### Conversation
```json
{
  "id": "string (UUID)",
  "user_id": "string (UUID)",
  "title": "string (1-200 characters)",
  "created_at": "string (ISO 8601 datetime)",
  "updated_at": "string (ISO 8601 datetime)",
  "last_activity": "string (ISO 8601 datetime)",
  "message_count": "integer",
  "is_archived": "boolean",
  "parent_conversation_id": "string (UUID, nullable)",
  "branch_depth": "integer",
  "is_branch_point": "boolean"
}
```

### Message
```json
{
  "id": "string (UUID)",
  "conversation_id": "string (UUID)",
  "role": "string (user|assistant|system)",
  "content": "string (1-10000 characters)",
  "timestamp": "string (ISO 8601 datetime)",
  "created_at": "string (ISO 8601 datetime)",
  "updated_at": "string (ISO 8601 datetime)",
  "tool_calls": "string (JSON, nullable)",
  "tool_results": "string (JSON, nullable)",
  "needs_clarification": "boolean"
}
```

### ChatRequest
```json
{
  "message": "string (required, 1-5000 characters)",
  "conversation_id": "string (optional, UUID format)"
}
```

### ChatResponse
```json
{
  "conversation_id": "string (UUID format)",
  "response": "string (AI-generated response)",
  "message_id": "string (UUID format of the assistant's response message)"
}
```

## Security Requirements
- All endpoints require authentication
- User ID in path must match authenticated user
- Users can only access their own conversations
- Input sanitization applied to prevent injection attacks
- Rate limiting applied to prevent abuse of AI services
- MCP tools enforce user ownership for all operations

## Performance Requirements
- API responses should return within 5 seconds under normal load
- Support for 100+ concurrent users
- Database queries should complete within 1 second
- AI agent processing should complete within 3 seconds under normal conditions

## Error Handling
- Consistent error response format using JSON with "detail" field
- Appropriate HTTP status codes for different error conditions
- No sensitive information exposed in error messages
- Proper logging of errors for debugging without exposing details to users