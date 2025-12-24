import os
import dramatiq
from dramatiq.brokers.redis import RedisBroker


def configure_broker() -> RedisBroker:
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        raise RuntimeError("REDIS_URL not configured")

    broker = RedisBroker(url=redis_url)
    dramatiq.set_broker(broker)
    return broker
