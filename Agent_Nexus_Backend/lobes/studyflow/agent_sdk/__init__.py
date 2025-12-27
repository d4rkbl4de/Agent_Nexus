from typing import Dict, Any, Optional
from lobes.studyflow.agent_sdk.registry import study_registry
from lobes.studyflow.agent_sdk.state import StudyStateManager
from lobes.studyflow.agent_sdk.constraints import StudyFlowConstraints
from lobes.studyflow.agent_sdk.core.planner import CurriculumPlanner
from lobes.studyflow.agent_sdk.core.tutor import AdaptiveTutor
from lobes.studyflow.agent_sdk.core.evaluator import KnowledgeEvaluator
from common.schemas.errors import AppError, ErrorCategory, ErrorCode
from common.config.logging_config import logger

class StudyFlowSDK:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StudyFlowSDK, cls).__new__(cls)
            cls._instance.registry = study_registry
            cls._instance._initialized = True
        return cls._instance

    async def create_learning_engine(
        self,
        agent_id: str,
        trace_id: str,
        user_id: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        definition = self.registry.get_definition(agent_id)
        
        constraints = StudyFlowConstraints(agent_id=agent_id, trace_id=trace_id)
        state_manager = StudyStateManager(trace_id=trace_id, user_id=user_id)
        evaluator = KnowledgeEvaluator(trace_id=trace_id, state=state_manager)
        
        planner = CurriculumPlanner(
            definition=definition,
            trace_id=trace_id,
            constraints=constraints
        )
        
        tutor = AdaptiveTutor(
            state=state_manager,
            trace_id=trace_id,
            evaluator=evaluator,
            constraints=constraints
        )

        logger.info(
            f"STUDYFLOW_SDK_INITIALIZED | Agent: {agent_id} | User: {user_id}",
            extra={
                "trace_id": trace_id,
                "session_id": session_id,
                "lobe": "StudyFlow"
            }
        )

        return {
            "planner": planner,
            "tutor": tutor,
            "evaluator": evaluator,
            "state": state_manager,
            "session_id": session_id or f"study_{trace_id}",
            "agent_metadata": definition.model_dump()
        }

    def get_capabilities(self) -> List[str]:
        return [
            "adaptive_curriculum_generation",
            "knowledge_gap_analysis",
            "active_recall_testing",
            "spaced_repetition_scheduling"
        ]

study_sdk = StudyFlowSDK()

__all__ = [
    "study_sdk",
    "CurriculumPlanner",
    "AdaptiveTutor",
    "KnowledgeEvaluator",
    "StudyStateManager",
    "StudyFlowConstraints"
]