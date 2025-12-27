import os
from common.config.secrets import secrets
from common.config.logging import logger
from common.config.monitoring import monitor

class ConfigManifest:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManifest, cls).__new__(cls)
            cls._instance.env = os.getenv("APP_ENV", "development")
            cls._instance.version = "1.0.0"
            cls._instance.secrets = secrets
            cls._instance.logger = logger
            cls._instance.monitor = monitor
        return cls._instance

    @property
    def is_production(self) -> bool:
        return self.env == "production"

    @property
    def is_debug(self) -> bool:
        return self.env == "development"

    def get_platform_metadata(self):
        return {
            "platform": "Agent Nexus Hive Mind",
            "version": self.version,
            "environment": self.env,
            "cost_limit_active": True
        }

config = ConfigManifest()

__all__ = [
    "config",
    "secrets",
    "logger",
    "monitor"
]