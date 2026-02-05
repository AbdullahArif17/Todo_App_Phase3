"""
Hugging Face Space App Entry Point
This file is required for Hugging Face Spaces deployment
"""
from apps.backend.src.main import app

# This is the entry point for Hugging Face Spaces
# The FastAPI app is imported from the main application file
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)