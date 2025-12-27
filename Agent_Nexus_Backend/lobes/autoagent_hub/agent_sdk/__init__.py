from typing import Dict, Any, Optional, Type
from lobes.autoagent_hub.agent_sdk.core.coordinator import AgentCoordinator
from lobes.autoagent_hub.agent_sdk.core.delegator import TaskDelegator
from lobes.autoagent_hub.agent_sdk.core.verifier import PolicyVerifier
from lobes.autoagent_hub.agent_sdk.state import AgentStateManager
from lobes.autoagent_hub.agent_sdk.constraints import AgentConstraints
from lobes.autoagent_hub.agent_sdk.registry import AgentRegistry
from common.config.logging_config import logger
from common.schemas.errors import AppError, ErrorCategory, ErrorCode

class AutoAgentSDK:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AutoAgentSDK, cls).__new__(cls)
            cls._instance.registry = AgentRegistry()
            cls._instance.state_manager = AgentStateManager()
            cls._instance._initialized = True
        return cls._instance

    async def initialize_session(self, agent_id: str, trace_id: str) -> Dict[str, Any]:
        agent_def = self.registry.get_agent_definition(agent_id)
        if not agent_def:
            raise AppError(
                message=f"Agent {agent_id} not found in AutoAgent Hub registry",
                category=ErrorCategory.NOT_FOUND_ERROR,
                code=ErrorCode.RESOURCE_NOT_FOUND,
                trace_id=trace_id
            )
            
        constraints = AgentConstraints(agent_id=agent_id, trace_id=trace_id)
        verifier = PolicyVerifier(constraints=constraints)
        
        coordinator = AgentCoordinator(
            agent_id=agent_id,
            trace_id=trace_id,
            definition=agent_def,
            state_manager=self.state_manager,
            verifier=verifier,
            delegator=TaskDelegator(trace_id=trace_id)
        )
        
        return {
            "coordinator": coordinator,
            "session_id": f"sess_{trace_id}",
            "metadata": agent_def.metadata
        }

    def get_heartbeat(self) -> Dict[str, Any]:
        return {
            "status": "active",
            "lobe": "AutoAgent_Hub",
            "registered_agents": self.registry.list_agent_ids(),
            "active_sessions": self.state_manager.count_active_sessions()
        }

hub_sdk = AutoAgentSDK()

__all__ = [
    "hub_sdk",
    "AgentCoordinator",
    "TaskDelegator",
    "PolicyVerifier",
    "AgentStateManager",
    "AgentConstraints",
    "AgentRegistry"
]