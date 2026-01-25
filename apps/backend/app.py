import os
import uvicorn
from src.api.main import app

# For Hugging Face Spaces compatibility
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
