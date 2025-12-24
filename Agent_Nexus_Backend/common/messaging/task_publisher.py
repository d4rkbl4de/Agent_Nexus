from typing import Any, Dict
import dramatiq
from .event_schemas import TaskEvent


class TaskPublisher:
    def __init__(self, namespace: str = "tasks"):
        self.namespace = namespace

    def publish(self, task_name: str, agent_id: str, payload: Dict[str, Any]) -> None:
        event = TaskEvent(
            task_name=task_name,
            agent_id=agent_id,
            payload=payload,
        )
        actor_name = f"{self.namespace}.{task_name}"
        try:
            actor = dramatiq.get_broker().get_actor(actor_name)
        except KeyError:
            raise RuntimeError(f"Task actor not registered: {actor_name}")
        actor.send(event.dict())
