import logging

def get_logger(name: str):
    return logging.getLogger(f"agent_nexus.{name}")