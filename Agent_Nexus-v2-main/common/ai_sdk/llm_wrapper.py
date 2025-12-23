import asyncio
import random
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .tokenizer import TokenUsage, count_tokens

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LLMResponse:
    text: str
    usage: TokenUsage
    model: str
    raw: Optional[Any] = None


class LLMClient(ABC):
    def __init__(
        self,
        model: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        base_backoff: float = 1.5,
    ):
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_backoff = base_backoff

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Dict[str, Any],
    ) -> LLMResponse:
        attempt = 0
        prompt_tokens = count_tokens(prompt)

        while True:
            try:
                response = await asyncio.wait_for(
                    self._generate_internal(prompt, system_prompt, **kwargs),
                    timeout=self.timeout,
                )

                return response

            except Exception as exc:
                attempt += 1

                logger.warning(
                    "llm_failure",
                    extra={
                        "model": self.model,
                        "attempt": attempt,
                        "error": str(exc),
                    },
                )

                if attempt >= self.max_retries:
                    raise

                await asyncio.sleep(
                    (self.base_backoff ** attempt)
                    + random.uniform(0.0, 0.5)
                )

    @abstractmethod
    async def _generate_internal(
        self,
        prompt: str,
        system_prompt: Optional[str],
        **kwargs: Dict[str, Any],
    ) -> LLMResponse:
        raise NotImplementedError
