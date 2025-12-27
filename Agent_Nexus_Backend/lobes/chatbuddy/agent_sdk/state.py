import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from common.config.logging_config import logger
from common.memory.short_term import ShortTermMemory
from common.schemas.errors import AppError, ErrorCategory, ErrorCode

class ChatState(BaseModel):
    thread_id: str
    agent_id: str
    user_id: str
    last_interaction: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    active_tokens: int = 0

class AgentStateManager:
    def __init__(self, trace_id: str):
        self.trace_id = trace_id
        self.stm = ShortTermMemory(trace_id=trace_id, ttl=3600)

    async def get_context_window(self, limit: int = 20) -> List[Dict[str, Any]]:
        try:
            history = await self.stm.get_recent(limit=limit)
            return [item["data"] for item in history]
        except Exception as e:
            logger.error(
                f"STATE_RETRIEVAL_FAILURE | Trace: {self.trace_id}",
                trace_id=self.trace_id,
                extra={"error": str(e)}
            )
            return []

    async def save_interaction(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        payload = {
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.stm.append(payload)
        
        logger.info(
            f"STATE_UPDATED | Role: {role}",
            trace_id=self.trace_id,
            lobe="ChatBuddy",
            extra={"content_length": len(content)}
        )

    async def snapshot_state(self, chat_state: ChatState) -> bool:
        try:
            snapshot = {
                "type": "state_snapshot",
                "data": chat_state.model_dump(),
                "timestamp": datetime.utcnow().isoformat()
            }
            await self.stm.append(snapshot)
            return True
        except Exception as e:
            logger.error(f"STATE_SNAPSHOT_FAILURE | Trace: {self.trace_id} | Error: {str(e)}")
            return False

    async def clear_session(self):
        success = await self.stm.clear()
        if not success:
            raise AppError(
                message="Failed to clear chat session state",
                category=ErrorCategory.INTERNAL_ERROR,
                code=ErrorCode.SYSTEM_PANIC,
                trace_id=self.trace_id
            )

    def calculate_token_usage(self, history: List[Dict[str, Any]]) -> int:
        return sum(len(str(m.get("content", ""))) // 4 for m in history)