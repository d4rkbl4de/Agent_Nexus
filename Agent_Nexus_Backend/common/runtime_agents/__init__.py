from common.runtime_agents.registry import ToolRegistry, ToolMetadata
from common.runtime_agents.permissions import (
    PermissionEngine,
    AgentPermissions,
    ToolPermission,
    PermissionLevel
)
from common.runtime_agents.tool_agents import ToolExecutorAgent

__all__ = [
    "ToolRegistry",
    "ToolMetadata",
    "PermissionEngine",
    "AgentPermissions",
    "ToolPermission",
    "PermissionLevel",
    "ToolExecutorAgent"
]

_default_registry = ToolRegistry()
_default_permissions = PermissionEngine()
_default_executor = ToolExecutorAgent(_default_registry, _default_permissions)

def get_runtime_executor() -> ToolExecutorAgent:
    return _default_executor

def get_runtime_registry() -> ToolRegistry:
    return _default_registry

def get_runtime_permissions() -> PermissionEngine:
    return _default_permissions