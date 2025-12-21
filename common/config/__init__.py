from .settings import settings
from .logging_config import setup_logging

setup_logging()

__all__ = [
    "settings",
    "setup_logging",
]