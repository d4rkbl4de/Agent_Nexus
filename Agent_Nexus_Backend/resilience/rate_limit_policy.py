import asyncio
import time
from typing import Optional
from common.config.logging import logger
from common.config.settings import settings
from tracing.context import get_trace_id

class RateLimiter:
    _instances: dict[str, "RateLimiter"] = {}

    def __new__(cls, resource_name: str, **kwargs):
        if resource_name not in cls._instances:
            cls._instances[resource_name] = super(RateLimiter, cls).__new__(cls)
        return cls._instances[resource_name]

    def __init__(
        self, 
        resource_name: str, 
        requests_per_minute: int = 60, 
        burst_limit: int = 10
    ):
        if hasattr(self, "_initialized"):
            return
        self.resource_name = resource_name
        self.rate = requests_per_minute / 60.0
        self.burst_limit = burst_limit
        self.tokens = float(burst_limit)
        self.last_check = time.perf_counter()
        self._lock = asyncio.Lock()
        self._initialized = True

    async def acquire(self) -> bool:
        async with self._lock:
            now = time.perf_counter()
            elapsed = now - self.last_check
            self.last_check = now
            
            self.tokens += elapsed * self.rate
            if self.tokens > self.burst_limit:
                self.tokens = self.burst_limit

            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return True
            
            logger.warning(
                f"Rate limit exceeded for {self.resource_name}. "
                f"TraceID: {get_trace_id()} | Tokens: {self.tokens:.2f}"
            )
            return False

    async def wait_for_slot(self, timeout: float = 10.0):
        start_time = time.perf_counter()
        while not await self.acquire():
            if time.perf_counter() - start_time > timeout:
                logger.error(f"Timeout waiting for rate limit slot: {self.resource_name}")
                raise TimeoutError(f"Rate limit timeout for {self.resource_name}")
            
            sleep_time = max(0.1, (1.0 - self.tokens) / self.rate if self.rate > 0 else 1.0)
            await asyncio.sleep(min(sleep_time, 1.0))

def rate_limited(resource_name: str, rpm: int = 60):
    def decorator(func):
        limiter = RateLimiter(resource_name, requests_per_minute=rpm)
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            await limiter.wait_for_slot()
            return await func(*args, **kwargs)
        return wrapper
    return decorator