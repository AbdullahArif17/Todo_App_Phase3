# Data Model: Stateless Chat Architecture

## Entities

### Conversation
Represents a chat session between a user and the AI assistant, containing a sequence of messages with timestamps.

**Fields**:
- `id`: UUID (primary key) - Unique identifier for the conversation
- `user_id`: UUID (foreign key) - Reference to the user who owns this conversation
- `title`: String - Descriptive title for the conversation (auto-generated from first message if not provided)
- `created_at`: DateTime - Timestamp when the conversation was created
- `updated_at`: DateTime - Timestamp when the conversation was last updated
- `last_activity`: DateTime - Timestamp of the most recent message in the conversation
- `message_count`: Integer - Number of messages in the conversation (for performance)
- `is_archived`: Boolean - Whether the conversation is archived (default: false)
- `parent_conversation_id`: UUID (nullable, foreign key) - Reference to parent conversation if this is a branch
- `branch_depth`: Integer - Depth in the conversation branching hierarchy (default: 0)
- `is_branch_point`: Boolean - Whether this conversation has branches from it (default: false)

**Relationships**:
- One-to-many with Message (conversation has many messages)
- Many-to-one with User (conversation belongs to one user)
- Self-referencing optional (parent_conversation_id points to another conversation)

**Validation Rules**:
- `user_id` must reference an existing user
- `title` must be 1-200 characters
- `created_at` is set automatically on creation
- `updated_at` is updated automatically on changes
- `message_count` must be non-negative
- `branch_depth` must be non-negative

### Message
A single communication in a conversation, either from the user or the AI assistant, with content and metadata.

**Fields**:
- `id`: UUID (primary key) - Unique identifier for the message
- `conversation_id`: UUID (foreign key) - Reference to the conversation this message belongs to
- `role`: String (enum: "user", "assistant", "system") - The role of the message sender
- `content`: Text - The actual content of the message
- `timestamp`: DateTime - When the message was created
- `created_at`: DateTime - When the record was created in the database
- `updated_at`: DateTime - When the record was last updated
- `tool_calls`: JSON (nullable) - Information about tools called during AI processing
- `tool_results`: JSON (nullable) - Results from tools called during AI processing
- `needs_clarification`: Boolean - Whether the agent needs clarification from the user (default: false)

**Relationships**:
- Many-to-one with Conversation (message belongs to one conversation)
- Through conversation, indirectly related to User

**Validation Rules**:
- `conversation_id` must reference an existing conversation
- `role` must be one of "user", "assistant", or "system"
- `content` must be 1-10,000 characters
- `timestamp` is set automatically on creation
- `tool_calls` must be valid JSON if present
- `tool_results` must be valid JSON if present

### User
An authenticated entity that owns conversations and has permissions to access only their own data. (This entity likely already exists in the system.)

**Fields**:
- `id`: UUID (primary key) - Unique identifier for the user
- `email`: String - User's email address (unique)
- `hashed_password`: String - Hashed password for authentication
- `is_active`: Boolean - Whether the user account is active
- `created_at`: DateTime - When the user account was created
- `updated_at`: DateTime - When the user account was last updated

**Relationships**:
- One-to-many with Conversation (user has many conversations)

**Validation Rules**:
- `email` must be a valid email format and unique
- `hashed_password` must be properly hashed
- `is_active` defaults to true

## Relationships

### Conversation ↔ Message
- One Conversation has many Messages (1:N relationship)
- Foreign key: `conversation_id` in Message table references `id` in Conversation table
- Cascade delete: When a conversation is deleted, all its messages are also deleted

### User ↔ Conversation
- One User has many Conversations (1:N relationship)
- Foreign key: `user_id` in Conversation table references `id` in User table
- When a user is deleted, their conversations are also deleted

## Indexes

### Conversation Table
- Primary index on `id` (UUID)
- Composite index on `(user_id, last_activity)` for efficient user conversation queries sorted by recency
- Index on `created_at` for chronological queries

### Message Table
- Primary index on `id` (UUID)
- Index on `conversation_id` for efficient conversation message queries
- Composite index on `(conversation_id, timestamp)` for chronological message retrieval within conversations
- Index on `timestamp` for temporal queries

## State Transitions

### Conversation States
1. **Active** → **Archived**: When user archives the conversation (is_archived = true)
2. **Archived** → **Active**: When user unarchives the conversation (is_archived = false)

### Message States
- Messages are immutable once created (no state transitions)
- Message content can be updated only by system for corrections (rare operation)

## Constraints

### Referential Integrity
- All foreign key relationships enforce referential integrity
- CASCADE delete ensures data consistency when parent records are removed
- NOT NULL constraints on required fields

### Data Consistency
- Conversation message_count is updated automatically when messages are added/deleted
- Conversation last_activity is updated automatically when new messages are added
- User ownership is validated on all conversation and message access operations