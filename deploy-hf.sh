#!/bin/bash

# Deployment script for Hugging Face Spaces Backend

set -e  # Exit immediately if a command exits with a non-zero status

echo "🚀 Deploying Todo Backend to Hugging Face Spaces..."

# Function to check if a command exists
command_exists() {
  command -v "$@" > /dev/null 2>&1
}

# Check prerequisites
if ! command_exists git; then
  echo "❌ Error: git is not installed or not in PATH"
  exit 1
fi

if ! command_exists curl; then
  echo "❌ Error: curl is not installed or not in PATH"
  exit 1
fi

echo "✅ Prerequisites check passed"

# Function to prepare backend for Hugging Face deployment
prepare_backend_for_hf() {
  echo "📦 Preparing backend for Hugging Face Spaces deployment..."

  # Create a clean directory for Hugging Face deployment
  HF_DIR="hf-backend-deployment"
  rm -rf "$HF_DIR"
  mkdir -p "$HF_DIR"

  # Copy necessary files to Hugging Face directory
  cp apps/backend/Dockerfile.hf "$HF_DIR/Dockerfile" || { echo "❌ Dockerfile.hf not found"; exit 1; }
  cp apps/backend/requirements-final.txt "$HF_DIR/requirements.txt" || { echo "❌ requirements-final.txt not found"; exit 1; }
  cp apps/backend/app.py "$HF_DIR/" || { echo "❌ app.py not found"; exit 1; }

  # Copy source code
  mkdir -p "$HF_DIR/src"
  cp -r apps/backend/src/* "$HF_DIR/src/" || { echo "❌ Failed to copy src directory"; exit 1; }

  # Copy alembic directory if it exists
  if [ -d "apps/backend/alembic" ]; then
    mkdir -p "$HF_DIR/alembic"
    cp -r apps/backend/alembic/* "$HF_DIR/alembic/"
  fi

  echo "✅ Backend prepared for Hugging Face Spaces deployment in $HF_DIR/"
  echo "📁 Contents of Hugging Face deployment directory:"
  ls -la "$HF_DIR/"
}

# Function to display deployment instructions
display_hf_deployment_instructions() {
  echo ""
  echo "🎉 Backend preparation completed!"
  echo ""
  echo "##################################################"
  echo "# HUGGING FACE SPACES DEPLOYMENT INSTRUCTIONS"
  echo "##################################################"
  echo ""
  echo "1. CREATE A HUGGING FACE SPACE:"
  echo "   a. Go to https://huggingface.co/spaces"
  echo "   b. Click 'Create new Space'"
  echo "   c. Set these options:"
  echo "      - Name: your-username/todo-backend"
  echo "      - SDK: Docker"
  echo "      - Hardware: CPU Basic (or higher)"
  echo "      - Visibility: Public/Private"
  echo ""
  echo "2. UPLOAD THE FILES TO YOUR SPACE:"
  echo "   a. You can either:"
  echo "      - Option 1: Git clone your Space repository and copy files"
  echo "      - Option 2: Use the Hugging Face web interface to upload files"
  echo ""
  echo "   b. Copy these files to your Space:"
  echo "      - Dockerfile (from apps/backend/Dockerfile.hf)"
  echo "      - requirements.txt (from apps/backend/requirements-final.txt)"
  echo "      - app.py (from apps/backend/app.py)"
  echo "      - src/ directory (entire backend source code)"
  echo "      - alembic/ directory (for database migrations)"
  echo ""
  echo "3. SET ENVIRONMENT VARIABLES IN YOUR SPACE SETTINGS:"
  echo "   - DATABASE_URL: PostgreSQL connection string"
  echo "   - SECRET_KEY: Strong secret key for JWT (at least 32 chars)"
  echo "   - ALGORITHM: HS256"
  echo "   - ACCESS_TOKEN_EXPIRE_MINUTES: 30"
  echo "   - ENVIRONMENT: production"
  echo "   - DEBUG: False"
  echo ""
  echo "4. WAIT FOR BUILD:"
  echo "   - The Space will automatically build and deploy"
  echo "   - Check the 'Logs' tab to monitor the build process"
  echo ""
  echo "5. VERIFY DEPLOYMENT:"
  echo "   - Once deployed, your API will be available at:"
  echo "     https://your-username-todo-backend.hf.space"
  echo "   - API documentation: https://your-username-todo-backend.hf.space/docs"
  echo "   - Health check: https://your-username-todo-backend.hf.space/health"
  echo ""
  echo "6. CONNECT TO FRONTEND:"
  echo "   - Update your frontend's NEXT_PUBLIC_API_BASE_URL to point to your Hugging Face backend"
  echo "   - For Vercel deployment: Set NEXT_PUBLIC_API_BASE_URL=https://your-username-todo-backend.hf.space"
  echo ""
  echo "💡 TIPS:"
  echo "   - For database, consider using Neon Serverless PostgreSQL (free tier available)"
  echo "   - Generate a strong SECRET_KEY using: openssl rand -hex 32"
  echo "   - Monitor the Space logs during initial deployment"
  echo ""
  echo "✅ Your backend is now ready for Hugging Face Spaces deployment!"
  echo "##################################################"
}

# Main execution
main() {
  prepare_backend_for_hf
  display_hf_deployment_instructions
}

# Run main function
main "$@"