import logging
from common.config import settings
from logging.config import dictConfig
import json

class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    def format(self, record):
        # Base log data
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineNo": record.lineno,
        }
        
        # Add extra dictionary data if available
        if isinstance(record.args, dict):
            log_record.update(record.args)
        
        return json.dumps(log_record)

def setup_logging(log_level: str = None):
    """
    Sets up application-wide structured logging.
    """
    # FIX: Correctly access the settings object attribute (settings.LOG_LEVEL)
    effective_level = log_level or settings.LOG_LEVEL
    
    log_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                '()': JsonFormatter,
            },
            'standard': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'json',
                'stream': 'ext://sys.stdout',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': effective_level,
        },
        'loggers': {
            'sqlalchemy.engine': {
                'level': 'WARNING',
                'handlers': ['console'],
                'propagate': False,
            },
            'dramatiq': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate': False,
            }
        }
    }
    
    dictConfig(log_config)

# Initialize logging on import
setup_logging()

# Use the root logger for application-wide logging
logger = logging.getLogger('agent_nexus')
