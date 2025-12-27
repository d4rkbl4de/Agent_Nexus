from typing import Dict, Any, List, Optional
from lobes.chatbuddy.agent_sdk.registry import registry
from lobes.chatbuddy.agent_sdk.state import AgentStateManager
from lobes.chatbuddy.agent_sdk.constraints import ChatBuddyConstraints
from lobes.chatbuddy.agent_sdk.core.conversational import ConversationalEngine
from lobes.chatbuddy.agent_sdk.core.memory import ChatMemoryFacade
from common.config.logging_config import logger
from common.schemas.errors import AppError, ErrorCategory, ErrorCode

class ChatBuddyLobe:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChatBuddyLobe, cls).__new__(cls)
            cls._instance.name = "ChatBuddy"
            cls._instance.registry = registry
            cls._instance._initialized = True
        return cls._instance

    async def start_session(self, agent_id: str, trace_id: str, user_id: str) -> Dict[str, Any]:
        definition = self.registry.get_agent(agent_id)
        
        state_manager = AgentStateManager(trace_id=trace_id)
        constraints = ChatBuddyConstraints(agent_id=agent_id, trace_id=trace_id)
        memory_facade = ChatMemoryFacade(trace_id=trace_id, user_id=user_id)
        
        engine = ConversationalEngine(
            definition=definition,
            state=state_manager,
            constraints=constraints,
            memory=memory_facade,
            trace_id=trace_id
        )

        logger.info(
            f"CHATBUDDY_SESSION_STARTED | Agent: {agent_id} | User: {user_id}",
            trace_id=trace_id,
            lobe=self.name
        )

        return {
            "engine": engine,
            "metadata": definition.metadata,
            "status": "ready"
        }

    async def get_health(self) -> Dict[str, Any]:
        return {
            "lobe": self.name,
            "status": "healthy",
            "available_agents": self.registry.list_agent_ids(),
            "version": "1.0.0"
        }

lobe = ChatBuddyLobe()

__all__ = [
    "lobe",
    "registry",
    "AgentStateManager",
    "ChatBuddyConstraints",
    "ConversationalEngine",
    "ChatMemoryFacade"
]