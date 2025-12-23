# logger.py
import logging
import os
from logging.handlers import RotatingFileHandler
import json

LOG_DIR = os.getenv("LOG_DIR", os.path.join(os.getcwd(), "logs"))
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, "agentic.log")

class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload)

def get_logger(name: str = "agentic"):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fh = RotatingFileHandler(LOG_PATH, maxBytes=5 * 1024 * 1024, backupCount=3)
    fh.setFormatter(JsonFormatter())
    logger.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(sh)
    return logger
