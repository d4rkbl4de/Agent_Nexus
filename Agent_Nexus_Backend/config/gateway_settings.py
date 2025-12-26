from pydantic_settings import BaseSettings
from typing import List, Dict
from enum import Enum

class RoutingMode(str, Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_LOAD = "least_load"
    AFFINITY = "affinity"

class GatewaySettings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Agent Nexus Hive Mind"
    
    ALLOWED_HOSTS: List[str] = ["*"]
    
    LOBE_ROUTING_TABLE: Dict[str, str] = {
        "insightmate": "http://insightmate:8001",
        "studyflow": "http://studyflow:8002",
        "chatbuddy": "http://chatbuddy:8003",
        "autoagent_hub": "http://autoagent_hub:8004"
    }

    DEFAULT_ROUTING_MODE: RoutingMode = RoutingMode.AFFINITY
    REQUEST_TIMEOUT_SECONDS: int = 60
    MAX_CONCURRENT_AGENT_SESSIONS: int = 1000

    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    class Config:
        case_sensitive = True
        env_prefix = "GATEWAY_"

gateway_settings = GatewaySettings()