import sys
import logging
import json
from datetime import datetime
from typing import Any, Dict
from common.config.secrets import secrets

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_payload: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "func_name": record.funcName,
            "line_no": record.lineno,
            "trace_id": getattr(record, "trace_id", "GLOBAL"),
            "lobe": getattr(record, "lobe", "CORE"),
            "agent_id": getattr(record, "agent_id", "PLATFORM")
        }
        
        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)
        
        if hasattr(record, "extra_data"):
            log_payload["extra"] = record.extra_data

        return json.dumps(log_payload)

def setup_logging():
    log_level = getattr(logging, secrets.LOG_LEVEL.upper(), logging.INFO)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    
    if secrets.APP_ENV == "production":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | [%(trace_id)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

class AgentLogger:
    def __init__(self, name: str = "agent_nexus"):
        self.logger = logging.getLogger(name)

    def _log(self, level: int, msg: str, trace_id: str, lobe: str, agent_id: str, extra: Dict = None):
        extra_fields = {
            "trace_id": trace_id,
            "lobe": lobe,
            "agent_id": agent_id,
            "extra_data": extra or {}
        }
        self.logger.log(level, msg, extra=extra_fields)

    def info(self, msg: str, trace_id: str, lobe: str = "CORE", agent_id: str = "PLATFORM", extra: Dict = None):
        self._log(logging.INFO, msg, trace_id, lobe, agent_id, extra)

    def error(self, msg: str, trace_id: str, lobe: str = "CORE", agent_id: str = "PLATFORM", extra: Dict = None):
        self._log(logging.ERROR, msg, trace_id, lobe, agent_id, extra)

    def warning(self, msg: str, trace_id: str, lobe: str = "CORE", agent_id: str = "PLATFORM", extra: Dict = None):
        self._log(logging.WARNING, msg, trace_id, lobe, agent_id, extra)

    def critical(self, msg: str, trace_id: str, lobe: str = "CORE", agent_id: str = "PLATFORM", extra: Dict = None):
        self._log(logging.CRITICAL, msg, trace_id, lobe, agent_id, extra)

setup_logging()
logger = AgentLogger()