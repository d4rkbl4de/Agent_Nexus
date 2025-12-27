import enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from common.schemas.errors import AppError, ErrorCategory

class ToolCategory(str, enum.Enum):
    MEMORY = "MEMORY"
    COMMUNICATION = "COMMUNICATION"
    COMPUTATION = "COMPUTATION"
    WEB_RESEARCH = "WEB_RESEARCH"
    FILESYSTEM = "FILESYSTEM"

class ToolParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None

class ToolDefinition(BaseModel):
    name: str
    category: ToolCategory
    description: str
    parameters: List[ToolParameter]
    cost_per_use: float = 0.0
    requires_approval: bool = False
    timeout_sec: int = 30

class ToolManifestRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._initialize_core_manifest()

    def _initialize_core_manifest(self):
        core_tools = [
            ToolDefinition(
                name="episodic_search",
                category=ToolCategory.MEMORY,
                description="Search long-term memory for specific historical agent turns",
                parameters=[
                    ToolParameter(name="query", type="string", description="Semantic search query"),
                    ToolParameter(name="limit", type="integer", description="Max results", required=False, default=5)
                ],
                cost_per_use=0.005
            ),
            ToolDefinition(
                name="slack_notify",
                category=ToolCategory.COMMUNICATION,
                description="Send urgent status updates to the primary user channel",
                parameters=[
                    ToolParameter(name="message", type="string", description="Notification body"),
                    ToolParameter(name="priority", type="string", description="low/high")
                ],
                requires_approval=True
            ),
            ToolDefinition(
                name="python_interpreter",
                category=ToolCategory.COMPUTATION,
                description="Execute sandboxed Python code for data analysis",
                parameters=[
                    ToolParameter(name="code", type="string", description="Python script to execute")
                ],
                timeout_sec=60,
                requires_approval=True
            )
        ]
        for tool in core_tools:
            self.register_tool(tool)

    def register_tool(self, tool: ToolDefinition):
        if tool.name in self._tools:
            raise AppError(
                message=f"Tool {tool.name} already exists in manifest",
                category=ErrorCategory.INTERNAL_ERROR,
                status_code=409
            )
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> ToolDefinition:
        tool = self._tools.get(name)
        if not tool:
            raise AppError(
                message=f"Tool {name} not found in manifest",
                category=ErrorCategory.NOT_FOUND,
                status_code=404
            )
        return tool

    def list_tools(self, category: Optional[ToolCategory] = None) -> List[ToolDefinition]:
        if category:
            return [t for t in self._tools.values() if t.category == category]
        return list(self._tools.values())

tool_registry = ToolManifestRegistry()