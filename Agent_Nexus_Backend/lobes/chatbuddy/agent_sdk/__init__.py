from typing import Dict, Any, Optional
from lobes.chatbuddy.agent_sdk.registry import registry
from lobes.chatbuddy.agent_sdk.state import AgentStateManager
from lobes.chatbuddy.agent_sdk.constraints import ChatBuddyConstraints
from lobes.chatbuddy.agent_sdk.core.conversational import ConversationalEngine
from lobes.chatbuddy.agent_sdk.core.memory import ChatMemoryFacade
from common.schemas.errors import AppError, ErrorCategory, ErrorCode
from common.config.logging_config import logger

class ChatBuddySDK:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChatBuddySDK, cls).__new__(cls)
            cls._instance.registry = registry
            cls._instance._initialized = True
        return cls._instance

    async def create_engine(
        self, 
        agent_id: str, 
        trace_id: str, 
        user_id: str,
        session_id: Optional[str] = None
    ) -> ConversationalEngine:
        definition = self.registry.get_agent(agent_id)
        
        constraints = ChatBuddyConstraints(agent_id=agent_id, trace_id=trace_id)
        state_manager = AgentStateManager(trace_id=trace_id)
        memory_facade = ChatMemoryFacade(trace_id=trace_id, user_id=user_id)
        
        engine = ConversationalEngine(
            definition=definition,
            state=state_manager,
            constraints=constraints,
            memory=memory_facade,
            trace_id=trace_id,
            session_id=session_id or f"chat_{trace_id}"
        )

        logger.info(
            f"CHATBUDDY_ENGINE_INITIALIZED | Agent: {agent_id} | Trace: {trace_id}",
            extra={
                "agent_name": definition.name,
                "user_id": user_id,
                "lobe": "ChatBuddy"
            }
        )
        
        return engine

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "lobe": "ChatBuddy",
            "available_agents": self.registry.list_agent_ids(),
            "supported_features": ["streaming", "short_term_memory", "personal_context"],
            "constraints_enabled": True
        }

chat_sdk = ChatBuddySDK()

__all__ = [
    "chat_sdk",
    "ConversationalEngine",
    "ChatMemoryFacade",
    "AgentStateManager",
    "ChatBuddyConstraints",
    "registry"
]