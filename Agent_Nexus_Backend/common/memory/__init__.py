from typing import Dict, Any, Optional
from common.memory.facade import MemoryFacade
from common.memory.short_term import ShortTermMemory
from common.memory.long_term import LongTermMemory
from common.memory.episodic import EpisodicMemory
from common.memory.semantic import SemanticMemory
from common.memory.compressor import MemoryCompressor

class MemorySystem:
    _instance: Optional['MemorySystem'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MemorySystem, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._facade_cache: Dict[str, MemoryFacade] = {}
        self.compressor = MemoryCompressor()
        self._initialized = True

    def get_facade(self, trace_id: str, agent_id: str) -> MemoryFacade:
        cache_key = f"{agent_id}:{trace_id}"
        if cache_key not in self._facade_cache:
            self._facade_cache[cache_key] = MemoryFacade(
                trace_id=trace_id,
                agent_id=agent_id,
                short_term=ShortTermMemory(trace_id),
                long_term=LongTermMemory(agent_id),
                episodic=EpisodicMemory(trace_id),
                semantic=SemanticMemory(),
                compressor=self.compressor
            )
        return self._facade_cache[cache_key]

    async def clear_trace_context(self, trace_id: str, agent_id: str):
        cache_key = f"{agent_id}:{trace_id}"
        if cache_key in self._facade_cache:
            facade = self._facade_cache.pop(cache_key)
            await facade.short_term.clear()

memory_system = MemorySystem()

__all__ = [
    "MemoryFacade",
    "ShortTermMemory",
    "LongTermMemory",
    "EpisodicMemory",
    "SemanticMemory",
    "MemoryCompressor",
    "memory_system"
]