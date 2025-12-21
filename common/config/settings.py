from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    ENV: Literal['dev', 'test', 'prod'] = 'dev'
    SERVICE_NAME: str = "AgentNexusHiveMind"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "YOUR_SUPER_SECRET_KEY_FOR_JWT_OR_TASK_SIGNING"

    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/mydb"
    REDIS_URL: str = "redis://redis:6379/0"
    QDRANT_HOST: str = "http://qdrant:6333"

    INSIGHT_MATE_URL: str = "http://insightmate:8000"
    STUDY_FLOW_URL: str = "http://studyflow:8000"
    CHAT_BUDDY_URL: str = "http://chatbuddy:8000"
    AUTO_AGENT_HUB_URL: str = "http://autoagenthub:8000"

    GEMINI_API_KEY: str = "sk-..."
    N8N_WEBHOOK_SECRET: str = "n8n-..."

def settings() -> Settings:
    return Settings()