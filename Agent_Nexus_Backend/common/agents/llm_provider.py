from typing import Optional, List, Dict
from common.llm.gemini import OpenRouterClient
import logging

logger = logging.getLogger(__name__)

class LLMProvider:
    def __init__(self):
        self.client = OpenRouterClient()

    async def ask(self, prompt: str, system_instruction: str = "You are a helpful AI agent.") -> str:
        """Standard interface for single-turn reasoning."""
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ]
        
        try:
            result = await self.client.get_completion(messages)
            return result['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"LLM Provider failed to generate response: {e}")
            return "Error: The agent's reasoning engine is currently offline."


_provider_instance = None

def get_llm() -> LLMProvider:
    global _provider_instance
    if _provider_instance is None:
        _provider_instance = LLMProvider()
    return _provider_instance