from typing import Dict, Any, List, Optional
from lobes.studyflow.agent_sdk.registry import study_registry
from lobes.studyflow.agent_sdk.core.planner import CurriculumPlanner
from lobes.studyflow.agent_sdk.core.tutor import AdaptiveTutor
from lobes.studyflow.agent_sdk.state import StudyStateManager
from lobes.studyflow.tasks import study_task_registry
from common.config.logging_config import logger
from common.schemas.errors import AppError, ErrorCategory, ErrorCode

class StudyFlowLobe:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StudyFlowLobe, cls).__new__(cls)
            cls._instance.name = "StudyFlow"
            cls._instance.registry = study_registry
            cls._instance.tasks = study_task_registry
            cls._instance._initialized = True
        return cls._instance

    async def start(self):
        logger.info(
            "LOBE_BOOTSTRAP | Name: StudyFlow",
            trace_id="SYSTEM_BOOT",
            lobe=self.name
        )

    async def initialize_study_session(
        self, 
        agent_id: str, 
        user_id: str, 
        trace_id: str
    ) -> Dict[str, Any]:
        definition = self.registry.get_definition(agent_id)
        if not definition:
            raise AppError(
                message=f"Study agent {agent_id} not found",
                category=ErrorCategory.NOT_FOUND_ERROR,
                code=ErrorCode.RESOURCE_NOT_FOUND,
                trace_id=trace_id
            )

        state_manager = StudyStateManager(trace_id=trace_id, user_id=user_id)
        planner = CurriculumPlanner(definition=definition, trace_id=trace_id)
        tutor = AdaptiveTutor(state=state_manager, trace_id=trace_id)

        return {
            "planner": planner,
            "tutor": tutor,
            "state_manager": state_manager,
            "agent_name": definition.name,
            "status": "active"
        }

    async def get_health(self) -> Dict[str, Any]:
        return {
            "lobe": self.name,
            "status": "healthy",
            "active_sessions": await self.tasks.get_active_count(),
            "registered_tutors": self.registry.count_agents()
        }

lobe = StudyFlowLobe()

__all__ = [
    "lobe",
    "study_registry",
    "CurriculumPlanner",
    "AdaptiveTutor",
    "StudyStateManager",
    "study_task_registry"
]