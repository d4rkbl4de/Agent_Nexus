import dramatiq
from dramatiq.brokers.redis import RedisBroker
from common.config import settings
from common.config.logging_config import logger

try:
    broker = RedisBroker(url=settings.REDIS_URL)
    dramatiq.set_broker(broker)
    logger.info("Generic Dramatiq broker initialized successfully.")
except Exception as e:
    logger.error(f"FATAL: Could not initialize generic Dramatiq broker: {e}")