"""
Hugging Face Space App Entry Point
This file is required for Hugging Face Spaces deployment
"""
import os
from apps.backend.src.main import app

# This is the entry point for Hugging Face Spaces
# The FastAPI app is imported from the main application file
# Make sure the app variable is accessible at the module level
# Hugging Face Spaces expects a variable called 'app' to be available

# For Hugging Face Spaces compatibility
# The 'app' variable is the FastAPI instance that will be served
app_instance = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app_instance, host="0.0.0.0", port=int(os.environ.get("PORT", 7860)))