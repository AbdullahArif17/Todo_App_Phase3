#!/bin/bash
# Production startup script for Todo AI Backend

set -e  # Exit on any error

echo "Starting Todo AI Backend in production mode..."

# Set default environment variables if not provided
export PORT=${PORT:-7860}
export ENVIRONMENT=${ENVIRONMENT:-production}
export DEBUG=${DEBUG:-false}
export LOG_LEVEL=${LOG_LEVEL:-info}

echo "Environment: $ENVIRONMENT"
echo "Port: $PORT"
echo "Debug: $DEBUG"

# Run any necessary database migrations
echo "Checking database migrations..."
python3 -c '
import sys
import os
# Add both the current directory and src directory to the Python path
sys.path.insert(0, os.path.join(os.getcwd(), "."))
sys.path.insert(0, os.path.join(os.getcwd(), "src"))
from sqlmodel import SQLModel
from database import engine
from models.conversation import Conversation
from models.message import Message
from models.user import User
try:
    from models.todo_task import TodoTask  # This may not exist yet, will be created as needed
except ImportError:
    # If TodoTask model doesn't exist yet, it's fine - just continue
    pass

try:
    # Create database tables if they don't exist
    SQLModel.metadata.create_all(bind=engine)
    print("Database tables created/updated successfully")
except Exception as e:
    print(f"Warning: Could not initialize database: {e}")
    # Don'\''t exit on database error as it might be a connection issue
'

# Start the application with gunicorn
echo "Starting application server..."
exec gunicorn --config gunicorn.conf.py production:app