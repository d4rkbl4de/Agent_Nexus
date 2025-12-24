import os
import dramatiq
from memory import MemoryManager


@dramatiq.actor(queue_name="maintenance")
def cleanup_agent_memory(event: dict) -> None:
    agent_id = event.get("agent_id")
    if not agent_id:
        raise RuntimeError("agent_id missing in event")

    manager: MemoryManager = os.getenv("MEMORY_MANAGER")
    if not manager:
        raise RuntimeError("MEMORY_MANAGER not injected")

    manager.wipe(agent_id)
