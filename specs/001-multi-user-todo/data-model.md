# Data Model: Multi-User Todo Web Application

**Feature**: 001-multi-user-todo
**Date**: 2026-01-20
**Modeler**: Claude

## Overview

This document defines the data models for the multi-user Todo web application, specifying entity relationships, validation rules, and state transitions.

## Entity Definitions

### User Entity
**Description**: Represents an individual user account with authentication details

**Fields**:
- `id`: UUID (Primary Key) - Unique identifier for the user
- `email`: String (Unique, Indexed) - User's email address for login
- `hashed_password`: String - Securely hashed password using bcrypt
- `created_at`: DateTime (Indexed) - Timestamp when account was created
- `updated_at`: DateTime - Timestamp when account was last updated
- `is_active`: Boolean (Default: True) - Whether the account is active

**Validation Rules**:
- Email must be a valid email format
- Email must be unique across all users
- Password must meet security requirements (min length, complexity)
- Email cannot be changed after creation

**Relationships**:
- One-to-Many: User has many TodoTasks (via user_id foreign key)

### TodoTask Entity
**Description**: Represents a user's task with title, description, and completion status

**Fields**:
- `id`: UUID (Primary Key) - Unique identifier for the task
- `title`: String (Required, Max 255 chars) - Task title
- `description`: String (Optional, Max 1000 chars) - Task details
- `is_completed`: Boolean (Default: False) - Completion status
- `user_id`: UUID (Foreign Key) - Reference to owning user
- `created_at`: DateTime (Indexed) - Timestamp when task was created
- `updated_at`: DateTime - Timestamp when task was last updated

**Validation Rules**:
- Title is required and cannot be empty
- Title must be between 1 and 255 characters
- Description, if provided, must be less than 1000 characters
- Task can only be accessed by the user who owns it (via user_id)
- User_id must reference an existing, active user

**State Transitions**:
- `is_completed` can transition from `false` to `true` (completed)
- `is_completed` can transition from `true` to `false` (uncompleted)
- All other fields remain constant except `updated_at` which updates on any change

## Relationships

### User → TodoTask (One-to-Many)
- A user can own multiple todo tasks
- Each todo task belongs to exactly one user
- Foreign key constraint ensures referential integrity
- Cascade delete: When a user is deleted, all their tasks are also deleted

## Indexes

### Primary Indexes
- User.id (Primary Key)
- TodoTask.id (Primary Key)

### Secondary Indexes
- User.email (Unique Index) - For efficient authentication
- User.created_at (Index) - For sorting and filtering
- TodoTask.user_id (Index) - For efficient user-specific queries
- TodoTask.created_at (Index) - For sorting tasks chronologically

## Constraints

### Data Integrity Constraints
- Email uniqueness across all users
- Referential integrity between TodoTask.user_id and User.id
- Non-null constraints on required fields
- Length constraints on string fields

### Business Logic Constraints
- Users can only access/modify their own tasks
- Task ownership cannot be transferred between users
- Users cannot create tasks for other users

## Schema Evolution Considerations

### Future Extensions
- Potential addition of task categories/tags
- Due date field for tasks
- Priority levels for tasks
- Subtasks relationship for hierarchical task organization

### Migration Strategy
- Use Alembic for database schema migrations
- Maintain backward compatibility during schema changes
- Plan for data transformation during schema updates