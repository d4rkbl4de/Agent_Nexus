from common.agent_sdk.base_agent import BaseAgent
from common.agent_sdk.registry import agent_registry
from common.agent_sdk.lifecycle import AgentLifecycle
from common.agent_sdk.orchestration_state import OrchestrationState
from common.agent_sdk.planner import AgentPlanner
from common.agent_sdk.executor import AgentExecutor
from common.agent_sdk.verifier import AgentVerifier
from common.agent_sdk.delegation import DelegationManager

class AgentSDK:
    def __init__(self):
        self.registry = agent_registry
        self.lifecycle = AgentLifecycle()
        self.delegation = DelegationManager()

    async def spawn_agent(self, agent_id: str, trace_id: str) -> BaseAgent:
        agent_cls = self.registry.get_agent_class(agent_id)
        state = OrchestrationState(trace_id=trace_id, agent_id=agent_id)
        
        agent_instance = agent_cls(
            state=state,
            planner=AgentPlanner(),
            executor=AgentExecutor(),
            verifier=AgentVerifier()
        )
        
        await self.lifecycle.on_spawn(agent_instance)
        return agent_instance

agent_sdk = AgentSDK()

__all__ = [
    "agent_sdk",
    "BaseAgent",
    "agent_registry",
    "AgentLifecycle",
    "OrchestrationState",
    "AgentPlanner",
    "AgentExecutor",
    "AgentVerifier",
    "DelegationManager"
]