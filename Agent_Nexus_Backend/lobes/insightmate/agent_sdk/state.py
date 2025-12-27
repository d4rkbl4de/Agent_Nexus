import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from common.memory.short_term import ShortTermMemory
from common.config.logging_config import logger
from common.schemas.errors import AppError, ErrorCategory, ErrorCode

class AnalysisState(BaseModel):
    session_id: str
    agent_id: str
    transcript_hash: str
    current_step: str = "initialization"
    processed_chunks: int = 0
    total_chunks: int = 0
    extracted_entities: List[str] = Field(default_factory=list)
    interim_results: Dict[str, Any] = Field(default_factory=dict)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class InsightStateManager:
    def __init__(self, trace_id: str):
        self.trace_id = trace_id
        self.stm = ShortTermMemory(trace_id=trace_id, ttl=7200)
        self.state_key = f"insight_state_{trace_id}"

    async def initialize_state(self, session_id: str, agent_id: str, transcript_hash: str):
        state = AnalysisState(
            session_id=session_id,
            agent_id=agent_id,
            transcript_hash=transcript_hash
        )
        await self.save_state(state)

    async def get_state(self) -> AnalysisState:
        data = await self.stm.get(self.state_key)
        if not data:
            raise AppError(
                message="Insight analysis state not found or expired",
                category=ErrorCategory.NOT_FOUND_ERROR,
                code=ErrorCode.RESOURCE_NOT_FOUND,
                trace_id=self.trace_id
            )
        return AnalysisState(**data)

    async def save_state(self, state: AnalysisState):
        state.updated_at = datetime.utcnow()
        success = await self.stm.set(self.state_key, state.model_dump())
        if not success:
            logger.error(f"STATE_PERSISTENCE_FAILED | Trace: {self.trace_id}")
            raise AppError(
                message="Failed to persist InsightMate analysis state",
                category=ErrorCategory.INTERNAL_ERROR,
                code=ErrorCode.SYSTEM_PANIC,
                trace_id=self.trace_id
            )

    async def update_progress(self, step: str, chunks_completed: int, total_chunks: Optional[int] = None):
        state = await self.get_state()
        state.current_step = step
        state.processed_chunks = chunks_completed
        if total_chunks is not None:
            state.total_chunks = total_chunks
        await self.save_state(state)

    async def store_interim_result(self, key: str, value: Any):
        state = await self.get_state()
        state.interim_results[key] = value
        await self.save_state(state)

    async def append_entities(self, entities: List[str]):
        state = await self.get_state()
        unique_entities = list(set(state.extracted_entities + entities))
        state.extracted_entities = unique_entities
        await self.save_state(state)

    async def clear_session(self):
        await self.stm.delete(self.state_key)
        logger.info(f"STATE_CLEARED | Trace: {self.trace_id}", lobe="InsightMate")