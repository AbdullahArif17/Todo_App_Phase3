import os
from main import app
import uvicorn

# Application entry point for various deployment platforms
if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))  # Default to 7860 for Hugging Face Spaces unless specified otherwise
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
