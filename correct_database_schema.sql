-- SQL schema for the multi-user todo application (matching SQLModel expectations)

-- Users table (matches User class in models/user.py)
CREATE TABLE IF NOT EXISTS "users" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON "users"(email);

-- TodoTask table (matches TodoTask class in models/todo_task.py)
CREATE TABLE IF NOT EXISTS "todotask" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    is_completed BOOLEAN DEFAULT FALSE,
    user_id UUID NOT NULL REFERENCES "users"(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index on user_id for faster user todo queries
CREATE INDEX IF NOT EXISTS idx_todotask_user_id ON "todotask"(user_id);

-- Index on is_completed for filtering completed/incomplete todos
CREATE INDEX IF NOT EXISTS idx_todotask_is_completed ON "todotask"(is_completed);

-- Index on created_at for sorting by date
CREATE INDEX IF NOT EXISTS idx_todotask_created_at ON "todotask"(created_at);

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to automatically update the updated_at column
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON "users"
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_todotask_updated_at BEFORE UPDATE ON "todotask"
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();