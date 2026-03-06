from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    QDRANT_URL: str
    QDRANT_API_KEY: str
    COHERE_API_KEY: str
    GROQ_API_KEY: str
    ADMIN_API_KEY: str   # ← add this

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
