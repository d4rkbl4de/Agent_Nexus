import inspect
from typing import Dict, Any, Callable, Optional, Type
from pydantic import BaseModel
from common.config.logging import logger
from common.ai_sdk.exceptions import ConfigurationException

class ToolMetadata(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
    plugin_id: str

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._metadata: Dict[str, ToolMetadata] = {}

    def register_tool(
        self, 
        name: str, 
        func: Callable, 
        description: str, 
        plugin_id: str = "core"
    ):
        if name in self._tools:
            logger.warning(f"TOOL_REGISTRY_OVERWRITE | Name: {name} | Plugin: {plugin_id}")
            
        # Extract JSON Schema-style parameters from function signature
        sig = inspect.signature(func)
        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue
            
            param_type = "string"
            if param.annotation == int:
                param_type = "integer"
            elif param.annotation == bool:
                param_type = "boolean"
            elif param.annotation == dict:
                param_type = "object"

            parameters["properties"][param_name] = {
                "type": param_type,
                "description": f"Input for {param_name}"
            }
            
            if param.default is inspect.Parameter.empty:
                parameters["required"].append(param_name)

        self._tools[name] = func
        self._metadata[name] = ToolMetadata(
            name=name,
            description=description,
            parameters=parameters,
            plugin_id=plugin_id
        )
        
        logger.info(f"TOOL_REGISTERED | Name: {name} | Plugin: {plugin_id}")

    def get_tool(self, name: str) -> Optional[Callable]:
        return self._tools.get(name)

    def get_all_metadata(self) -> List[Dict[str, Any]]:
        return [m.dict() for m in self._metadata.values()]

    def get_tool_definition_for_llm(self, name: str) -> Dict[str, Any]:
        meta = self._metadata.get(name)
        if not meta:
            raise ConfigurationException(f"Tool {name} not found in registry.")
        
        return {
            "type": "function",
            "function": {
                "name": meta.name,
                "description": meta.description,
                "parameters": meta.parameters
            }
        }