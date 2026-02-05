from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    # Database configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://todo_user:todo_password@localhost:5432/todo_db")

    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Environment settings
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # CORS settings
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,https://localhost:3000,https://127.0.0.1:3000")

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # in seconds

    # Redis configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # AI Service configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.7"))
    AI_MAX_TOKENS: int = int(os.getenv("AI_MAX_TOKENS", "1000"))

    # AI Agent configuration
    AI_AGENT_NAME: str = os.getenv("AI_AGENT_NAME", "Todo Assistant")
    AI_AGENT_MODEL: str = os.getenv("AI_AGENT_MODEL", "gpt-4-turbo")
    AI_AGENT_TEMPERATURE: float = float(os.getenv("AI_AGENT_TEMPERATURE", "0.7"))
    AI_AGENT_MAX_TOKENS: int = int(os.getenv("AI_AGENT_MAX_TOKENS", "1500"))
    AI_AGENT_INSTRUCTIONS: str = os.getenv(
        "AI_AGENT_INSTRUCTIONS",
        "You are a helpful todo management assistant that helps users manage their tasks using natural language. "
        "You can help create, update, delete, and list todos. You have access to tools for these operations. "
        "Always respond in a friendly and helpful manner."
    )

    model_config = {
        "env_file": ".env"
    }

settings = Settings()