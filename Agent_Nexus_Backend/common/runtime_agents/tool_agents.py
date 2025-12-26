import logging
from typing import Dict, Any, Optional
import asyncio
import json
from common.runtime_agents.registry import ToolRegistry
from common.runtime_agents.permissions import PermissionEngine, PermissionLevel
from common.ai_sdk.exceptions import PolicyViolationException, ConfigurationException
from tracing.context import get_trace_id

logger = logging.getLogger(__name__)

class ToolExecutorAgent:
    def __init__(self, registry: ToolRegistry, permissions: PermissionEngine):
        self.registry = registry
        self.permissions = permissions

    async def execute_tool(
        self,
        agent_id: str,
        tool_name: str,
        tool_input: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        trace_id = get_trace_id() or "system_internal"
        
        logger.info(
            f"TOOL_EXECUTION_START | Trace: {trace_id} | Agent: {agent_id} | "
            f"Tool: {tool_name} | Input: {json.dumps(tool_input)}"
        )

        try:
            self.permissions.validate_action(
                agent_id=agent_id, 
                tool_name=tool_name, 
                required_level=PermissionLevel.EXECUTE
            )

            tool_func = self.registry.get_tool(tool_name)
            if not tool_func:
                raise ConfigurationException(f"Tool {tool_name} not found in registry.")

            if asyncio.iscoroutinefunction(tool_func):
                result = await tool_func(**tool_input)
            else:
                result = tool_func(**tool_input)

            logger.info(f"TOOL_EXECUTION_SUCCESS | Trace: {trace_id} | Tool: {tool_name}")
            
            return {
                "status": "success",
                "tool": tool_name,
                "output": result,
                "trace_id": trace_id
            }

        except PolicyViolationException as pve:
            logger.warning(f"TOOL_EXECUTION_BLOCKED | Trace: {trace_id} | Reason: {str(pve)}")
            return {
                "status": "denied",
                "error": str(pve),
                "trace_id": trace_id
            }
        except Exception as e:
            logger.error(f"TOOL_EXECUTION_FAILED | Trace: {trace_id} | Error: {str(e)}")
            return {
                "status": "error",
                "error": "Internal execution failure",
                "details": str(e),
                "trace_id": trace_id
            }