import os
from datetime import timedelta, datetime
from memory import MemoryManager


def run_maintenance():
    agent_id = os.getenv("AGENT_ID")
    if not agent_id:
        raise RuntimeError("AGENT_ID not configured")

    manager: MemoryManager = os.getenv("MEMORY_MANAGER")
    if not manager:
        raise RuntimeError("MEMORY_MANAGER not injected")

    cutoff = datetime.utcnow() - timedelta(days=30)

    memories = manager.recall(agent_id, long_term=True, short_term=False)
    for record in memories:
        if record.timestamp < cutoff:
            manager.wipe(agent_id)


if __name__ == "__main__":
    run_maintenance()
