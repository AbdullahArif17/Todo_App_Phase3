# AI Chat API Documentation

## Overview

The AI Chat API provides a natural language interface for todo management. Users can interact with an AI assistant to create, update, delete, and list their todo items using conversational language.

## Authentication

All chat endpoints require authentication using JWT Bearer tokens. Include the token in the `Authorization` header:

```
Authorization: Bearer <jwt_token>
```

## Endpoints

### POST /api/v1/chat/{user_id}

Initiates a new conversation or continues an existing one with the AI assistant.

#### Path Parameters

- `user_id` (string, required): The ID of the authenticated user. Must match the user ID in the JWT token.

#### Request Body

```json
{
  "conversation_id": "string", // Optional: ID of existing conversation to continue
  "message": "string"          // Required: User's message to the AI assistant
}
```

#### Response

```json
{
  "conversation_id": "string",  // ID of the conversation (new or existing)
  "response": "string",         // AI assistant's response
  "message_id": "string"        // Optional: ID of the AI response message
}
```

#### Example Request

```bash
curl -X POST "http://localhost:8000/api/v1/chat/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a new todo: Buy groceries"
  }'
```

#### Example Response

```json
{
  "conversation_id": "987e6543-21dc-ba98-7654-fedcba987654",
  "response": "I've added 'Buy groceries' to your todo list.",
  "message_id": "555e6543-33dc-ca98-8854-fedcba987777"
}
```

## Conversation Flow

1. **Starting a new conversation**: Send a request without `conversation_id` to start a new conversation.
2. **Continuing a conversation**: Include `conversation_id` to continue an existing conversation and maintain context.
3. **AI Capabilities**: The AI assistant can:
   - Create new todos: "Add a todo: Buy milk"
   - Update existing todos: "Mark 'Buy milk' as completed"
   - Delete todos: "Delete the 'Buy milk' todo"
   - List todos: "Show me my todos"

## Rate Limits

- 30 requests per minute per user for AI service usage
- Exceeding the limit results in a 429 Too Many Requests response

## Error Responses

- `400 Bad Request`: Invalid request format or content
- `401 Unauthorized`: Invalid or missing authentication token
- `403 Forbidden`: User not authorized to access resource
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Unexpected server error

## Additional Endpoints

### GET /api/v1/chat/{user_id}/conversations

Retrieve a paginated list of user's conversations.

#### Query Parameters

- `skip` (integer, optional): Number of conversations to skip (default: 0)
- `limit` (integer, optional): Maximum number of conversations to return (default: 20)

#### Response

```json
[
  {
    "id": "string",
    "title": "string",
    "created_at": "string",
    "updated_at": "string",
    "last_activity": "string",
    "message_count": "integer",
    "is_archived": "boolean"
  }
]
```

### GET /api/v1/chat/{user_id}/conversations/{conversation_id}/messages

Retrieve paginated messages from a specific conversation.

#### Path Parameters

- `user_id` (string, required): The ID of the authenticated user
- `conversation_id` (string, required): The ID of the conversation

#### Query Parameters

- `skip` (integer, optional): Number of messages to skip (default: 0)
- `limit` (integer, optional): Maximum number of messages to return (default: 50)

#### Response

```json
[
  {
    "id": "string",
    "role": "user|assistant|system",
    "content": "string",
    "timestamp": "string",
    "created_at": "string"
  }
]
```

### GET /api/v1/chat/{user_id}/search

Search conversations and messages by content.

#### Path Parameters

- `user_id` (string, required): The ID of the authenticated user

#### Query Parameters

- `query` (string, required): Search query string
- `limit` (integer, optional): Maximum number of results to return (default: 20)
- `offset` (integer, optional): Number of results to skip (default: 0)

#### Response

```json
{
  "query": "string",
  "conversations": [...],
  "messages": [...],
  "total_conversation_results": "integer",
  "total_message_results": "integer",
  "limit": "integer",
  "offset": "integer"
}
```

### GET /api/v1/chat/{user_id}/analytics

Get analytics for the user's conversations.

#### Path Parameters

- `user_id` (string, required): The ID of the authenticated user

#### Response

Analytics data for the user's conversations.

### GET /api/v1/chat/{user_id}/stream/{conversation_id}

Stream messages from a conversation in real-time.

#### Path Parameters

- `user_id` (string, required): The ID of the authenticated user
- `conversation_id` (string, required): The ID of the conversation to stream

#### Response

Server-sent events with conversation messages.

### POST /api/v1/conversations/{conversation_id}/archive

Archive a conversation.

#### Path Parameters

- `conversation_id` (string, required): The ID of the conversation to archive

#### Response

Confirmation message.

### POST /api/v1/conversations/{conversation_id}/tag

Add a tag to a conversation.

#### Path Parameters

- `conversation_id` (string, required): The ID of the conversation

#### Request Body

```json
{
  "tag_name": "string"  // Name of the tag to add
}
```

#### Response

Confirmation message.

## Conversation Management

The API now supports advanced conversation management features:

- **Tagging**: Tag conversations for better organization
- **Search**: Search through conversation history
- **Pagination**: Paginated access to conversations and messages
- **Analytics**: Detailed analytics for conversation patterns
- **Export**: Export conversation data for privacy compliance
- **Archiving**: Archive old conversations to optimize performance

## Security Considerations

- Input sanitization is applied to prevent injection attacks
- Conversation access is validated to ensure user ownership
- Malicious content patterns are detected and blocked
- Rate limiting is applied per user and per conversation to prevent abuse
- User data deletion and anonymization functions are available for privacy compliance
- Conversation export functionality is available for data portability