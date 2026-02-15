"""
Production startup script for Todo AI Chatbot Backend
Used for Hugging Face Spaces deployment
"""
import os
import sys
import uvicorn

# Add the backend src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    host = os.environ.get("HOST", "0.0.0.0")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=os.environ.get("LOG_LEVEL", "info"),
    )