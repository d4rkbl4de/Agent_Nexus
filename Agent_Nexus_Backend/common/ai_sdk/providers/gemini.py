import httpx
import logging
from common.config import settings

logger = logging.getLogger(__name__)

class OpenRouterClient:
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://agent-nexus.com", # Required by OpenRouter
            "Content-Type": "application/json",
        }

    async def get_completion(self, messages: list, model: str = "google/gemini-2.0-flash-001"):
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(self.base_url, headers=self.headers, json=payload)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"OpenRouter API Error: {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Unexpected Connection Error: {str(e)}")
                raise