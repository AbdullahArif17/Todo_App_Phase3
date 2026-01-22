-- Initialize the database for the Todo application

-- Create extension for UUID generation if not exists
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- The tables will be created by SQLModel migrations
-- This file is for additional initialization if needed

-- Example: Create indexes for better performance
-- CREATE INDEX IF NOT EXISTS idx_user_email ON user(email);
-- CREATE INDEX IF NOT EXISTS idx_todo_user_id ON todo_task(user_id);
-- CREATE INDEX IF NOT EXISTS idx_todo_created_at ON todo_task(created_at);

-- Optionally, create the demo user here if needed
-- INSERT INTO user (id, email, hashed_password, created_at, updated_at, is_active)
-- SELECT 'demo-user-uuid', 'demo@example.com', '$2b$12$d4QWY//rkFrriOzlzH1Txu5eHC9XlqbQje.PLXuTCTGugf0SAm4mq', NOW(), NOW(), true
-- WHERE NOT EXISTS (SELECT 1 FROM user WHERE email = 'demo@example.com');