import os
from src.api.main import app
import uvicorn

# For Hugging Face Spaces compatibility
if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
