"""
Main application entry point for Hugging Face Spaces deployment
This file is required for the app.py to import from
"""
from apps.backend.src.main import app

# Export the app instance for Hugging Face Spaces
# The variable 'app' is what Hugging Face Spaces will look for
app_instance = app

if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(
        app_instance,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )