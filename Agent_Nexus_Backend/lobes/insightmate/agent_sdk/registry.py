from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from common.schemas.errors import AppError, ErrorCategory, ErrorCode

class InsightAgentDefinition(BaseModel):
    agent_id: str
    name: str
    version: str
    system_prompt: str
    analysis_depth: str = "standard"
    supported_tasks: List[str] = Field(default_factory=list)
    max_context_window: int = 128000
    temperature: float = 0.1
    metadata: Dict[str, Any] = Field(default_factory=dict)

class InsightRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InsightRegistry, cls).__new__(cls)
            cls._instance._agents: Dict[str, InsightAgentDefinition] = {}
            cls._instance._load_default_definitions()
        return cls._instance

    def _load_default_definitions(self):
        corporate_summarizer = InsightAgentDefinition(
            agent_id="im-corp-sum-01",
            name="Corporate Insight Pro",
            version="1.1.0",
            system_prompt="You are an expert corporate secretary and strategic analyst. "
                          "Your goal is to extract high-leverage insights and concrete action items "
                          "from meeting transcripts with extreme precision.",
            analysis_depth="high",
            supported_tasks=["generate_meeting_summary", "extract_action_items", "detect_sentiment_trends"],
            metadata={"industry": "general_corporate", "optimization": "accuracy"}
        )
        self.register_agent(corporate_summarizer)

    def register_agent(self, definition: InsightAgentDefinition):
        if definition.agent_id in self._agents:
            raise AppError(
                message=f"Insight Agent {definition.agent_id} is already registered",
                category=ErrorCategory.INTERNAL_ERROR,
                code=ErrorCode.SYSTEM_PANIC,
                status_code=409
            )
        self._agents[definition.agent_id] = definition

    def get_definition(self, agent_id: str) -> InsightAgentDefinition:
        definition = self._agents.get(agent_id)
        if not definition:
            raise AppError(
                message=f"Insight Agent {agent_id} not found in InsightMate registry",
                category=ErrorCategory.NOT_FOUND_ERROR,
                code=ErrorCode.RESOURCE_NOT_FOUND,
                status_code=404
            )
        return definition

    def list_agents(self) -> List[InsightAgentDefinition]:
        return list(self._agents.values())

    def list_agent_ids(self) -> List[str]:
        return list(self._agents.keys())

    def count_agents(self) -> int:
        return len(self._agents)

    def remove_agent(self, agent_id: str):
        if agent_id in self._agents:
            del self._agents[agent_id]

insight_registry = InsightRegistry()