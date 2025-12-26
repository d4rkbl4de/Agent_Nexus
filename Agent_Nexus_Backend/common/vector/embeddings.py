import os
import asyncio
import uuid
from typing import List, Optional, Union
from openai import AsyncOpenAI, RateLimitError, APIConnectionError, APIStatusError
from common.config.logging import logger

class EmbeddingGenerator:
    def __init__(
        self, 
        model: str = "text-embedding-3-small", 
        dimensions: Optional[int] = None,
        max_retries: int = 3
    ):
        self.model = model
        self.dimensions = dimensions or (1536 if "small" in model else 3072)
        self.max_retries = max_retries
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY_MISSING")
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def generate(
        self, 
        input_data: Union[str, List[str]], 
        trace_id: Optional[str] = None
    ) -> List[List[float]]:
        t_id = trace_id or str(uuid.uuid4())
        texts = [input_data] if isinstance(input_data, str) else input_data
        
        if not texts:
            return []

        cleaned_texts = [t.replace("\n", " ").strip() for t in texts if t.strip()]
        
        for attempt in range(self.max_retries):
            try:
                params = {
                    "input": cleaned_texts,
                    "model": self.model
                }
                if "text-embedding-3" in self.model:
                    params["dimensions"] = self.dimensions

                response = await self.client.embeddings.create(**params)
                
                logger.info(
                    f"EMBEDDING_GEN_SUCCESS | Trace: {t_id} | Model: {self.model} | "
                    f"Count: {len(cleaned_texts)} | Attempt: {attempt + 1}"
                )
                
                return [data.embedding for data in response.data]

            except RateLimitError:
                if attempt == self.max_retries - 1:
                    logger.error(f"EMBEDDING_RATE_LIMIT_EXCEEDED | Trace: {t_id}")
                    raise
                wait_time = (2 ** attempt)
                await asyncio.sleep(wait_time)
            
            except (APIConnectionError, APIStatusError) as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"EMBEDDING_API_ERROR | Trace: {t_id} | Error: {str(e)}")
                    raise
                await asyncio.sleep(1)
            
            except Exception as e:
                logger.critical(f"EMBEDDING_UNEXPECTED_FAILURE | Trace: {t_id} | Error: {str(e)}")
                raise

    async def generate_single(self, text: str, trace_id: Optional[str] = None) -> List[float]:
        result = await self.generate([text], trace_id=trace_id)
        return result[0] if result else []