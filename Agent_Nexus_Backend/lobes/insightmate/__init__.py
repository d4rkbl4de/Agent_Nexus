from typing import Dict, Any, List, Optional
from lobes.insightmate.agent_sdk.registry import insight_registry
from lobes.insightmate.agent_sdk.core.planner import InsightPlanner
from lobes.insightmate.agent_sdk.core.executor import InsightExecutor
from lobes.insightmate.agent_sdk.state import InsightStateManager
from lobes.insightmate.tasks import task_registry
from common.config.logging_config import logger
from common.schemas.errors import AppError, ErrorCategory, ErrorCode

class InsightMateLobe:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InsightMateLobe, cls).__new__(cls)
            cls._instance.name = "InsightMate"
            cls._instance.registry = insight_registry
            cls._instance.tasks = task_registry
            cls._instance._initialized = True
        return cls._instance

    async def start(self):
        logger.info(
            "LOBE_BOOTSTRAP | Name: InsightMate",
            trace_id="SYSTEM_BOOT",
            lobe=self.name
        )

    async def initialize_analysis(self, agent_id: str, trace_id: str) -> Dict[str, Any]:
        definition = self.registry.get_definition(agent_id)
        if not definition:
            raise AppError(
                message=f"Insight agent {agent_id} not found",
                category=ErrorCategory.NOT_FOUND_ERROR,
                code=ErrorCode.RESOURCE_NOT_FOUND,
                trace_id=trace_id
            )

        state_manager = InsightStateManager(trace_id=trace_id)
        planner = InsightPlanner(definition=definition, trace_id=trace_id)
        executor = InsightExecutor(state=state_manager, trace_id=trace_id)

        return {
            "planner": planner,
            "executor": executor,
            "agent_name": definition.name,
            "status": "active"
        }

    async def get_health(self) -> Dict[str, Any]:
        return {
            "lobe": self.name,
            "status": "healthy",
            "active_tasks": len(self.tasks.list_tasks()),
            "registered_summarizers": self.registry.count_agents()
        }

lobe = InsightMateLobe()

__all__ = [
    "lobe",
    "insight_registry",
    "InsightPlanner",
    "InsightExecutor",
    "InsightStateManager",
    "task_registry"
]