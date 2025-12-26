import asyncio
import time
import functools
from enum import Enum
from typing import Callable, Any, Dict, Optional, Type
from common.config.logging import logger
from tracing.context import get_trace_id

class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreaker:
    _instances: Dict[str, "CircuitBreaker"] = {}

    def __new__(cls, name: str, **kwargs):
        if name not in cls._instances:
            cls._instances[name] = super(CircuitBreaker, cls).__new__(cls)
        return cls._instances[name]

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        expected_exceptions: tuple = (Exception,),
    ):
        if hasattr(self, "_initialized"):
            return
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exceptions = expected_exceptions
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self._lock = asyncio.Lock()
        self._initialized = True

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        async with self._lock:
            await self._before_call()

        if self.state == CircuitState.OPEN:
            raise RuntimeError(f"Circuit {self.name} is OPEN. Terminating execution to protect resources.")

        try:
            result = await func(*args, **kwargs)
            async with self._lock:
                self._on_success()
            return result
        except self.expected_exceptions as e:
            async with self._lock:
                self._on_failure(e)
            raise e

    async def _before_call(self):
        if self.state == CircuitState.OPEN and self.last_failure_time:
            if time.perf_counter() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit {self.name} transitioned to HALF_OPEN. Probing resource...")

    def _on_success(self):
        if self.state == CircuitState.HALF_OPEN or self.failure_count > 0:
            logger.info(f"Circuit {self.name} transitioned to CLOSED. Health restored.")
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None

    def _on_failure(self, exception: Exception):
        self.failure_count += 1
        self.last_failure_time = time.perf_counter()
        
        logger.warning(
            f"Circuit {self.name} failure detected (Count: {self.failure_count}/{self.failure_threshold}). "
            f"TraceID: {get_trace_id()} Error: {str(exception)}"
        )

        if self.failure_count >= self.failure_threshold or self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            logger.error(f"Circuit {self.name} is now OPEN. High failure rate detected. Escalating per Rule 14.")

def circuit_breaker(name: str, **cb_kwargs):
    def decorator(func: Callable):
        cb = CircuitBreaker(name, **cb_kwargs)
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await cb.call(func, *args, **kwargs)
        return wrapper
    return decorator