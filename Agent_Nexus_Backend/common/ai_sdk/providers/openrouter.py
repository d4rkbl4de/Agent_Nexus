import httpx
import os
from typing import Optional, List, Dict, Any
from ..exceptions import AIProviderError

class OpenRouterClient:
    """Production-grade client for OpenRouter Multi-Model Orchestration."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000", # Required for OpenRouter rankings
            "X-Title": "Agent Nexus"
        }

    async def generate_completion(
        self, 
        model: str, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Sends a request to OpenRouter and returns the text response."""
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    error_data = response.json()
                    raise AIProviderError(
                        f"OpenRouter Error: {error_data.get('error', {}).get('message', 'Unknown Error')}"
                    )

                result = response.json()
                return result["choices"][0]["message"]["content"]

            except httpx.HTTPError as e:
                raise AIProviderError(f"Network error connecting to OpenRouter: {str(e)}")
            except Exception as e:
                raise AIProviderError(f"Unexpected error in OpenRouter provider: {str(e)}")