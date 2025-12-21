import time
import threading
from .errors import RateLimitError


class RateLimiter:
    def __init__(self, max_calls: int, period: float):
        if max_calls <= 0:
            raise ValueError("max_calls must be positive")
        if period <= 0:
            raise ValueError("period must be positive")
        self.max_calls = max_calls
        self.period = period
        self.calls = []
        self.lock = threading.Lock()

    def acquire(self) -> None:
        with self.lock:
            now = time.time()
            self.calls = [t for t in self.calls if now - t < self.period]
            if len(self.calls) >= self.max_calls:
                raise RateLimitError("LLM rate limit exceeded")
            self.calls.append(now)
