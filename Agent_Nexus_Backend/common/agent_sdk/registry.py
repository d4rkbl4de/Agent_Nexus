import inspect
from typing import Dict, Type, Any, List
from common.config.logging import logger
from common.agent_sdk.base_agent import BaseAgent

class AgentRegistry:
    _instance = None
    _agents: Dict[str, Type[BaseAgent]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentRegistry, cls).__new__(cls)
        return cls._instance

    def register(self, agent_id: str):
        def wrapper(cls: Type[BaseAgent]):
            if not issubclass(cls, BaseAgent):
                raise TypeError(f"Class {cls.__name__} must inherit from BaseAgent")
            
            self._agents[agent_id.lower()] = cls
            logger.info(f"REGISTRY_BOND | Agent_ID: {agent_id} | Class: {cls.__name__}")
            return cls
        return wrapper

    def get_agent_class(self, agent_id: str) -> Type[BaseAgent]:
        agent_cls = self._agents.get(agent_id.lower())
        if not agent_cls:
            logger.error(f"REGISTRY_MISSING | Agent_ID: {agent_id}")
            raise ValueError(f"Agent '{agent_id}' is not registered in the Hive Mind.")
        return agent_cls

    def list_available_agents(self) -> List[str]:
        return list(self._agents.keys())

agent_registry = AgentRegistry()