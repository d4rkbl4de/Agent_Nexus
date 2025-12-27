from common.config.settings import settings
from common.config.logging_config import logger
from common.memory.facade import MemorySystem
from common.ai_sdk.client import AgenticAISDK
from common.messaging.schemas import MessageValidator

class NexusCore:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NexusCore, cls).__new__(cls)
            cls._instance.settings = settings
            cls._instance.logger = logger
            cls._instance.memory = MemorySystem()
            cls._instance.ai = AgenticAISDK()
            cls._instance.validator = MessageValidator()
            cls._instance._initialized = True
        return cls._instance

    def get_status(self):
        return {
            "version": self.settings.VERSION,
            "env": self.settings.APP_ENV,
            "lobes_active": self.settings.ALLOWED_LOBES
        }

sdk = NexusCore()

__all__ = [
    "sdk",
    "settings",
    "logger",
    "MemorySystem",
    "AgenticAISDK",
    "MessageValidator"
]