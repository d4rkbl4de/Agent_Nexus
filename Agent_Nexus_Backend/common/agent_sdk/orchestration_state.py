from datetime import datetime, timezone
from typing import Any, Dict, List
from pydantic import BaseModel, Field

class OrchestrationState(BaseModel):
    request_id: str
    current_node: str
    visited_nodes: List[str] = Field(default_factory=list)
    shared_memory: Dict[str, Any] = Field(default_factory=dict)
    intermediate_results: Dict[str, Any] = Field(default_factory=dict)
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def transition(self, next_node: str) -> None:
        self.visited_nodes.append(self.current_node)
        self.current_node = next_node
        self.updated_at = datetime.now(timezone.utc)

    def save_result(self, key: str, value: Any) -> None:
        self.intermediate_results[key] = value
        self.updated_at = datetime.now(timezone.utc)