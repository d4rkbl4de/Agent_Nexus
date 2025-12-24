import logging
from typing import Optional
from .llm_wrapper import LLMWrapper
from .exceptions import AIProviderError

logger = logging.getLogger("agent_nexus.ai_sdk")
logger.setLevel(logging.INFO)

_wrapper: Optional[LLMWrapper] = None

def get_ai_client() -> LLMWrapper:
   
    global _wrapper
    if _wrapper is None:
        logger.info("Initializing Agent Nexus Unified AI Client...")
        _wrapper = LLMWrapper()
    return _wrapper


__all__ = [
    "get_ai_client",
    "LLMWrapper",
    "AIProviderError",
    "logger"
]


