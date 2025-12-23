from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import Literal

class DatabaseSettings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://agentnexus_user:nexus_password@db/agentnexus_db"
    REDIS_URL: str = "redis://redis:6379/0"
    QDRANT_HOST: str = "http://qdrant:6333"

class LobeSettings(BaseSettings):
    INSIGHT_MATE_URL: str = "http://insightmate:8000"
    STUDY_FLOW_URL: str = "http://studyflow:8000"
    CHAT_BUDDY_URL: str = "http://chatbuddy:8000"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', 
        env_file_encoding='utf-8',
        extra='ignore'
    )

    ENV: Literal['dev', 'test', 'prod'] = 'dev'
    LOG_LEVEL: str = "INFO"
    SERVICE_NAME: str = "AgentNexus"

    GEMINI_API_KEY: str = Field(
        default="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"
    )

    DB: DatabaseSettings = DatabaseSettings()
    LOBES: LobeSettings = LobeSettings()

    @field_validator("GEMINI_API_KEY")
    @classmethod
    def check_key_presence(cls, v: str):
        if not v or "sk-or" not in v:
            raise ValueError("A valid OpenRouter API Key is required.")
        return v

settings = Settings()