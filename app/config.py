"""Application configuration using pydantic-settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Create a .env file with these variables for local development.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    openai_api_key: str
    database_url: str = "sqlite:///./knowledge_extractor.db"
    llm_model: str = "gpt-4.1-mini"


# Global settings instance
settings = Settings()

