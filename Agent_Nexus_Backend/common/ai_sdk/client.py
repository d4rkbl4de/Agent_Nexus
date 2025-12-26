import time
import uuid
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from common.config.logging import logger
from common.ai_sdk.routing import AIRouter
from common.ai_sdk.tokenization import TokenCounter
from common.ai_sdk.exceptions import ProviderException, RateLimitException
from tracing.context import get_trace_id

class AIResponse(BaseModel):
    request_id: str
    content: str
    model: str
    provider: str
    usage: Dict[str, int]
    cost_estimate: float
    latency_ms: float

class AIClient:
    def __init__(self, default_provider: str = "openai"):
        self.router = AIRouter()
        self.tokenizer = TokenCounter()
        self.default_provider = default_provider

    async def generate(
        self,
        prompt: str,
        system_instructions: Optional[str] = None,
        model_override: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        context: Optional[Dict[str, Any]] = None
    ) -> AIResponse:
        start_time = time.perf_counter()
        trace_id = get_trace_id() or str(uuid.uuid4())
        
        target_config = self.router.get_route(
            prompt=prompt, 
            override=model_override,
            context=context
        )
        
        logger.info(
            f"AI_REQUEST_START | Trace: {trace_id} | "
            f"Provider: {target_config['provider']} | Model: {target_config['model']}"
        )

        try:
            raw_response = await self._dispatch_to_provider(
                provider=target_config["provider"],
                model=target_config["model"],
                prompt=prompt,
                system=system_instructions,
                max_tokens=max_tokens,
                temperature=temperature
            )

            latency = (time.perf_counter() - start_time) * 1000
            usage = self.tokenizer.calculate_usage(prompt, raw_response["content"], target_config["model"])
            cost = self.tokenizer.estimate_cost(usage, target_config["model"])

            response = AIResponse(
                request_id=trace_id,
                content=raw_response["content"],
                model=target_config["model"],
                provider=target_config["provider"],
                usage=usage,
                cost_estimate=cost,
                latency_ms=latency
            )

            logger.info(
                f"AI_REQUEST_SUCCESS | Trace: {trace_id} | "
                f"Tokens: {usage['total_tokens']} | Cost: ${cost:.6f} | Latency: {latency:.2f}ms"
            )
            
            return response

        except Exception as e:
            logger.error(f"AI_REQUEST_FAILURE | Trace: {trace_id} | Error: {str(e)}")
            self._handle_provider_error(e, target_config)
            raise

    async def _dispatch_to_provider(self, **kwargs) -> Dict[str, Any]:
        provider = kwargs["provider"]
        if provider == "openai":
            from common.ai_sdk.providers.openai import OpenAIProvider
            return await OpenAIProvider().call(**kwargs)
        elif provider == "gemini":
            from common.ai_sdk.providers.gemini import GeminiProvider
            return await GeminiProvider().call(**kwargs)
        elif provider == "openrouter":
            from common.ai_sdk.providers.openrouter import OpenRouterProvider
            return await OpenRouterProvider().call(**kwargs)
        else:
            raise ProviderException(f"Unsupported provider: {provider}")

    def _handle_provider_error(self, error: Exception, config: Dict[str, Any]):
        if "rate_limit" in str(error).lower():
            raise RateLimitException(f"Provider {config['provider']} rate limited.")
        raise ProviderException(f"Provider {config['provider']} failed: {str(error)}")