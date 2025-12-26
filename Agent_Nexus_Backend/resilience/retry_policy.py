import asyncio
import random
import functools
from typing import Callable, Any, Type, Union, Tuple, Optional
from common.config.logging import logger
from tracing.context import get_trace_id

class AsyncRetryPolicy:
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 10.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
        exceptions: Tuple[Type[Exception], ...] = (Exception,)
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.exceptions = exceptions

    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except self.exceptions as e:
                last_exception = e
                if attempt == self.max_retries:
                    logger.error(
                        f"Retry exhaustion after {attempt} attempts. "
                        f"TraceID: {get_trace_id()} | Error: {str(e)}"
                    )
                    raise last_exception

                delay = min(self.max_delay, self.base_delay * (self.backoff_factor ** attempt))
                if self.jitter:
                    delay *= (0.5 + random.random())

                logger.warning(
                    f"Transient error detected (Attempt {attempt + 1}/{self.max_retries}). "
                    f"Retrying in {delay:.2f}s... | TraceID: {get_trace_id()} | Error: {type(e).__name__}"
                )
                
                await asyncio.sleep(delay)
        
        raise last_exception

def with_retry(
    max_retries: int = 3, 
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    **retry_kwargs
):
    def decorator(func: Callable):
        policy = AsyncRetryPolicy(max_retries=max_retries, exceptions=exceptions, **retry_kwargs)
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await policy.execute(func, *args, **kwargs)
        return wrapper
    return decorator