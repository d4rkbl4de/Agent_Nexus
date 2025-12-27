from common.ai_sdk.client import AgenticAISDK
from common.ai_sdk.routing import model_router
from common.ai_sdk.prompts import PromptManager
from common.ai_sdk.tokenization import TokenCounter
from common.ai_sdk.exceptions import (
    AISDKException,
    ProviderError,
    TokenLimitExceeded,
    RateLimitReached,
    SafetyConstraintViolation
)

class AISDKManifest:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AISDKManifest, cls).__new__(cls)
            cls._instance.client = AgenticAISDK()
            cls._instance.router = model_router
            cls._instance.prompts = PromptManager()
            cls._instance.tokenizer = TokenCounter()
        return cls._instance

ai_sdk = AISDKManifest()

__all__ = [
    "ai_sdk",
    "AgenticAISDK",
    "model_router",
    "PromptManager",
    "TokenCounter",
    "AISDKException",
    "ProviderError",
    "TokenLimitExceeded",
    "RateLimitReached",
    "SafetyConstraintViolation"
]