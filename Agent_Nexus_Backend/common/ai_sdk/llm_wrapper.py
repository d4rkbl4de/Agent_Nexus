import os
import logging
from typing import List, Dict, Any, Optional, Union, TypeAlias

from .providers.openrouter import OpenRouterClient
from .providers.gemini import GeminiClient
from .utils.rate_limiter import RateLimiter
from .exceptions import AIProviderError

MessageList: TypeAlias = List[Dict[str, str]]

logger = logging.getLogger("agent_nexus.ai_sdk")

class LLMWrapper:
    def __init__(self):
        self.openrouter = OpenRouterClient()
        self.gemini_fallback = GeminiClient()
        self.rate_limiter = RateLimiter(requests_per_minute=int(os.getenv("AI_RPM_LIMIT", 50)))
        
        self.primary_model = os.getenv("PRIMARY_MODEL", "google/gemini-pro-1.5")
        self.reasoning_model = os.getenv("REASONING_MODEL", "anthropic/claude-3.5-sonnet")

    async def chat(
        self, 
        messages: MessageList, 
        model_type: str = "primary",
        temperature: float = 0.7
    ) -> str:
        target_model = self.primary_model
        if model_type == "reasoning":
            target_model = self.reasoning_model
        elif "/" in model_type:
            target_model = model_type

        await self.rate_limiter.wait_if_needed()

        try:
            logger.info(f"AI_REQ_START: model={target_model}")
            return await self.openrouter.generate_completion(
                model=target_model,
                messages=messages,
                temperature=temperature
            )
        except (AIProviderError, Exception) as e:
            logger.warning(f"AI_PRIMARY_FAIL: {str(e)}")
            
            try:
                logger.info("AI_FALLBACK_START: target=gemini-direct")
                return await self.gemini_fallback.generate_content(messages)
            except Exception as final_err:
                logger.critical(f"AI_SYSTEM_HALT: total_provider_failure err={str(final_err)}")
                raise AIProviderError("Nexus AI Infrastructure Unreachable") from final_err