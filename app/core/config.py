from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    QDRANT_URL: str
    QDRANT_API_KEY: str
    COHERE_API_KEY: str
    GROQ_API_KEY: str
    ADMIN_API_KEY: str

    # New: API keys for /chat
    RAG_API_KEYS: str  # comma-separated string

    # Convert string → list
    @property
    def api_keys(self) -> List[str]:
        return [k.strip() for k in self.RAG_API_KEYS.split(",") if k.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()