import os
import aiohttp
from typing import Any, Dict, Optional
from common.config.logging import logger
from common.ai_sdk.exceptions import ProviderException, RateLimitException

class OpenAIProvider:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def call(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs: Any
    ) -> Dict[str, Any]:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=45
                ) as response:
                    if response.status == 429:
                        raise RateLimitException("OpenAI rate limit hit", provider="openai")
                    
                    if response.status != 200:
                        error_text = await response.text()
                        raise ProviderException(
                            f"OpenAI API error: {response.status}",
                            provider="openai",
                            original_error=error_text
                        )

                    data = await response.json()
                    return {
                        "content": data["choices"][0]["message"]["content"],
                        "raw": data
                    }

        except aiohttp.ClientError as e:
            logger.error(f"OPENAI_CONNECTION_ERROR | Error: {str(e)}")
            raise ProviderException(
                "Failed to connect to OpenAI",
                provider="openai",
                original_error=str(e)
            )