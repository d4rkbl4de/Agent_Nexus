import os
from pathlib import Path
from typing import Dict, Any, List
from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "Agent Nexus Hive Mind"
    APP_ENV: str = Field(default="development")
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    POSTGRES_URL: PostgresDsn
    REDIS_URL: RedisDsn
    VECTOR_DB_URL: str
    VECTOR_DB_API_KEY: Optional[str] = None
    
    OPENAI_API_KEY: str
    GEMINI_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    
    DEFAULT_LLM_MODEL: str = "gpt-4o"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    MAX_TOKENS_SHORT_TERM: int = 4000
    MAX_TOKENS_LONG_TERM: int = 8000
    CONTEXT_WINDOW_LIMIT: int = 128000
    
    LOG_LEVEL: str = "INFO"
    ENABLE_TRACING: bool = True
    COST_THRESHOLD_DAILY: float = 10.0
    
    ALLOWED_LOBES: List[str] = ["InsightMate", "StudyFlow", "ChatBuddy", "AutoAgent_Hub"]

    @field_validator("APP_ENV")
    @classmethod
    def validate_env(cls, v: str) -> str:
        allowed = ["development", "staging", "production", "testing"]
        if v not in allowed:
            raise ValueError(f"Env must be one of {allowed}")
        return v

    def get_lobe_config(self, lobe_name: str) -> Dict[str, Any]:
        if lobe_name not in self.ALLOWED_LOBES:
            return {}
        return {
            "lobe": lobe_name,
            "tracing_enabled": self.ENABLE_TRACING,
            "environment": self.APP_ENV
        }

settings = Settings()