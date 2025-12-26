import os
import sys
from typing import List, Dict, Any, Optional

from lobes.autoagent_hub.app import app
from lobes.autoagent_hub.tasks import HubTaskProcessor
from lobes.autoagent_hub.agent_sdk.registry import HubAgentRegistry
from lobes.autoagent_hub.orchestration.planner import OrchestrationPlanner
from lobes.autoagent_hub.orchestration.executor import OrchestrationExecutor
from lobes.autoagent_hub.orchestration.supervisor import OrchestrationSupervisor

__lobe_name__ = "autoagent_hub"
__version__ = "1.0.0"
__author__ = "Kakarot"

hub_registry = HubAgentRegistry()
task_processor = HubTaskProcessor()
planner = OrchestrationPlanner()
executor = OrchestrationExecutor()
supervisor = OrchestrationSupervisor()

__all__ = [
    "app",
    "hub_registry",
    "task_processor",
    "planner",
    "executor",
    "supervisor",
    "__lobe_name__",
    "__version__"
]