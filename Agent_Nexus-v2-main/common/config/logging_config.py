import logging
import json
import sys
from logging.config import dictConfig
from .settings import settings

class AgentNexusFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "lobe": settings.SERVICE_NAME,
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

def setup_logging():
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json_formatter': {
                '()': AgentNexusFormatter,
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'json_formatter',
                'stream': sys.stdout,
            }
        },
        'root': {
            'handlers': ['console'],
            'level': settings.LOG_LEVEL,
        }
    }
    dictConfig(config)