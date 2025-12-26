import enum
from typing import Dict, List, Optional, Set, Any
from pydantic import BaseModel, Field
from common.config.logging import logger
from common.ai_sdk.exceptions import PolicyViolationException

class PermissionLevel(enum.IntEnum):
    DENY = 0
    READ = 1
    WRITE = 2
    EXECUTE = 3
    ADMIN = 4

class ToolPermission(BaseModel):
    tool_name: str
    level: PermissionLevel
    constraints: Dict[str, Any] = Field(default_factory=dict)

class AgentPermissions(BaseModel):
    agent_id: str
    allowed_tools: Dict[str, ToolPermission] = Field(default_factory=dict)
    max_tokens_per_turn: int = 4096
    allow_external_internet: bool = False

class PermissionEngine:
    def __init__(self):
        self._registry: Dict[str, AgentPermissions] = {}
        self._load_default_policies()

    def _load_default_policies(self):
        self.register_policy(
            AgentPermissions(
                agent_id="insight_mate",
                allowed_tools={
                    "vector_search": ToolPermission(tool_name="vector_search", level=PermissionLevel.READ),
                    "postgres_query": ToolPermission(tool_name="postgres_query", level=PermissionLevel.READ),
                    "email_notifier": ToolPermission(tool_name="email_notifier", level=PermissionLevel.EXECUTE)
                },
                allow_external_internet=False
            )
        )

    def register_policy(self, policy: AgentPermissions):
        self._registry[policy.agent_id] = policy

    def validate_action(
        self, 
        agent_id: str, 
        tool_name: str, 
        required_level: PermissionLevel = PermissionLevel.EXECUTE
    ) -> bool:
        policy = self._registry.get(agent_id)
        
        if not policy:
            logger.error(f"PERMISSION_DENIED | Agent: {agent_id} | Reason: No Policy Defined")
            raise PolicyViolationException(f"Agent {agent_id} has no registered permissions.", "NO_POLICY")

        tool_perm = policy.allowed_tools.get(tool_name)
        
        if not tool_perm or tool_perm.level < required_level:
            logger.error(f"PERMISSION_DENIED | Agent: {agent_id} | Tool: {tool_name} | Required: {required_level.name}")
            raise PolicyViolationException(
                f"Agent {agent_id} is not authorized to {required_level.name} tool: {tool_name}", 
                "INSUFFICIENT_PERMISSIONS"
            )

        return True

    def check_token_budget(self, agent_id: str, used_tokens: int):
        policy = self._registry.get(agent_id)
        if policy and used_tokens > policy.max_tokens_per_turn:
             raise PolicyViolationException("Token budget exceeded for current turn.", "BUDGET_EXCEEDED")