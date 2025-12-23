from typing import List
from .history_model import MemoryRecord
from .redis_backend import RedisMemoryBackend
from .db_backend import DBMemoryBackend


class MemoryManager:
    def __init__(
        self,
        short_term: RedisMemoryBackend,
        long_term: DBMemoryBackend,
        short_term_limit: int = 20,
        short_term_ttl: int = 3600,
    ):
        self.short_term = short_term
        self.long_term = long_term
        self.short_term_limit = short_term_limit
        self.short_term_ttl = short_term_ttl

    def write(self, record: MemoryRecord) -> None:
        self.short_term.append(record, ttl=self.short_term_ttl)
        self.long_term.add(record)

    def recall(
        self,
        agent_id: str,
        short_term: bool = True,
        long_term: bool = True,
        limit: int | None = None,
    ) -> List[MemoryRecord]:
        memories = []
        if short_term:
            memories.extend(
                self.short_term.fetch(
                    agent_id,
                    limit=min(limit or self.short_term_limit, self.short_term_limit),
                )
            )
        if long_term:
            memories.extend(self.long_term.fetch(agent_id, limit=limit))
        memories.sort(key=lambda m: m.timestamp)
        return memories

    def wipe(self, agent_id: str) -> None:
        self.short_term.clear(agent_id)
        self.long_term.clear(agent_id)
