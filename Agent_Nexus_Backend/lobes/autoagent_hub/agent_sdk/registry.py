import threading
import importlib
from typing import Any, Dict, List, Optional, Type
from datetime import datetime
from pydantic import BaseModel, Field

from common.config.logging import logger
from common.schemas.errors import AppError, ErrorCategory

class AgentManifest(BaseModel):
    agent_id: str
    name: str
    version: str
    lobe: str
    description: str
    capabilities: List[str]
    config_schema: Dict[str, Any]
    class_path: str
    status: str = "AVAILABLE"
    last_registered: datetime = Field(default_factory=datetime.utcnow)

class HubAgentRegistry:
    _instance: Optional['HubAgentRegistry'] = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._agents: Dict[str, AgentManifest] = {}
            self._loaded_classes: Dict[str, Type[Any]] = {}
            self._registry_lock = threading.RLock()
            self._initialized = True

    async def register_agent(self, manifest: AgentManifest):
        with self._registry_lock:
            if manifest.agent_id in self._agents:
                logger.warning(f"REGISTRY_OVERWRITE | Agent: {manifest.agent_id} | Version: {manifest.version}")
            
            self._agents[manifest.agent_id] = manifest
            logger.info(f"REGISTRY_SUCCESS | Agent: {manifest.agent_id} | Lobe: {manifest.lobe}")

    async def get_agent(self, agent_id: str) -> Any:
        manifest = self._get_manifest(agent_id)
        
        if agent_id not in self._loaded_classes:
            self._load_agent_class(manifest)
            
        agent_class = self._loaded_classes[agent_id]
        return agent_class(manifest=manifest)

    async def list_available_agents(self, lobe: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._registry_lock:
            return [
                m.model_dump() for m in self._agents.values() 
                if not lobe or m.lobe == lobe
            ]

    def _get_manifest(self, agent_id: str) -> AgentManifest:
        with self._registry_lock:
            manifest = self._agents.get(agent_id)
            if not manifest:
                raise AppError(
                    category=ErrorCategory.NOT_FOUND,
                    error={"code": "AGENT_NOT_FOUND", "message": f"Agent {agent_id} not in registry"}
                )
            return manifest

    def _load_agent_class(self, manifest: AgentManifest):
        with self._registry_lock:
            if manifest.agent_id in self._loaded_classes:
                return

            try:
                module_path, class_name = manifest.class_path.rsplit(".", 1)
                module = importlib.import_module(module_path)
                agent_class = getattr(module, class_name)
                self._loaded_classes[manifest.agent_id] = agent_class
                logger.info(f"REGISTRY_CLASS_LOADED | Agent: {manifest.agent_id} | Path: {manifest.class_path}")
            except (ImportError, AttributeError) as e:
                logger.error(f"REGISTRY_LOAD_FAILURE | Agent: {manifest.agent_id} | Error: {str(e)}")
                raise AppError(
                    category=ErrorCategory.INTERNAL,
                    error={"code": "AGENT_LOAD_ERROR", "message": f"Could not load agent class: {str(e)}"}
                )

hub_agent_registry = HubAgentRegistry()