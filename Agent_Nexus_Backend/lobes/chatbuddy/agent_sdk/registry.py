from typing import Dict, Any, List, Optional, Type
from pydantic import BaseModel, Field
from common.schemas.errors import AppError, ErrorCategory, ErrorCode

class ChatBuddyDefinition(BaseModel):
    agent_id: str
    name: str
    version: str
    system_prompt: str
    temperature: float = 0.7
    max_tokens: int = 1000
    model_override: Optional[str] = None
    tools_enabled: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ChatBuddyRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChatBuddyRegistry, cls).__new__(cls)
            cls._instance._agents: Dict[str, ChatBuddyDefinition] = {}
            cls._instance._load_default_agents()
        return cls._instance

    def _load_default_agents(self):
        default_buddy = ChatBuddyDefinition(
            agent_id="cb-standard-01",
            name="ChatBuddy Prime",
            version="1.0.0",
            system_prompt="You are ChatBuddy+, a helpful and concise personal AI assistant. "
                          "Focus on providing clear, direct answers and helpful insights.",
            tools_enabled=["web_search", "memory_query"],
            metadata={"personality": "empathetic", "role": "generalist"}
        )
        self.register_agent(default_buddy)

    def register_agent(self, definition: ChatBuddyDefinition):
        if definition.agent_id in self._agents:
            raise AppError(
                message=f"Agent {definition.agent_id} already exists in ChatBuddy Registry",
                category=ErrorCategory.INTERNAL_ERROR,
                code=ErrorCode.SYSTEM_PANIC,
                status_code=409
            )
        self._agents[definition.agent_id] = definition

    def get_agent(self, agent_id: str) -> ChatBuddyDefinition:
        agent = self._agents.get(agent_id)
        if not agent:
            raise AppError(
                message=f"ChatBuddy agent {agent_id} not found",
                category=ErrorCategory.NOT_FOUND_ERROR,
                code=ErrorCode.RESOURCE_NOT_FOUND,
                status_code=404
            )
        return agent

    def list_agents(self) -> List[ChatBuddyDefinition]:
        return list(self._agents.values())

    def list_agent_ids(self) -> List[str]:
        return list(self._agents.keys())

    def update_agent(self, agent_id: str, updates: Dict[str, Any]):
        if agent_id not in self._agents:
            raise AppError(
                message=f"Cannot update non-existent agent {agent_id}",
                category=ErrorCategory.NOT_FOUND_ERROR,
                code=ErrorCode.RESOURCE_NOT_FOUND
            )
        current_data = self._agents[agent_id].model_dump()
        current_data.update(updates)
        self._agents[agent_id] = ChatBuddyDefinition(**current_data)

registry = ChatBuddyRegistry()