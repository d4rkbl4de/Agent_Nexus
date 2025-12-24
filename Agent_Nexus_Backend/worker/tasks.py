import dramatiq
from .dramatiq_app import broker
from common.config.logging_config import logger

@dramatiq.actor
def health_check_task(service_name: str):
    """
    A simple task used to confirm the generic worker is running and connected.
    """
    logger.info(f"Worker Health Check: Task received for service: {service_name}")
    return f"Generic worker task completed for {service_name}"
