#!/bin/bash

# Production startup script for Todo Web Application Backend

set -e  # Exit immediately if a command exits with a non-zero status

echo "🚀 Starting Todo Web Application Backend in Production Mode..."

# Function to check if a command exists
command_exists() {
  command -v "$@" > /dev/null 2>&1
}

# Check prerequisites
if ! command_exists python; then
  echo "❌ Error: Python is not installed or not in PATH"
  exit 1
fi

if ! command_exists uvicorn; then
  echo "❌ Error: uvicorn is not installed"
  pip install uvicorn
fi

# Check if environment variables are set
if [ -z "$SECRET_KEY" ]; then
  echo "⚠️  Warning: SECRET_KEY is not set. Using default value (not recommended for production)."
  export SECRET_KEY="your-super-secret-key-change-in-production"
fi

if [ -z "$DATABASE_URL" ]; then
  echo "⚠️  Warning: DATABASE_URL is not set. Using SQLite default (not recommended for production)."
  export DATABASE_URL="sqlite:///./todo_app_prod.db"
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Run database migrations first
echo "🔄 Running database migrations..."
python -m alembic upgrade head || echo "⚠️  Database migrations skipped (alembic not configured)"

# Start the application with uvicorn
echo "⚙️  Starting application server..."
exec uvicorn src.api.main:app \
  --host ${HOST:-0.0.0.0} \
  --port ${PORT:-8000} \
  --workers ${WORKERS:-4} \
  --timeout-keep-alive 30 \
  --log-level ${LOG_LEVEL:-info} \
  --access-log