#!/bin/bash

# Production deployment script for Todo Web Application

set -e  # Exit immediately if a command exits with a non-zero status

echo "Starting production deployment..."

# Check if running as root (not recommended for production)
if [ "$EUID" -eq 0 ]; then
  echo "WARNING: Running as root is not recommended. Please run as a non-root user."
fi

# Environment variables
ENV_FILE=".env.production"
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"

# Function to check if a command exists
command_exists() {
  command -v "$@" > /dev/null 2>&1
}

# Check required commands
for cmd in docker docker-compose git curl; do
  if ! command_exists "$cmd"; then
    echo "Error: $cmd is not installed or not in PATH"
    exit 1
  fi
done

# Load environment variables
if [ -f "$ENV_FILE" ]; then
  echo "Loading environment variables from $ENV_FILE"
  export $(grep -v '^#' "$ENV_FILE" | xargs)
else
  echo "Error: $ENV_FILE not found"
  exit 1
fi

# Check if SECRET_KEY is set
if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "super-long-and-secure-key-generated-for-production" ]; then
  echo "Error: SECRET_KEY is not properly set in $ENV_FILE"
  echo "Please generate a strong secret key and update the .env.production file"
  exit 1
fi

# Build and deploy the application
echo "Building and deploying the application..."

# Build the services
docker-compose -f "$DOCKER_COMPOSE_FILE" build

# Start the services in detached mode
docker-compose -f "$DOCKER_COMPOSE_FILE" up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 10

# Check if services are running
SERVICES=("backend" "frontend" "db" "redis")
for service in "${SERVICES[@]}"; do
  if docker-compose -f "$DOCKER_COMPOSE_FILE" ps "$service" | grep -q "Up"; then
    echo "✓ $service is running"
  else
    echo "✗ $service is not running"
    docker-compose -f "$DOCKER_COMPOSE_FILE" logs "$service"
    exit 1
  fi
done

# Run database migrations
echo "Running database migrations..."
docker-compose -f "$DOCKER_COMPOSE_FILE" exec backend alembic upgrade head

# Create admin user if it doesn't exist
echo "Creating demo user..."
docker-compose -f "$DOCKER_COMPOSE_FILE" exec backend python create_demo_user.py

# Health check
echo "Performing health check..."
if curl -sf http://localhost:8000/health > /dev/null; then
  echo "✓ Backend health check passed"
else
  echo "✗ Backend health check failed"
  exit 1
fi

if curl -sf http://localhost:3000 > /dev/null; then
  echo "✓ Frontend is accessible"
else
  echo "✗ Frontend is not accessible"
fi

echo ""
echo "==========================================="
echo "DEPLOYMENT SUCCESSFUL!"
echo "==========================================="
echo "Application is now running in production mode"
echo ""
echo "Services:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  Database: localhost:5432 (internal)"
echo "  Redis:    localhost:6379 (internal)"
echo ""
echo "Demo Credentials:"
echo "  Email: demo@example.com"
echo "  Password: demo123"
echo ""
echo "To view logs: docker-compose -f $DOCKER_COMPOSE_FILE logs -f"
echo "To stop: docker-compose -f $DOCKER_COMPOSE_FILE down"
echo "==========================================="

# Create a backup of the deployment configuration
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
cp "$ENV_FILE" "$ENV_FILE.backup_$TIMESTAMP"
cp "$DOCKER_COMPOSE_FILE" "$DOCKER_COMPOSE_FILE.backup_$TIMESTAMP"

echo "Configuration backups created with timestamp: $TIMESTAMP"