"""
Production startup script for Todo AI Backend
Uses gunicorn for production deployment
"""
import os
import sys
import logging
from main import app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the backend src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Set environment variables if not already set
if not os.getenv("ENVIRONMENT"):
    os.environ["ENVIRONMENT"] = "production"

if not os.getenv("DEBUG"):
    os.environ["DEBUG"] = "false"

if not os.getenv("LOG_LEVEL"):
    os.environ["LOG_LEVEL"] = "INFO"

# For Hugging Face Spaces compatibility
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 7860))
    host = os.environ.get("HOST", "0.0.0.0")

    # Run with uvicorn for development/testing or directly for Hugging Face
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=os.environ.get("LOG_LEVEL", "info"),
    )
else:
    # When imported by gunicorn
    application = app