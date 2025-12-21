
from typing import List, Dict, Any, Optional
import os
import google.generativeai as genai
from .rate_limiter import RateLimiter
from .errors import ProviderError, ConfigurationError


class GeminiLLM:
    def __init__(
        self,
        model: str = "models/gemini-1.5-pro",
        api_key: Optional[str] = None,
        rate_limiter: Optional[RateLimiter] = None,
        generation_config: Optional[Dict[str, Any]] = None,
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ConfigurationError("GEMINI_API_KEY not configured")

        genai.configure(api_key=self.api_key)

        self.model_name = model
        self.model = genai.GenerativeModel(
            model_name=model,
            generation_config=generation_config or {},
        )
        self.rate_limiter = rate_limiter

    def generate(self, prompt: str) -> str:
        if self.rate_limiter:
            self.rate_limiter.acquire()
        try:
            response = self.model.generate_content(prompt)
            if not response.text:
                raise ProviderError("Empty response from Gemini")
            return response.text
        except Exception as e:
            raise ProviderError(str(e)) from e

    def chat(self, messages: List[Dict[str, str]]) -> str:
        if self.rate_limiter:
            self.rate_limiter.acquire()
        try:
            chat = self.model.start_chat(history=messages)
            response = chat.send_message(messages[-1]["content"])
            if not response.text:
                raise ProviderError("Empty response from Gemini")
            return response.text
        except Exception as e:
            raise ProviderError(str(e)) from e
