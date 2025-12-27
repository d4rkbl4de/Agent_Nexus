from typing import Dict, Any, Optional
from lobes.insightmate.agent_sdk.registry import insight_registry
from lobes.insightmate.agent_sdk.state import InsightStateManager
from lobes.insightmate.agent_sdk.constraints import InsightMateConstraints
from lobes.insightmate.agent_sdk.core.planner import InsightPlanner
from lobes.insightmate.agent_sdk.core.executor import InsightExecutor
from lobes.insightmate.agent_sdk.core.verifier import PolicyVerifier
from common.schemas.errors import AppError, ErrorCategory, ErrorCode
from common.config.logging_config import logger

class InsightMateSDK:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InsightMateSDK, cls).__new__(cls)
            cls._instance.registry = insight_registry
            cls._instance._initialized = True
        return cls._instance

    async def create_analysis_engine(
        self,
        agent_id: str,
        trace_id: str,
        user_id: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        definition = self.registry.get_definition(agent_id)
        
        constraints = InsightMateConstraints(agent_id=agent_id, trace_id=trace_id)
        state_manager = InsightStateManager(trace_id=trace_id)
        verifier = PolicyVerifier(constraints=constraints, trace_id=trace_id)
        
        planner = InsightPlanner(
            definition=definition,
            trace_id=trace_id,
            verifier=verifier
        )
        
        executor = InsightExecutor(
            state=state_manager,
            trace_id=trace_id,
            verifier=verifier
        )

        logger.info(
            f"INSIGHTMATE_SDK_INITIALIZED | Agent: {agent_id} | Trace: {trace_id}",
            extra={
                "user_id": user_id,
                "session_id": session_id,
                "lobe": "InsightMate"
            }
        )

        return {
            "planner": planner,
            "executor": executor,
            "state": state_manager,
            "session_id": session_id or f"ins_{trace_id}",
            "config": definition.model_dump()
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "lobe": "InsightMate",
            "registry_count": self.registry.count_agents(),
            "capabilities": ["transcription_analysis", "action_item_extraction", "executive_summary"]
        }

insight_sdk = InsightMateSDK()

__all__ = [
    "insight_sdk",
    "InsightPlanner",
    "InsightExecutor",
    "InsightStateManager",
    "InsightMateConstraints",
    "PolicyVerifier"
]