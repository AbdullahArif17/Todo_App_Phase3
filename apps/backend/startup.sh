#!/bin/bash
# Production startup script for Todo AI Chatbot Backend

set -e  # Exit on any error

echo "Starting Todo AI Chatbot Backend..."

# Run database migrations if needed
echo "Running database migrations..."
python -c "
from sqlmodel import SQLModel
from apps.backend.src.database import engine
from apps.backend.src.models.conversation import Conversation
from apps.backend.src.models.message import Message
from apps.backend.src.models.user import User
from apps.backend.src.models.todo_task import TodoTask

try:
    SQLModel.metadata.create_all(engine)
    print('Database tables created/updated successfully')
except Exception as e:
    print(f'Warning: Could not initialize database: {e}')
"

# Start the application with uvicorn
if [ "$ENVIRONMENT" = "development" ]; then
    echo "Starting in development mode..."
    exec uvicorn apps.backend.src.main:app --host 0.0.0.0 --port $PORT --reload
else
    echo "Starting in production mode..."
    exec uvicorn apps.backend.src.main:app --host 0.0.0.0 --port $PORT --workers 2 --timeout-keep-alive 30
fi