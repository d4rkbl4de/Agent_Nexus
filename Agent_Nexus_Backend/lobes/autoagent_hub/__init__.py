from typing import Dict, Any
from lobes.autoagent_hub.agent_sdk import hub_sdk
from lobes.autoagent_hub.orchestration.supervisor import HubSupervisor
from lobes.autoagent_hub.tasks import task_registry
from common.config.logging_config import logger

class AutoAgentHubLobe:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AutoAgentHubLobe, cls).__new__(cls)
            cls._instance.sdk = hub_sdk
            cls._instance.supervisor = HubSupervisor()
            cls._instance.tasks = task_registry
            cls._instance.name = "AutoAgent_Hub"
            cls._instance._initialized = True
        return cls._instance

    async def start(self):
        logger.info(
            "LOBE_INITIALIZED | Name: AutoAgent_Hub",
            trace_id="SYSTEM_BOOT",
            lobe=self.name
        )

    async def get_health(self) -> Dict[str, Any]:
        sdk_status = self.sdk.get_heartbeat()
        return {
            "lobe": self.name,
            "status": "healthy",
            "agents_ready": sdk_status["registered_agents"],
            "active_orchestrations": self.supervisor.get_active_count(),
            "tasks_defined": len(self.tasks.list_tasks())
        }

lobe = AutoAgentHubLobe()

__all__ = [
    "lobe",
    "hub_sdk",
    "HubSupervisor",
    "task_registry"
]