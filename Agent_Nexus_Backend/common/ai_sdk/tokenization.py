import tiktoken
from typing import Dict, Any, Union
from common.config.logging import logger
from common.ai_sdk.exceptions import TokenLimitException

class TokenCounter:
    def __init__(self):
        self.prices = {
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
            "gemini-1.5-flash": {"input": 0.00035, "output": 0.00105},
            "anthropic/claude-3-haiku": {"input": 0.00025, "output": 0.00125}
        }
        self.default_encoding = "cl100k_base"

    def count_tokens(self, text: str, model: str = "gpt-4-turbo") -> int:
        try:
            try:
                encoding = tiktoken.encoding_for_model(model)
            except KeyError:
                encoding = tiktoken.get_encoding(self.default_encoding)
            
            return len(encoding.encode(text))
        except Exception as e:
            logger.error(f"TOKEN_COUNT_ERROR | Model: {model} | Error: {str(e)}")
            return len(text) // 4

    def calculate_usage(self, prompt: str, completion: str, model: str) -> Dict[str, int]:
        prompt_tokens = self.count_tokens(prompt, model)
        completion_tokens = self.count_tokens(completion, model)
        
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens
        }

    def estimate_cost(self, usage: Dict[str, int], model: str) -> float:
        model_pricing = self.prices.get(model, self.prices["gpt-3.5-turbo"])
        
        input_cost = (usage["prompt_tokens"] / 1000) * model_pricing["input"]
        output_cost = (usage["completion_tokens"] / 1000) * model_pricing["output"]
        
        return round(input_cost + output_cost, 6)

    def validate_limit(self, prompt: str, limit: int, model: str):
        count = self.count_tokens(prompt, model)
        if count > limit:
            logger.error(f"TOKEN_LIMIT_EXCEEDED | Limit: {limit} | Attempted: {count}")
            raise TokenLimitException(
                message=f"Prompt exceeds token limit of {limit}",
                limit=limit,
                attempted=count
            )
        return True