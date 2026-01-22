#!/bin/bash

# Production build script for Todo Web Application

set -e  # Exit immediately if a command exits with a non-zero status

echo "Starting production build..."

# Function to check if a command exists
command_exists() {
  command -v "$@" > /dev/null 2>&1
}

# Check required commands
for cmd in docker docker-compose node npm python; do
  if ! command_exists "$cmd"; then
    echo "Error: $cmd is not installed or not in PATH"
    exit 1
  fi
done

# Build backend
echo "Building backend..."
cd apps/backend
if [ -f "requirements-prod.txt" ]; then
    pip install -r requirements-prod.txt
else
    pip install -r requirements.txt
fi

# Run any necessary backend build steps
# (e.g., database migrations preparation, etc.)

cd ..

# Build frontend
echo "Building frontend..."
cd frontend

# Install dependencies
npm ci --only=production

# Build the application
npm run build

# Verify build succeeded
if [ -d ".next" ]; then
    echo "✓ Frontend build completed successfully"
else
    echo "✗ Frontend build failed - .next directory not found"
    exit 1
fi

cd ..

echo ""
echo "==========================================="
echo "BUILD SUCCESSFUL!"
echo "==========================================="
echo "Both backend and frontend have been built for production."
echo ""
echo "Next steps:"
echo "1. Ensure your environment variables are set in .env.production"
echo "2. Run the deployment script: ./deploy.sh"
echo "==========================================="

# Set executable permissions
chmod +x ../deploy.sh