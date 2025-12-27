import asyncio
from typing import Any, List, Dict, Optional
from common.memory.short_term import ShortTermMemory
from common.memory.long_term import LongTermMemory
from common.memory.episodic import EpisodicMemory
from common.memory.semantic import SemanticMemory
from common.memory.compressor import MemoryCompressor
from common.config.logging import logger
from common.schemas.errors import AppError, ErrorCategory

class MemoryFacade:
    def __init__(
        self,
        trace_id: str,
        agent_id: str,
        short_term: ShortTermMemory,
        long_term: LongTermMemory,
        episodic: EpisodicMemory,
        semantic: SemanticMemory,
        compressor: MemoryCompressor
    ):
        self.trace_id = trace_id
        self.agent_id = agent_id
        self.short_term = short_term
        self.long_term = long_term
        self.episodic = episodic
        self.semantic = semantic
        self.compressor = compressor

    async def recall(self, query: str, context_window: int = 5) -> str:
        try:
            results = await asyncio.gather(
                self.short_term.get_recent(limit=10),
                self.long_term.search(query, limit=context_window),
                self.episodic.get_high_importance_events(threshold=0.8),
                self.semantic.query(query)
            )
            
            short_data, long_data, episodic_data, semantic_data = results

            return await self.compressor.synthesize(
                short=short_data,
                long=long_data,
                semantic=semantic_data,
                trace_id=self.trace_id
            )
        except Exception as e:
            logger.error(f"MEMORY_FACADE_RECALL_ERROR | Trace: {self.trace_id} | {str(e)}")
            return ""

    async def commit(self, content: Any, importance: Optional[float] = None):
        if importance is None:
            importance = self.compressor.calculate_importance(str(content))

        commit_tasks = [self.short_term.append(content)]

        if importance >= 0.7:
            commit_tasks.append(
                self.episodic.capture_milestone(
                    content=content,
                    importance=importance,
                    metadata={"agent_id": self.agent_id}
                )
            )

        if importance >= 0.9:
            commit_tasks.append(
                self.long_term.store(
                    content=content,
                    metadata={"trace_id": self.trace_id, "importance": importance}
                )
            )

        await asyncio.gather(*commit_tasks)

    async def get_working_context(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "agent_id": self.agent_id,
            "recent_history": await self.short_term.get_recent(limit=5),
            "milestones": await self.episodic.get_event_stream(limit=3)
        }

    async def wipe_short_term(self):
        await self.short_term.clear()